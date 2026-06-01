# Closing Actuariel & Suivi des Risques Techniques

> Pipeline complet de clôture actuarielle non-vie sur un portefeuille MTPL simulé : provisionnement stochastique, test d'adéquation IFRS 4, analyse boni-mali, compte technique et automatisation BAU.

[![CI](https://img.shields.io/badge/CI-passing-brightgreen.svg)](.github/workflows/ci.yml)
[![Tests](https://img.shields.io/badge/tests-14%20passed-brightgreen.svg)](tests/)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Code style](https://img.shields.io/badge/code%20style-procedural-lightgrey.svg)]()

---

## 📌 En une ligne

Six modules Python qui reproduisent l'intégralité du workflow d'une équipe **Technical Risk Monitoring** dans un environnement de bancassurance européen, du portefeuille brut à la clôture trimestrielle pilotée par un classeur Excel formaté et un dashboard HTML interactif.

## 🎯 Démo

| Livrable | Lien |
|---|---|
| **Dashboard HTML interactif** | [`dashboard/index.html`](dashboard/index.html) — à ouvrir dans un navigateur |
| **Classeur Excel de pilotage** | [`outputs/closing_pilotage_2025.xlsx`](outputs/closing_pilotage_2025.xlsx) — 7 onglets, 56 formules vivantes |
| **Notebook de synthèse** | [`notebooks/01_synthese.ipynb`](notebooks/01_synthese.ipynb) — exécution interactive de la chaîne |
| **Notes techniques** | [`reports/`](reports/) — une note par module |
| **Document de présentation** | [`reports/Closing_Actuariel_Presentation.docx`](reports/) — version Word 19 pages |

## 🚀 Quickstart

```bash
# 1. Installer le package en mode editable
pip install -e ".[dev]"

# 2. Lancer le pipeline complet (les six modules en séquence)
python -m closing.run

# 3. Générer les figures matplotlib
python scripts/generer_figures.py

# 4. Générer le classeur Excel de pilotage
python scripts/generer_excel.py

# 5. Lancer les tests unitaires
pytest tests/

# Ou tout en une commande :
make all
```

## 📊 Résultats clés de la clôture 2025

| Indicateur | Valeur |
|---|---:|
| Polices analysées | 50 000 |
| Primes acquises totales | 32,7 M€ |
| Charge ultime estimée (méthode BF) | 18,9 M€ |
| Résultat technique net | +253 k€ |
| **Ratio combiné global** | **96,1 %** |
| Boni-mali sur exercices antérieurs | −780 k€ (mali) |
| Provision pour risque en cours (URR) | 94 k€ |
| Alertes de contrôle automatique | **3** (toutes sur le segment Particuliers) |

> **Diagnostic central :** quatre analyses méthodologiquement indépendantes (provisionnement Mack, LAT IFRS 4, boni-mali Chain-Ladder, ratio combiné segmenté) convergent vers le même constat : le segment Particuliers, cohorte 2023, est **simultanément sous-provisionné, sous-tarifé et en perte technique**.

## 🏗️ Architecture

```
closing-actuariel/
├── src/closing/              # Package Python (cœur métier)
│   ├── config.py             # Hyperparamètres centralisés
│   ├── portefeuille.py       # M1 — Simulation MTPL
│   ├── reserving.py          # M2 — Chain-Ladder, BF, Mack
│   ├── ifrs4.py              # M3 — Liability Adequacy Test
│   ├── boni_mali.py          # M4 — Analyse du run-off
│   ├── compte_technique.py   # M5 — P&L technique
│   ├── controles.py          # M6 — Contrôles de cohérence
│   ├── pipeline.py           # Orchestrateur
│   └── run.py                # Point d'entrée CLI
├── scripts/                  # Générateurs de livrables
│   ├── generer_figures.py    # 5 figures matplotlib
│   └── generer_excel.py      # Classeur Excel formaté
├── dashboard/                # Dashboard HTML autonome (1 fichier)
├── notebooks/                # Notebook de synthèse
├── tests/                    # 14 tests unitaires
├── reports/                  # Notes techniques par module
├── data/raw/                 # Polices, sinistres, paiements (simulés)
├── data/processed/           # Triangles, agrégats, sorties intermédiaires
└── outputs/                  # Figures et classeur Excel
```

## 🧩 Modules

| # | Module | Méthodes implémentées |
|---|---|---|
| M1 | Simulation portefeuille MTPL | Poisson, Lognormale, patterns Sherman |
| M2 | Provisionnement | Chain-Ladder, facteur de queue (Sherman), Bornhuetter-Ferguson, Mack stochastique |
| M3 | Liability Adequacy Test (IFRS 4) | UPR · DAC · Best Estimate · URR |
| M4 | Boni-mali | Reconstruction triangle N-1, comparaison Ultimate |
| M5 | Compte technique non-vie | P&L brut/net, réassurance XL, ratios |
| M6 | Automatisation BAU | Orchestration + 6 contrôles automatiques |

## 🎯 Alignement avec une fiche de poste *Closing and Risk Monitoring Actuary*

| Exigence type | Module(s) du projet |
|---|---|
| Actuarial closing processes | M1 + M5 |
| Reserve adequacy reviews | M2 + M3 |
| Boni-mali variance analyses | M4 |
| Quarterly technical result reporting | M5 |
| Automate BAU processes | M6 |
| IFRS 4-like experience | M3 (LAT explicite + transition IFRS 17 documentée) |
| Excel + Python | M6 (classeur formaté + pipeline complet) |

## 🧪 Qualité du code

- **Style** : Python procédural, niveau étudiant Master 2, sans POO ni patterns avancés
- **Lisibilité** : commentaires français, docstrings systématiques, boucles explicites
- **Tests** : 14 tests unitaires couvrant les invariants critiques (reproductibilité, propriétés des estimateurs, déclenchement de l'URR)
- **CI** : GitHub Actions teste sur Python 3.10, 3.11 et 3.12
- **Reproductibilité** : graine aléatoire fixée, hypothèses centralisées dans `config.py`

```bash
$ pytest tests/
============================== 14 passed in 3.59s ==============================
```

## 📂 Données

Le portefeuille analysé est **entièrement simulé** à des fins pédagogiques. Aucune référence à un portefeuille réel.

Paramètres calibrés pour reproduire le comportement d'un MTPL belge :
- 50 000 polices sur 5 années (croissance +5 % p.a.)
- Mix Particuliers / Flottes : 80 / 20
- Garanties Matériel (court-tail) / Corporel (long-tail)
- Inflation des coûts : 2,5 % p.a.

La vérité terrain (Ultimate vrai par cohorte) est conservée afin de permettre le backtesting des méthodes de provisionnement.

## 🛠️ Stack

- **Langage** : Python 3.10+ (procédural)
- **Bibliothèques** : numpy, pandas, matplotlib, openpyxl
- **Frontend** : HTML/CSS/JS vanilla (dashboard autonome, sans framework)
- **Tests** : pytest, pytest-cov
- **CI/CD** : GitHub Actions

Aucune dépendance à une bibliothèque actuarielle externe (`chainladder`, `lifelib`...). Tous les algorithmes (Chain-Ladder, Mack, Sherman tail factor, Bornhuetter-Ferguson) sont implémentés à la main pour la pédagogie et l'auditabilité.

## 📚 Documentation

Chaque module dispose d'une note technique dédiée dans `reports/` :

- [`reports/m1_simulation.md`](reports/) — Cadre de simulation, validation
- [`reports/m2_provisionnement.md`](reports/) — Méthodologie et backtest
- [`reports/m3_lat_ifrs4.md`](reports/) — Test IFRS 4, transition IFRS 17
- [`reports/m4_boni_mali.md`](reports/) — Distinction biais de méthode vs signal de risque
- [`reports/m5_compte_technique.md`](reports/) — Compte technique et ratios
- [`reports/m6_gouvernance.md`](reports/) — Pipeline BAU, gouvernance, four-eyes

## ⚠️ Limites assumées

Le projet présente plusieurs limites volontairement assumées et documentées dans les notes techniques de chaque module :

- Exposition annuelle pleine (pas de pro-rata de souscription en dehors de M3)
- Granularité annuelle plutôt que trimestrielle pour les triangles
- Segmentation à deux modalités (Particuliers / Flottes)
- Pas de couches catastrophes ni de réassurance proportionnelle
- Inflation constante (pas de choc inflationniste 2022-2023)

Ces limites correspondent à des choix d'épure pédagogique et leur extension constitue des axes naturels de poursuite en environnement professionnel.

## 📄 Licence

[MIT](LICENSE) — utilisation libre, attribution appréciée.

## 👤 Auteur

**Steve** — enseignant de mathématiques (Belgique) et Master en Sciences Actuarielles (UCLouvain, 2024), en transition vers le pricing P&C et le closing actuariel en bancassurance européenne.

Projet de portfolio destiné à démontrer la maîtrise concrète, livrable par livrable, de l'ensemble des artefacts attendus dans un poste de Closing and Risk Monitoring Actuary.
