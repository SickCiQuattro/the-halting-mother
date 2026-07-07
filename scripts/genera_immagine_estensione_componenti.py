#!/usr/bin/env python3
"""Figura di sintesi: beneficio del controllo dei componenti connessi (Relazione, Compito 3).

Usa i tempi già misurati da `scripts/verifica_componenti.py` (coppia irraggiungibile su
griglia 50x50 con recinto, si veda `results/verifica_componenti.log`): non li ricalcola,
perché la configurazione "senza controllo" esaurisce da sola l'intero tempo limite di 600 s.
"""
import os

from _common import plt

OUT_PNG = os.path.join(os.path.dirname(__file__), "..", "Relazione", "images", "estensione_componenti.png")

CON_CONTROLLO_S = 0.003659
SENZA_CONTROLLO_S = 600.000257

if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(8, 5))
    barre = ax.bar(
        ["Con controllo\ncomponenti", "Senza controllo\n(tempo limite raggiunto)"],
        [CON_CONTROLLO_S, SENZA_CONTROLLO_S],
        color=["#2ed573", "#ff4757"]
    )
    ax.set_yscale('log')
    ax.set_ylabel("Tempo di esecuzione (secondi)")
    ax.set_title("Coppia irraggiungibile: effetto del controllo\ndei componenti connessi", fontsize=12, fontweight='bold')
    ax.grid(True, which='both', axis='y', linestyle='--', alpha=0.4)
    for barra, valore in zip(barre, [CON_CONTROLLO_S, SENZA_CONTROLLO_S]):
        ax.text(barra.get_x() + barra.get_width() / 2, valore, f"{valore:.4f}s",
                ha='center', va='bottom', fontsize=9)
    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=200)
    print(f"Figura salvata in {OUT_PNG}")
