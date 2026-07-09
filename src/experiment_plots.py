"""Generazione dei sei grafici della campagna sperimentale (Compito 4)."""
import os

# Imposta il backend headless di matplotlib prima di importare pyplot per ambienti senza display
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from src.plot_style import apply_style, COLOR_DEBOLE, COLOR_FORTE, COLOR_ANDATA, COLOR_RITORNO, COLOR_TIMEOUT

apply_style()


def _estrai_campioni(
    scaling_res: list[dict[str, object]],
    density_res: list[dict[str, object]],
    pruning_res: list[dict[str, object]],
    ordering_res: list[dict[str, object]]
) -> tuple[list, list, list, list, list]:
    """
    Raccoglie in modo centralizzato i campioni sperimentali usati dagli scatter plot 4 e 5,
    escludendo le coppie banali (O=D o risolte senza alcuna ricorsione: non appartengono
    alla crescita di complessità e si accumulerebbero rumorosamente a x=1) e i timeout
    completi (falserebbero le pendenze ideali).

    Returns:
        Tupla di cinque liste parallele: celle di frontiera, tempo, numero di landmark,
        chiamate ricorsive, lunghezza del cammino.
    """
    frontier_cells_list: list[float] = []
    elapsed_time_list: list[float] = []
    landmarks_count_list: list[float] = []
    recursive_calls_list: list[float] = []
    path_length_list: list[float] = []

    def add_sample(metric_dict):
        if metric_dict and metric_dict.get('elapsed_time_s') is not None:
            if metric_dict.get('frontier_cells', 0) < 1 or metric_dict.get('recursive_calls', 0) <= 1:
                return
            if metric_dict.get('timed_out', False):
                return
            frontier_cells_list.append(metric_dict.get('frontier_cells', 0))
            elapsed_time_list.append(max(1e-6, metric_dict.get('elapsed_time_s', 0)))
            landmarks_count_list.append(max(1, metric_dict.get('landmarks_count', 1)))
            recursive_calls_list.append(metric_dict.get('recursive_calls', 0))
            path_length_list.append(max(1.0, metric_dict.get('path_length', 1.0)))

    # Estraiamo da scaling (singole esecuzioni, andata e ritorno)
    for r in scaling_res:
        add_sample(r.get("weak"))
        add_sample(r.get("strong"))
        add_sample(r.get("ritorno"))
    # Estraiamo da density (tutte le coppie, andata e ritorno)
    for r in density_res:
        for c in r.get("coppie", []):
            add_sample(c.get("andata"))
            add_sample(c.get("ritorno"))
    # Estraiamo da pruning (campioni con potatura debole e coppie con potatura forte)
    for r in pruning_res:
        for s in r.get("campioni_weak", []):
            add_sample(s)
        for c in r.get("coppie_strong", []):
            add_sample(c.get("andata"))
            add_sample(c.get("ritorno"))
    # Estraiamo da ordering (solo i campioni con ordinamento casuale: quelli
    # con ordinamento euristico coincidono con le coppie della potatura forte)
    for r in ordering_res:
        for s in r.get("campioni_random", []):
            add_sample(s)

    return frontier_cells_list, elapsed_time_list, landmarks_count_list, recursive_calls_list, path_length_list


