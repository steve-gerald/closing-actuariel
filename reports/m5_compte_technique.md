# Module 5 — Note technique : Résultat technique non-vie

Périmètre : compte technique de l'exercice de souscription 2025, brut et net de réassurance, par segment, avec ratios de pilotage.

---

## 1. Synthèse exécutive

| Indicateur (2025) | Flottes | Particuliers | **Total** |
|---|---:|---:|---:|
| Primes acquises | 3,03 M€ | 4,20 M€ | **7,23 M€** |
| Résultat technique net | +622 k€ | −369 k€ | **+253 k€** |
| **Ratio combiné** | **79,2 %** | **108,2 %** | **96,1 %** |

Sous 100 % de ratio combiné, l'activité est rentable avant produits financiers ; au-dessus, elle perd de l'argent. Le portefeuille est à 96,1 %, donc rentable de peu. Ce chiffre cache des Particuliers en perte (108,2 %) que compensent des Flottes très rentables (79,2 %).

## 2. Base comptable et structure

Le compte est établi en base exercice de souscription (underwriting year) : on rapproche la prime totale d'une cohorte de la charge ultime de cette même cohorte. C'est cohérent avec les données du projet (exposition annuelle pleine en M1).

```
(+) Primes acquises
(−) Charge de sinistres de l'exercice courant   (ultimate BF, depuis M2)
(±) Boni-mali sur exercices antérieurs           (depuis M4)
(−) Frais d'acquisition (15 %)
(−) Frais de gestion (12 %)
(=) Résultat technique BRUT
(−) Prime de réassurance cédée
(+) Récupérations de réassurance
(=) Résultat technique NET
```

## 3. Le compte technique 2025

| Poste (€) | Flottes | Particuliers | Total |
|---|---:|---:|---:|
| (+) Primes acquises | 3 031 733 | 4 201 124 | 7 232 857 |
| (−) Charge sinistres courant | 1 301 549 | 2 909 373 | 4 210 922 |
| (±) Boni-mali antérieurs | −280 940 | −502 763 | −783 703 |
| (−) Frais d'acquisition | 454 760 | 630 169 | 1 084 929 |
| (−) Frais de gestion | 363 808 | 504 135 | 867 943 |
| **(=) Résultat technique BRUT** | **+630 676** | **−345 315** | **+285 361** |
| (−) Prime réass. cédée | 66 819 | 178 371 | 245 190 |
| (+) Récupérations réass. | 58 103 | 155 105 | 213 209 |
| **(=) Résultat technique NET** | **+621 961** | **−368 581** | **+253 380** |

## 4. Ratios de pilotage

| Ratio | Flottes | Particuliers | Total |
|---|---:|---:|---:|
| S/P exercice courant | 42,9 % | 69,3 % | 58,2 % |
| S/P comptable (avec run-off) | 52,2 % | 81,2 % | 69,1 % |
| Ratio de frais | 27,0 % | 27,0 % | 27,0 % |
| **Ratio combiné** | **79,2 %** | **108,2 %** | **96,1 %** |

**L'effet du run-off sur le ratio combiné.**

Le passage du S/P courant (58,2 %) au S/P comptable (69,1 %) représente +11 points : c'est l'impact du mali de run-off de M4. Autrement dit, sur les 96,1 % de ratio combiné total, près de 11 points proviennent non pas de la sinistralité de l'année, mais de la correction des sous-provisions des exercices passés. À ne regarder que le S/P courant, on croit le portefeuille bien plus rentable qu'il ne l'est. Il faut présenter les deux chiffres côte à côte.

## 5. Effet de la réassurance

Le traité en excédent de sinistre (XL, priorité 150 000 € par sinistre) a été touché par 2 sinistres en 2025 (un par segment, des corporels lourds). Récupérations totales : 213 k€, pour une prime cédée de 245 k€.

Le solde de réassurance est légèrement négatif (−32 k€) au global : c'est le coût net du chargement réassureur (15 %). En moyenne, l'assureur paie plus qu'il ne récupère, ce qui est normal : il achète une protection contre les gros sinistres, pas un gain. Le bénéfice réel de la réassurance est la réduction de la volatilité du résultat et du SCR (non quantifié dans ce projet).

## 6. Recommandations

1. **Action prioritaire sur les Particuliers** : ratio combiné de 108,2 %, le segment perd de l'argent. Hausse tarifaire ciblée + révision de la segmentation. Cohérent avec le diagnostic LAT (M3) et boni-mali (M4).
2. **Capitaliser sur les Flottes** : ratio combiné de 79,2 %, il y a de la place pour croître, à condition de tenir la volatilité des gros sinistres (c'est le rôle du traité XL).
3. **Revoir les triangles chaque trimestre** : onze points du ratio combiné viennent du run-off. Une revue trimestrielle des réserves éviterait de tout découvrir à la clôture annuelle.
4. **Réviser la structure de réassurance** : avec seulement 2 sinistres touchant la priorité de 150 k€, évaluer si une priorité plus haute (200-250 k€) réduirait le coût net tout en conservant la protection sur les sinistres vraiment exceptionnels.

## 7. Limites

**Non-additivité du Chain-Ladder entre segments.**

Le boni-mali sommé par segment (−783 703 €) diffère légèrement du boni-mali calculé au niveau portefeuille en M4 (−780 387 €), soit un écart de 3 316 € (0,4 %). Ce n'est pas une erreur : le Chain-Ladder n'est pas additif. Projeter deux triangles séparés (Flottes, Particuliers) puis sommer ne donne pas exactement le même résultat que projeter le triangle agrégé, car les facteurs de développement diffèrent d'un segment à l'autre. En production, on choisit une convention (généralement la somme des projections segmentaires, plus fine) et on documente l'écart de réconciliation.

Autres limites :
- **Ventilation de l'ultimate BF par segment** au prorata de la charge vraie : en toute rigueur, il faudrait estimer un BF par segment (avec un a priori S/P propre à chaque segment).
- **Pas de produits financiers** : le résultat technique est avant rendement des placements. Le résultat net comptable de l'assureur intégrerait le produit financier sur les provisions.

## 8. Fichiers produits

```
data/processed/
└── m5_compte_technique.csv         (compte détaillé par segment)

outputs/
└── m5_resultat_technique.png       (figure 2-panels)
```

## 9. Module suivant : Module 6 — Automatisation BAU

Le module 6 enchaîne M1 à M5 en un pipeline qu'on relance à chaque clôture, avec :
- orchestration des scripts,
- contrôles de cohérence automatiques (réconciliations, seuils d'alerte),
- export d'un classeur Excel de pilotage formaté (onglets standardisés : triangle, provisions, LAT, boni-mali, compte technique),
- note de gouvernance (qui valide quoi, fréquence, principe des quatre yeux).
