# Clôture actuarielle et suivi des risques techniques

[![CI](https://github.com/steve-gerald/closing-actuariel/actions/workflows/ci.yml/badge.svg)](https://github.com/steve-gerald/closing-actuariel/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

La clôture annuelle d'un portefeuille RC auto simulé, en six modules Python : provisionnement, test d'adéquation IFRS 4, boni-mali, compte technique et contrôles automatiques. Le tout tourne en une commande et produit un classeur Excel de pilotage et un dashboard HTML.

Projet personnel. Les données sont entièrement simulées.

## Démo

| Livrable | Lien |
|---|---|
| Dashboard HTML | [en ligne](https://steve-gerald.github.io/mon_portfolio/projets/closing/) · source : [`dashboard/index.html`](dashboard/index.html) |
| Classeur Excel de pilotage | [`outputs/closing_pilotage_2025.xlsx`](outputs/closing_pilotage_2025.xlsx) (7 onglets, 56 formules) |
| Figures | [`outputs/`](outputs/) |
| Notebook de synthèse | [`notebooks/01_synthese.ipynb`](notebooks/01_synthese.ipynb), exécuté, avec ses sorties |
| Notes techniques | [`reports/`](reports/), une par module (liste plus bas) |
| Document de présentation | [`reports/Closing_Actuariel_Presentation.docx`](reports/Closing_Actuariel_Presentation.docx) (Word, 14 pages) |
| Architecture | [`docs/architecture.md`](docs/architecture.md) |

## Lancer le projet

```bash
pip install -e ".[dev]"

python -m closing.run              # les six modules à la suite
python scripts/generer_figures.py  # 5 figures matplotlib
python scripts/generer_excel.py    # classeur Excel de pilotage
pytest tests/                      # 14 tests

make all                           # tout d'un coup
```

Par défaut, `closing.run` se termine normalement même s'il y a des alertes : ce sont des résultats à analyser, pas des erreurs. Avec `--strict`, la commande renvoie le code 1 dès qu'une alerte apparaît, ce qui permet de bloquer une chaîne automatisée.

## Résultats de la clôture 2025

| Indicateur | Valeur |
|---|---:|
| Polices | 50 000 |
| Primes acquises, 2021-2025 | 32,7 M€ |
| Primes acquises, exercice 2025 | 7,23 M€ |
| Charge ultime estimée (Bornhuetter-Ferguson) | 18,9 M€ |
| Résultat technique net 2025 | +253 k€ |
| Ratio combiné 2025 | 96,1 % |
| Boni-mali sur exercices antérieurs | −780 k€ (mali) |
| Provision pour risque en cours (URR) | 93 k€ |
| Alertes de contrôle | 3, toutes sur les Particuliers |

Quatre analyses menées séparément (provisionnement Mack, LAT IFRS 4, boni-mali, ratio combiné par segment) aboutissent au même constat : les Particuliers, cohorte 2023, sont sous-provisionnés, sous-tarifés et en perte technique.

## Les six modules

| # | Module | Méthodes |
|---|---|---|
| M1 | Simulation du portefeuille | Poisson, lognormale, cadences de paiement |
| M2 | Provisionnement | Chain-Ladder, facteur de queue de Sherman, Bornhuetter-Ferguson, Mack |
| M3 | Test d'adéquation (LAT, IFRS 4) | UPR, DAC, best estimate, URR |
| M4 | Boni-mali | Triangle N-1 reconstruit, comparaison des ultimes |
| M5 | Compte technique | Résultat brut et net, réassurance XL, ratios |
| M6 | Automatisation | Enchaînement des modules, 6 contrôles automatiques |

Les algorithmes sont codés à la main, sans `chainladder` ni autre bibliothèque actuarielle, pour qu'on puisse suivre chaque calcul.

## Organisation du dépôt

```
closing-actuariel/
├── src/closing/              # le code
│   ├── config.py             # hypothèses, au même endroit
│   ├── portefeuille.py       # M1
│   ├── reserving.py          # M2
│   ├── ifrs4.py              # M3
│   ├── boni_mali.py          # M4
│   ├── compte_technique.py   # M5
│   ├── controles.py          # M6
│   ├── pipeline.py           # enchaînement des modules
│   └── run.py                # ligne de commande
├── scripts/                  # figures et classeur Excel
├── dashboard/                # dashboard HTML, un seul fichier
├── notebooks/
├── tests/                    # 14 tests
├── reports/                  # une note technique par module
├── docs/
├── data/                     # créé à l'exécution (CSV non versionnés)
└── outputs/                  # figures et classeur Excel
```

## Code

Python procédural, sans classes, avec des commentaires en français et des boucles explicites. La graine aléatoire est fixée dans `config.py`, donc deux exécutions donnent les mêmes chiffres. Les tests vérifient la reproductibilité, quelques propriétés des estimateurs et le déclenchement de l'URR. La CI GitHub Actions les lance sur Python 3.10, 3.11 et 3.12.

## Données

Le portefeuille est simulé, avec des paramètres proches d'une RC auto belge :
- 50 000 polices sur 5 ans, croissance de 5 % par an ;
- 80 % de Particuliers, 20 % de Flottes ;
- garanties matérielles (développement court) et corporelles (développement long) ;
- inflation des coûts de 2,5 % par an.

La charge ultime réelle de chaque cohorte est conservée, ce qui permet de tester les méthodes de provisionnement contre la vérité.

## Notes techniques

- [`reports/m1_simulation.md`](reports/m1_simulation.md) : simulation et validation du portefeuille
- [`reports/m2_provisionnement.md`](reports/m2_provisionnement.md) : méthodes et backtest
- [`reports/m3_lat_ifrs4.md`](reports/m3_lat_ifrs4.md) : test IFRS 4 et passage à IFRS 17
- [`reports/m4_boni_mali.md`](reports/m4_boni_mali.md) : biais de méthode ou vrai signal de risque
- [`reports/m5_compte_technique.md`](reports/m5_compte_technique.md) : compte technique et ratios
- [`reports/m6_gouvernance.md`](reports/m6_gouvernance.md) : automatisation, contrôles, principe des quatre yeux

## Limites

- Exposition d'un an plein par police (pas de prorata, sauf dans M3).
- Triangles annuels, pas trimestriels.
- Deux segments seulement (Particuliers, Flottes).
- Pas de catastrophes ni de réassurance proportionnelle.
- Inflation constante : pas de choc comme en 2022-2023.

## Licence

[MIT](LICENSE).

## Auteur

Steve G. SIMO TCHEMO, Master en sciences actuarielles (UCLouvain, 2024), enseignant de mathématiques en Belgique. [Portfolio](https://steve-gerald.github.io/mon_portfolio/) · [LinkedIn](https://www.linkedin.com/in/s-g-simo-tchemo/)