def _plot_time_vs_density(density_res: list[dict[str, object]], output_dir: str) -> None:
    """Plot 1: tempo di esecuzione in funzione della densità di ostacoli (transizione di fase),
    per taglia di griglia. "timed_out" indica che almeno una delle coppie campionate (mediana
    su coppia d'angolo più quattro casuali) non ha completato entro il tempo limite: il tempo
    mostrato per quei punti non è quindi un tempo di completamento pieno."""
    density_timeout_val = 20.0
    min_densita = min(r["density"] for r in density_res)
    plt.figure(figsize=(8, 5))
    colori_taglia = {50: '#e056fd', 100: '#0984e3'}
    taglie_presenti = sorted({r.get("size", 50) for r in density_res})
    for taglia in taglie_presenti:
        campioni_taglia = [r for r in density_res if r.get("size", 50) == taglia]
        dens = [r["density"] for r in campioni_taglia]
        times = [r["metrics"]["elapsed_time_s"] for r in campioni_taglia]
        timed_out = [r["metrics"]["timed_out"] for r in campioni_taglia]
        colore = colori_taglia.get(taglia, '#e056fd')
        plt.plot(dens, times, color=colore, linewidth=2.5, alpha=0.55, zorder=1)
        ok_pts = [(x, y) for x, y, t in zip(dens, times, timed_out) if not t]
        to_pts = [(x, y) for x, y, t in zip(dens, times, timed_out) if t]
        if ok_pts:
            xs, ys = zip(*ok_pts)
            plt.scatter(xs, ys, marker='o', s=80, color=colore, edgecolors='black',
                        linewidths=0.8, zorder=3, label=f'Griglia {taglia}x{taglia} (potatura forte)')
        if to_pts:
            xs, ys = zip(*to_pts)
            plt.scatter(xs, ys, marker='x', s=110, color=colore, linewidths=2.5, zorder=3)
    plt.axhline(density_timeout_val, color='#636e72', linestyle=':', linewidth=1.5, zorder=0)
    plt.text(min_densita, density_timeout_val, " tempo limite raggiunto", fontsize=8.5,
             color='#636e72', va='bottom', ha='left')
    plt.scatter([], [], marker='x', s=110, color='#636e72', linewidths=2.5,
                label='Tempo limite raggiunto (su almeno una delle coppie campionate)')
    plt.title("Tempo di esecuzione in funzione della densità di ostacoli (transizione di fase)", fontsize=12, fontweight='bold')
    plt.xlabel("Densità ostacoli", fontsize=10)
    plt.ylabel("Tempo di esecuzione (secondi)", fontsize=10)
    plt.yscale('log')
    plt.grid(True, which="both", linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "1_time_vs_density.png"), dpi=200)
    plt.close()


def _plot_pruning_comparison(
    pruning_res: list[dict[str, object]],
    ordering_res: list[dict[str, object]],
    output_dir: str
) -> None:
    """Plot 2: confronto a barre delle tre configurazioni realmente distinte (potatura
    debole/forte, ordinamento euristico/casuale) per tipologia di ostacolo. Non esiste una
    quarta barra isolata per il solo ordinamento euristico, perché nella campagna coincide
    sempre con la misura della potatura forte."""
    categories = [r["obstacle_type"] for r in pruning_res]
    weak_times = [r["weak"]["elapsed_time_s"] for r in pruning_res]
    strong_times = [r["strong"]["elapsed_time_s"] for r in pruning_res]

    random_times = []
    for cat in categories:
        match = next((r for r in ordering_res if r["obstacle_type"] == cat), None)
        random_times.append(match["random"]["elapsed_time_s"] if match else 0.0)

    x = np.arange(len(categories))
    width = 0.25
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width, weak_times, width, label='Potatura debole + ordinamento euristico', color='#ff7979')
    ax.bar(x, strong_times, width, label='Potatura forte + ordinamento euristico', color='#2ed573')
    ax.bar(x + width, random_times, width, label='Potatura forte + ordinamento casuale', color='#a29bfe')

    ax.set_title("Tempi di esecuzione delle diverse configurazioni per scenario", fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.set_ylabel("Tempo di esecuzione (secondi)")
    ax.set_yscale('log')
    ax.grid(True, which="both", linestyle='--', alpha=0.4)
    ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.2), ncol=2)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "2_pruning_comparison_boxplot.png"), dpi=200, bbox_inches='tight')
    plt.close()


