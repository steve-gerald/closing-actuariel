# Architecture & Flux de données

## Diagramme du pipeline

```
                          ┌─────────────────┐
                          │   config.py     │  Hyperparamètres
                          │                 │  centralisés
                          └────────┬────────┘
                                   │
       ┌───────────────────────────┼───────────────────────────┐
       │                           │                           │
       ▼                           ▼                           ▼
┌──────────────┐         ┌──────────────────┐         ┌─────────────────┐
│      M1      │         │      M2          │         │       M3        │
│ portefeuille │────────▶│   reserving      │         │     ifrs4       │
│              │ triangle│                  │         │                 │
│   simuler_   │ vérité  │  Chain-Ladder    │         │  UPR/DAC/URR    │
│   polices    │ terrain │  BF / Mack       │         │  par segment    │
│   sinistres  │         │  Sherman queue   │         │                 │
│   paiements  │─────────┘                  │         └────────┬────────┘
│              │         └────────┬─────────┘                  │
└──────┬───────┘                  │                            │
       │ triangle                 │ ult_bf                     │
       ▼                          ▼                            ▼
┌──────────────┐         ┌──────────────────┐         ┌─────────────────┐
│      M4      │         │       M5         │         │       M6        │
│  boni_mali   │────────▶│ compte_technique │◀────────│   controles     │
│              │ bm/seg  │                  │ alertes │                 │
│  Run-off N-1 │         │ P&L + ratios     │         │  6 contrôles    │
│  vs N        │         │ Réassurance XL   │         │  Seuils alerte  │
└──────────────┘         └──────────────────┘         └─────────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │   pipeline.py    │
                         │                  │
                         │  Orchestrateur   │
                         └────────┬─────────┘
                                  │
                                  ▼
                 ┌────────────────┴────────────────┐
                 ▼                                  ▼
         ┌──────────────┐                  ┌────────────────┐
         │  Livrables   │                  │   Dashboard    │
         │              │                  │     HTML       │
         │  • Figures   │                  │                │
         │  • Excel     │                  │  Navigation    │
         │  • Docx      │                  │  par modules   │
         └──────────────┘                  └────────────────┘
```

## Dépendances inter-modules

| Module aval | Dépend de |
|---|---|
| M2 (reserving) | M1 (triangle) |
| M3 (ifrs4) | M1 (polices, sinistres pour S/P par segment) |
| M4 (boni_mali) | M1 (paiements pour reconstruire triangle N-1) |
| M5 (compte_technique) | M1 (polices), M2 (ult_bf), M4 (boni-mali par segment) |
| M6 (controles) | M2, M3, M4, M5 (résultats agrégés) |

Aucun module ne dépend d'un module situé après lui. On peut donc relire
et vérifier chaque étape séparément.

## Conventions de signe

- **Boni-mali** : positif = boni (l'estimation a baissé), négatif = mali
- **Marge LAT** : positive = UPR suffisant, négative = déficience
- **Résultat technique** : positif = profit, négatif = perte
- **Ratios** : exprimés en proportion (0,961 = 96,1 %)

## Reproductibilité

La graine aléatoire (`config.SEED = 20260527`) fait que deux exécutions
donnent exactement les mêmes chiffres. N'importe quel résultat peut être
rejoué et vérifié.

```python
>>> from closing.pipeline import executer_closing
>>> r1 = executer_closing(REPO, verbose=False)
>>> r2 = executer_closing(REPO, verbose=False)
>>> assert (r1['triangle'] == r2['triangle']).all().all()  # True
```
