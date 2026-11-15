# Module 6 — Note de gouvernance : Automatisation BAU

Périmètre : automatisation de la chaîne de clôture (M1 → M5), contrôles de cohérence automatiques, classeur Excel de pilotage et cadre de gouvernance.

---

## 1. Objectif

Faire de cinq scripts d'analyse une clôture qu'on relance en une commande à chaque trimestre, avec les mêmes résultats et une trace de chaque contrôle.

```
python -m closing.run            # ajouter --strict pour bloquer la chaîne en cas d'alerte
```

Cette commande unique :
1. ré-exécute les cinq modules dans l'ordre (simulation → provisionnement → LAT → boni-mali → compte technique) ;
2. lance six contrôles de cohérence avec seuils d'alerte ;
3. produit le journal des contrôles ;
4. génère le classeur Excel de pilotage formaté.

## 2. Les six contrôles automatiques

Les chiffres sont contrôlés avant d'être diffusés. Chaque contrôle compare un indicateur à un seuil de gouvernance ; tout dépassement déclenche une alerte qui doit être investiguée et documentée avant validation du closing.

| # | Contrôle | Seuil | Résultat |
|---|---|---|:---:|
| C1 | IBNR positif sur toutes les cohortes | ≥ 0 | OK |
| C2 | Réconciliation boni-mali (global vs segments) | écart < 1 % | OK (0,42 %) |
| C3 | Aucun mali significatif par cohorte | mali < 5 % | ALERTE (2021, 2023) |
| C4 | Aucun segment en premium deficiency (LAT) | aucun | ALERTE (Particuliers) |
| C5 | Ratio combiné global rentable | < 100 % | OK (96,1 %) |
| C6 | Aucun segment en perte technique | combiné < 100 % | ALERTE (Particuliers) |

**Statut global du closing : 3 alertes à investiguer.**

**Les trois alertes convergent.** Elles pointent toutes vers le même problème : le segment Particuliers (sous-provisionné sur 2023, déficitaire au LAT, en perte technique). Trois tests indépendants donnent le même diagnostic, ce qui rend très peu probable un problème accidentel. Le contrôle C2, lui, valide que l'écart de réconciliation reste dans la tolérance attendue (non-additivité du Chain-Ladder).

## 3. Le classeur Excel de pilotage

Le livrable `closing_pilotage_2025.xlsx` est structuré en sept onglets standardisés :

| Onglet | Contenu |
|---|---|
| 0_Synthese | Indicateurs clés + statut des contrôles (formules inter-onglets) |
| 1_Triangle | Triangle des paiements cumulés |
| 2_Provisionnement | Ultimate par méthode + IBNR, totaux en formules |
| 3_LAT_IFRS4 | Test d'adéquation par segment (UPR net et URR en formules, code couleur) |
| 4_Boni_Mali | Run-off par cohorte (boni-mali en formules, vert/rouge) |
| 5_Compte_Technique | P&L technique + ratios (entièrement en formules vivantes) |
| 6_Controles | Journal des contrôles (statut OK/ALERTE colorisé) |

Points de conception :
- **Formules vivantes, pas de valeurs figées** : les ratios, totaux et tests sont des formules Excel (56 formules, zéro erreur vérifiée par recalcul LibreOffice). Le classeur se recalcule si les données source changent.
- **Mise en forme** : police Arial, en-têtes bleus, formats monétaires avec parenthèses pour les négatifs, codes couleur conditionnels (rouge = alerte, vert = OK).
- **Traçabilité** : l'onglet Synthèse agrège les autres onglets par référence croisée, pour que la synthèse et le détail restent cohérents.

## 4. Cadre de gouvernance du closing

Qui fait quoi, quand, et qui valide. Dans une bancassurance, c'est examiné d'aussi près que les calculs.

### 4.1 Rôles et responsabilités

| Rôle | Responsabilité |
|---|---|
| Actuaire closing (préparateur) | Exécute le pipeline, investigue les alertes, prépare le dossier de clôture |
| Actuaire réviseur (second regard) | Vérifie indépendamment les hypothèses et les résultats (principe des quatre yeux) |
| Responsable provisionnement | Valide les choix méthodologiques et le niveau de provisions |
| Contrôle interne / Audit | Examine le journal des contrôles et la documentation des exceptions |

### 4.2 Principe des quatre yeux (four-eyes principle)

Aucun closing n'est validé sur la seule production de l'actuaire préparateur. Le réviseur contrôle a minima : les hypothèses de queue de développement, l'a priori S/P du Bornhuetter-Ferguson, les seuils d'alerte, et la justification de chaque alerte déclenchée.

### 4.3 Fréquence et calendrier

- **Trimestriel** : exécution complète du pipeline, revue des triangles, mise à jour du boni-mali.
- **Annuel (FY)** : revue approfondie, validation par le comité de provisionnement, documentation pour l'auditeur externe.

### 4.4 Gestion des exceptions

Toute alerte (C3, C4, C6 dans ce closing) doit faire l'objet d'une fiche d'exception documentée : nature du dépassement, analyse de la cause, décision prise (provision complémentaire, révision tarifaire, acceptation motivée), et validation hiérarchique. Ces fiches constituent la piste d'audit.

## 5. Ce que l'automatisation apporte

1. **Reproductibilité** : un closing identique produit des résultats identiques (graine aléatoire fixée). Plus de manipulations manuelles non tracées.
2. **Gain de temps** : la clôture passe d'un assemblage manuel de fichiers à une commande unique, ce qui laisse plus de temps pour analyser les alertes.
3. **Réduction du risque opérationnel** : les contrôles automatiques détectent les anomalies avant diffusion, là où un contrôle manuel peut les manquer.
4. **Auditabilité** : journal des contrôles horodaté, formules vivantes traçables, documentation systématique des exceptions.

## 6. Limites et suites possibles

- **Pas de versionnage des hypothèses** : en production, on stockerait chaque jeu d'hypothèses (queue, S/P a priori, seuils) dans un fichier de configuration versionné (Git) pour tracer leur évolution entre clôtures.
- **Pas de base de données** : ici tout passe par des fichiers CSV. Un environnement professionnel utiliserait une base (SQL) avec historisation des clôtures successives.
- **Pas d'orchestrateur** : pour une vraie chaîne BAU, on remplacerait `subprocess` par un orchestrateur (Airflow, Prefect) avec gestion des dépendances, reprise sur erreur et notifications.
- **Granularité annuelle** : le suivi « trimestriel » repose ici sur un phasage. Une chaîne réelle ingérerait des triangles trimestriels.

## 7. Fichiers produits

```
scripts/
└── generer_excel.py            (génération du classeur)

src/closing/
├── pipeline.py                 (orchestration des modules)
└── controles.py                (les 6 contrôles)

data/processed/
└── m6_journal_controles.csv    (journal des 6 contrôles)

outputs/
└── closing_pilotage_2025.xlsx  (classeur de pilotage)
```

## 8. Pour conclure

Le projet va de la donnée brute au classeur de pilotage : clôture (M1, M5), adéquation des provisions (M2, M3), boni-mali (M4), reporting du résultat technique (M5) et automatisation (M6). Ce qui m'intéresse le plus, c'est que les modules, faits séparément, pointent tous vers le même segment : les Particuliers, cohorte 2023.
