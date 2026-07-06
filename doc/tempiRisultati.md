# Tempi e risultati sperimentali

Questo file conteneva il log grezzo di una campagna eseguita da una **versione precedente e
poi rimossa** del sistema (cache dei sotto-problemi + *Greedy Seeding*, eliminate per un bug
di correttezza della chiave di cache che violava la simmetria O–D / D–O). Quei tempi — ad
esempio griglie 200×200 risolte "in frazioni di secondo" — non riflettono il comportamento
attuale e contraddicevano i risultati validi.

I risultati correnti e riproducibili si trovano in `results/`:

- `scaling_results.json` — campagna di scaling (taglie 10–200, tempo limite 600 s):
  taglie 10 e 20 complete in millisecondi; a 50 la potatura debole raggiunge il tempo
  limite; da 100 in su le esecuzioni vengono interrotte (muro esponenziale documentato
  in Relazione).
- `divario_anytime.json` — divario percentuale dei risultati anytime rispetto all'ottimo
  esatto calcolato con l'oracolo A* (`scripts/verifica_oracolo_astar.py`).
- `density_results.json`, `pruning_comparison.json`, `ordering_comparison.json`,
  `symmetry_per_type.json` — altri esperimenti della campagna (`main.py experiment`).

Per rieseguire la campagna: `python main.py experiment --output-dir results` (circa 2 ore).