def _plot_scaling(scaling_res: list[dict[str, object]], output_dir: str) -> None:
    """Plot 3: crescita temporale asintotica in scala bilogaritmica. I punti in cui il tempo
    limite è stato raggiunto non sono tempi di completamento reali: si distinguono con una
    "x" e non vanno confusi con un plateau asintotico."""
    plt.figure(figsize=(8, 5))
    sizes = [r["size"] for r in scaling_res]
    scaling_timeout_val = max(r["weak"]["elapsed_time_s"] for r in scaling_res)
    for key, label, color, marker in [
        ("weak", "Potatura debole (riga 16)", COLOR_DEBOLE, "s"),
        ("strong", "Potatura forte (riga 17)", COLOR_FORTE, "^"),
    ]:
        times = [r[key]["elapsed_time_s"] for r in scaling_res]
        timed_out = [r[key]["timed_out"] for r in scaling_res]
        plt.plot(sizes, times, color=color, linewidth=2, alpha=0.55, zorder=1)
        ok_pts = [(s, v) for s, v, to in zip(sizes, times, timed_out) if not to]
        to_pts = [(s, v) for s, v, to in zip(sizes, times, timed_out) if to]
        if ok_pts:
            xs, ys = zip(*ok_pts)
            plt.scatter(xs, ys, marker=marker, s=100, color=color,
                        edgecolors='black', linewidths=0.8, zorder=3, label=label)
        if to_pts:
            xs, ys = zip(*to_pts)
            plt.scatter(xs, ys, marker='x', s=130, color=color, linewidths=2.5, zorder=3)
    plt.axhline(scaling_timeout_val, color=COLOR_TIMEOUT, linestyle=':', linewidth=1.5, zorder=0)
    plt.text(sizes[0], scaling_timeout_val, " tempo limite raggiunto", fontsize=8.5,
             color=COLOR_TIMEOUT, va='bottom', ha='left')
    plt.scatter([], [], marker='x', s=130, color=COLOR_TIMEOUT, linewidths=2.5,
                label='Tempo limite raggiunto (non è un tempo di completamento reale)')
    plt.xscale('log')
    plt.yscale('log')
    plt.title("Crescita temporale asintotica in scala bilogaritmica (dimensione e tempo)", fontsize=12, fontweight='bold')
    plt.xlabel("Dimensione griglia (lato R = C)", fontsize=10)
    plt.ylabel("Tempo di esecuzione mediano (secondi)", fontsize=10)
    plt.grid(True, which="both", linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "3_complexity_scaling_loglog.png"), dpi=200)
    plt.close()


