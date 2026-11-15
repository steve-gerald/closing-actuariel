# Module 6 — Note de gouvernance : Automatisation BAU

**Périmètre :** industrialisation de la chaîne de clôture (M1 → M5), contrôles de cohérence automatiques, classeur Excel de pilotage et cadre de gouvernance.

---

## 1. Objectif

Transformer une série de scripts d'analyse en un **processus de clôture reproductible et auditable**, exécutable en une commande à chaque échéance trimestrielle. C'est la réponse directe à l'exigence « automate and streamline BAU processes » de la fiche de poste.

```
python scripts/m6_pipeline_bau.py
```

Cette commande unique :
1. ré-exécute les cinq modules dans l'ordre (simulation → provisionnement → LAT → boni-mali → compte technique) ;
2. lance six contrôles de cohérence avec seuils d'alerte ;
3. produit le journal des contrôles ;
4. génère le classeur Excel de pilotage formaté.

## 2. Les six contrôles automatiques

> **En clair —** *Un closing professionnel ne se contente pas de produire des chiffres : il les contrôle automatiquement avant de les diffuser. Chaque contrôle compare un indicateur à un seuil de gouvernance ; tout dépassement déclenche une alerte qui doit être investiguée et documentée avant validation du closing.*

| # | Contrôle | Seuil | Résultat |
|---|---|---|:---:|
| C1 | IBNR positif sur toutes les cohortes | ≥ 0 | ✅ OK |
| C2 | Réconciliation boni-mali (global vs segments) | écart < 1 % | ✅ OK (0,42 %) |
| C3 | Aucun mali significatif par cohorte | mali < 5 % | ⚠️ ALERTE (2021, 2023) |
| C4 | Aucun segment en premium deficiency (LAT) | aucun | ⚠️ ALERTE (Particuliers) |
| C5 | Ratio combiné global rentable | < 100 % | ✅ OK (96,1 %) |
| C6 | Aucun segment en perte technique | combiné < 100 % | ⚠️ ALERTE (Particuliers) |

**Statut global du closing : 3 alertes à investiguer.**

> **À noter — Les trois alertes convergent.** Elles pointent toutes vers le même problème : le segment Particuliers (sous-provisionné sur 2023, déficitaire au LAT, en perte technique). C'est la force d'un dispositif de contrôle multi-angles : trois tests indépendants confirment le diagnostic, ce qui retire tout doute sur le caractère structurel (et non accidentel) du problème. Le contrôle C2, lui, valide que l'écart de réconciliation reste dans la tolérance attendue (non-additivité du Chain-Ladder).

## 3. Le classeur Excel de pilotage

Le livrable `closing_pilotage_2025.xlsx` est structuré en **sept onglets standardisés** :

| Onglet | Contenu |
|---|---|
| 0_Synthese | Indicateurs clés + statut des contrôles (formules inter-onglets) |
| 1_Triangle | Triangle des paiements cumulés |
| 2_Provisionnement | Ultimate par méthode + IBNR, totaux en formules |
| 3_LAT_IFRS4 | Test d'adéquation par segment (UPR net et URR en formules, code couleur) |
| 4_Boni_Mali | Run-off par cohorte (boni-mali en formules, vert/rouge) |
| 5_Compte_Technique | P&L technique + ratios (entièrement en formules vivantes) |
| 6_Controles | Journal des contrôles (statut OK/ALERTE colorisé) |

**Points de conception** :
- **Formules vivantes, pas de valeurs figées** : les ratios, totaux et tests sont des formules Excel (56 formules, zéro erreur vérifiée par recalcul LibreOffice). Le classeur se recalcule si les données source changent.
- **Mise en forme professionnelle** : police Arial, en-têtes bleu institutionnel, formats monétaires avec parenthèses pour les négatifs, codes couleur conditionnels (rouge = alerte, vert = OK).
- **Traçabilité** : l'onglet Synthèse agrège les autres onglets par référence croisée, garantissant la cohérence entre la vue de pilotage et le détail.

## 4. Cadre de gouvernance du closing

> **En clair —** *La gouvernance définit qui fait quoi, quand, et qui valide. En environnement bancaire « governance-heavy » (comme mentionné dans la fiche de poste), c'est aussi important que les calculs eux-mêmes.*

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

Toute alerte (C3, C4, C6 dans ce closing) doit faire l'objet d'une **fiche d'exception** documentée : nature du dépassement, analyse de la cause, décision prise (provision complémentaire, révision tarifaire, acceptation motivée), et validation hiérarchique. Ces fiches constituent la piste d'audit.

## 5. Bénéfices de l'industrialisation

1. **Reproductibilité** : un closing identique produit des résultats identiques (graine aléatoire fixée). Plus de manipulations manuelles non tracées.
2. **Gain de temps** : la clôture passe d'un assemblage manuel de fichiers à une commande unique, ce qui libère du temps pour l'analyse à valeur ajoutée.
3. **Réduction du risque opérationnel** : les contrôles automatiques détectent les anomalies avant diffusion, là où un contrôle manuel peut les manquer.
4. **Auditabilité** : journal des contrôles horodaté, formules vivantes traçables, documentation systématique des exceptions.

## 6. Limites et pistes d'industrialisation supplémentaires

- **Pas de versionnage des hypothèses** : en production, on stockerait chaque jeu d'hypothèses (queue, S/P a priori, seuils) dans un fichier de configuration versionné (Git) pour tracer leur évolution entre clôtures.
- **Pas de base de données** : ici tout passe par des fichiers CSV. Un environnement professionnel utiliserait une base (SQL) avec historisation des clôtures successives. *(Note : la maîtrise de SQL est un axe de progression identifié pour ce type de poste.)*
- **Pas d'orchestrateur** : pour une vraie chaîne BAU, on remplacerait `subprocess` par un orchestrateur (Airflow, Prefect) avec gestion des dépendances, reprise sur erreur et notifications.
- **Granularité annuelle** : le suivi « trimestriel » repose ici sur un phasage. Une chaîne réelle ingérerait des triangles trimestriels.

## 7. Fichiers produits

```
scripts/
├── m6_pipeline_bau.py          (orchestration + contrôles)
└── m6_export_excel.py          (génération du classeur)

data/processed/
└── m6_journal_controles.csv    (journal des 6 contrôles)

outputs/
└── closing_pilotage_2025.xlsx  (CLASSEUR EXCEL DE PILOTAGE — livrable principal)
```

## 8. Conclusion du projet

Le projet couvre désormais l'intégralité de la chaîne de clôture actuarielle non-vie, de la donnée brute au reporting de pilotage automatisé. Chaque ligne de la fiche de poste « Closing and Risk Monitoring Actuary » trouve un livrable correspondant : closing (M1, M5), reserve adequacy (M2, M3), boni-mali variance (M4), quarterly technical reporting (M5), automation of BAU (M6), et expérience IFRS 4 (M3). La cohérence des diagnostics entre modules — convergence sur le segment Particuliers 2023 — démontre une maîtrise de niveau professionnel, au-delà de la simple application de méthodes isolées.