def _plot_scatter_combined(
    frontier_cells_list: list[float],
    recursive_calls_list: list[float],
    elapsed_time_list: list[float],
    landmarks_count_list: list[float],
    path_length_list: list[float],
    output_dir: str
) -> None:
    """Plot 4: dispersione tempo di esecuzione contro complessità esplorata, in due pannelli
    affiancati (celle di frontiera e invocazioni ricorsive). Le due metriche crescono insieme
    per costruzione (ogni chiamata ricorsiva aggiunge la propria frontiera al totale): prima
    erano due figure separate (4 e 5) con correlazione praticamente identica, qui sono
    un'unica figura per non presentarle come due fenomeni indipendenti."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))

    log_frontier = np.log10(frontier_cells_list)
    log_time = np.log10(elapsed_time_list)
    slope_f, intercept_f = np.polyfit(log_frontier, log_time, 1)
    x_fit_f = np.logspace(min(log_frontier), max(log_frontier), 100)
    y_fit_f = 10**(slope_f * np.log10(x_fit_f) + intercept_f)

    sc1 = ax1.scatter(frontier_cells_list, elapsed_time_list, c=landmarks_count_list,
                       cmap='viridis', s=90, alpha=0.85, edgecolors='black', linewidths=0.5)
    ax1.loglog(x_fit_f, y_fit_f, color='red', linestyle='--', label=f'Pendenza: {slope_f:.2f}')
    fig.colorbar(sc1, ax=ax1, label="Numero totale di landmark")
    ax1.set_xscale('log')
    ax1.set_yscale('log')
    ax1.set_title("Tempo contro celle di frontiera", fontsize=11, fontweight='bold')
    ax1.set_xlabel("Celle di frontiera considerate", fontsize=10)
    ax1.set_ylabel("Tempo di esecuzione (secondi)", fontsize=10)
    ax1.grid(True, which="both", linestyle='--', alpha=0.5)
    ax1.legend(fontsize=9)

    log_recursive = np.log10(recursive_calls_list)
    slope_r, intercept_r = np.polyfit(log_recursive, log_time, 1)
    x_fit_r = np.logspace(min(log_recursive), max(log_recursive), 100)
    y_fit_r = 10**(slope_r * np.log10(x_fit_r) + intercept_r)

    sc2 = ax2.scatter(recursive_calls_list, elapsed_time_list, c=path_length_list,
                       cmap='plasma', s=90, alpha=0.85, edgecolors='black', linewidths=0.5)
    ax2.loglog(x_fit_r, y_fit_r, color='red', linestyle='--', label=f'Pendenza: {slope_r:.2f}')
    fig.colorbar(sc2, ax=ax2, label="Lunghezza del cammino minimo")
    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_title("Tempo contro invocazioni ricorsive", fontsize=11, fontweight='bold')
    ax2.set_xlabel("Numero di invocazioni ricorsive", fontsize=10)
    ax2.set_ylabel("Tempo di esecuzione (secondi)", fontsize=10)
    ax2.grid(True, which="both", linestyle='--', alpha=0.5)
    ax2.legend(fontsize=9)

    fig.suptitle("Tempo di esecuzione e complessità esplorata (scala bilogaritmica)",
                 fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "4_scatter_time_vs_frontier.png"), dpi=200)
    plt.close()


def _plot_symmetry(pruning_res: list[dict[str, object]], output_dir: str) -> None:
    """Plot 6: tempo O→D contro D→O sulla coppia d'angolo, per tipologia di ostacolo. La
    lunghezza minima coincide nelle due direzioni: qui si mostra invece che il
    costo computazionale può differire anche di un ordine di grandezza, perché l'ordine di
    visita della frontiera dipende dal verso di marcia."""
    sym_types = [r["obstacle_type"] for r in pruning_res]
    corner_od = [r["coppie_strong"][0]["andata"]["elapsed_time_s"] for r in pruning_res]
    corner_do = [r["coppie_strong"][0]["ritorno"]["elapsed_time_s"] for r in pruning_res]

    x3 = np.arange(len(sym_types))
    width = 0.35
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.bar(x3 - width / 2, corner_od, width, label='O → D', color=COLOR_ANDATA)
    ax.bar(x3 + width / 2, corner_do, width, label='D → O', color=COLOR_RITORNO)
    ax.set_title("Tempo di esecuzione O→D contro D→O sulla coppia d'angolo (potatura forte)", fontsize=12, fontweight='bold')
    ax.set_xticks(x3)
    ax.set_xticklabels(sym_types)
    ax.set_ylabel("Tempo di esecuzione (secondi)")
    ax.set_yscale('log')
    ax.legend()
    ax.grid(True, which='both', linestyle='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "6_symmetry_per_type.png"), dpi=200)
    plt.close()


def generate_plots(
    scaling_res: list[dict[str, object]],
    density_res: list[dict[str, object]],
    pruning_res: list[dict[str, object]],
    ordering_res: list[dict[str, object]],
    output_dir: str
) -> None:
    """
    Genera ed esporta la suite di sei grafici ad alta risoluzione (2000x2000 px equivalenti)
    per l'analisi asintotica formale.
    """
    frontier_cells_list, elapsed_time_list, landmarks_count_list, recursive_calls_list, path_length_list = (
        _estrai_campioni(scaling_res, density_res, pruning_res, ordering_res)
    )

    _plot_time_vs_density(density_res, output_dir)
    _plot_pruning_comparison(pruning_res, ordering_res, output_dir)
    _plot_scaling(scaling_res, output_dir)
    if elapsed_time_list:
        _plot_scatter_combined(
            frontier_cells_list, recursive_calls_list, elapsed_time_list,
            landmarks_count_list, path_length_list, output_dir
        )
    _plot_symmetry(pruning_res, output_dir)
