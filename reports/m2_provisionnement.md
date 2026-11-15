# Module 2 — Note technique : Provisionnement

Périmètre : estimation de la charge ultime et des provisions IBNR du portefeuille MTPL au 31/12/2025, par triangulation. Trois méthodes confrontées à la vérité terrain (Module 1).

---

## 1. Synthèse exécutive

| Méthode | Ultimate total (€) | Écart vs vérité | IBNR (€) |
|---|---:|---:|---:|
| **Vérité terrain** (inconnue en pratique) | **19 332 211** | — | 5 563 629 |
| Chain-Ladder vanille | 18 019 044 | **−6,79 %** | 4 250 462 |
| Chain-Ladder + facteur de queue | 18 752 481 | −3,00 % | 4 983 899 |
| Bornhuetter-Ferguson (S/P a priori 60 %) | 18 940 648 | **−2,03 %** | 5 172 066 |

Les trois méthodes sous-estiment la charge ultime, mais Bornhuetter-Ferguson est la plus précise au niveau portefeuille (−2 %). Cela tient au fait que la cohorte 2023 est anormalement chargée par quelques sinistres corporels lourds, et que les méthodes purement chain-ladder ne peuvent pas le détecter à ce stade de développement.

## 2. Méthodologie

### 2.1 Chain-Ladder déterministe

Hypothèse fondamentale : le ratio de développement entre l'année j et j+1 est stable d'une cohorte à l'autre.

Link ratios calculés (volume-weighted) :

| Transition | f |
|---|---:|
| f₀→₁ | 1,6177 |
| f₁→₂ | 1,2371 |
| f₂→₃ | 1,1151 |
| f₃→₄ | 1,0562 |

Le ratio baisse d'une colonne à l'autre : l'essentiel de la charge est payé tôt, le reste s'étale. C'est le profil attendu pour de la RC auto.

### 2.2 Facteur de queue

Le triangle 5×5 ne capture pas le développement au-delà de la 5ᵉ année. Or, dans la réalité d'un portefeuille MTPL, les sinistres corporels lourds peuvent se développer jusqu'à 10-15 ans (rentes invalidité, frais médicaux récurrents, IPP). Sans facteur de queue, Chain-Ladder est structurellement biaisé à la baisse.

Méthode retenue : ajustement exponentiel de Sherman (1984) sur la suite des link ratios.

```
ln(f_j − 1) = a + b · j
```

Coefficients estimés : a = −0,554 et b = −0,791.

Le facteur de queue total ressort à 1,0407, équivalent à un développement résiduel de 4,07 % au-delà de la 5ᵉ année. C'est conservateur : pour du corporel pur on viserait plutôt 8-12 %.

### 2.3 Bornhuetter-Ferguson

Hypothèse fondamentale : on dispose d'un a priori de sinistralité ultime (issu du business plan ou du pricing actuariel).

Formule retenue :
```
Ultimate_BF = Paiements_observés + (1 − %_développé) × Ultimate_a_priori
```

A priori utilisé : S/P = 60 % sur la prime acquise (cohérent MTPL belge).

Pourcentages de développement au 31/12/2025 (issus du CL avec queue) :

| Année | % développé |
|---|---:|
| 2021 | 96,1 % |
| 2022 | 91,0 % |
| 2023 | 81,6 % |
| 2024 | 65,9 % |
| 2025 | 40,8 % |

BF s'appuie donc surtout sur l'a priori pour 2024-2025 et surtout sur les paiements observés pour 2021-2022.

### 2.4 Mack stochastique

Estimateur de la variance de prédiction (Mack 1993) :
```
MSEP_i = Ultimate_i² × Σ_{k=dernière_obs}^{n-2} [
            (σ_k² / f_k²) × (1/C_{i,k} + 1/Σ_C_k)
         ]
```

Variances par colonne :

| k | σ_k² | I_k (obs) |
|---|---:|---:|
| 0 | 13 118 | 4 |
| 1 | 4 609 | 3 |
| 2 | 909 | 2 |
| 3 | **179** | 1 (extrapolé par règle Mack) |

La règle d'extrapolation de Mack appliquée à k=3 retient le min de plusieurs options conservatrices, ce qui pourrait sous-estimer l'incertitude réelle de la dernière transition.

## 3. Backtest contre la vérité terrain

| Année | Vérité (€) | CL vanille (€) | Err % | CL + queue (€) | Err % | BF (€) | Err % | Mack IC 99,5 % |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2021 | 3 361 654 | 3 106 128 | −8 % | 3 232 559 | −4 % | 3 243 581 | −4 % | [3,11 ; 3,11] |
| 2022 | 2 767 420 | 2 630 329 | −5 % | 2 737 393 | −1 % | 2 827 913 | +2 % | [2,56 ; 2,70] |
| **2023** | **5 378 177** | **4 643 653** | **−14 %** | **4 832 666** | **−10 %** | **4 664 056** | **−13 %** | **[4,40 ; 4,89]** |
| 2024 | 3 965 069 | 3 772 526 | −5 % | 3 926 081 | −1 % | 3 994 176 | +1 % | [3,33 ; 4,21] |
| 2025 | 3 859 891 | 3 866 407 | 0 % | 4 023 783 | +4 % | 4 210 922 | +9 % | [3,10 ; 4,63] |

### Ce qu'on en retient

**L'année 2023 est en dehors de l'IC 99,5 % de Mack.**

La vérité terrain 2023 (5,38 M€) excède la borne supérieure Mack (4,89 M€) de 10 %. Mack a donc nettement sous-estimé l'incertitude sur cette année. La raison est connue : Mack mesure la variance statistique des link ratios mais pas le risque de modèle (changement de composition du portefeuille, anomalie de sinistralité, effet ponctuel sur la queue de distribution).

En clôture, cela se traduit par un mali probable à venir sur la cohorte 2023 : à mesure que les paiements futurs révéleront la vraie charge, la provision devra être renforcée. C'est un point à remonter dès la clôture 2025.

**BF se comporte mieux que CL sur les années récentes.**

Sur 2025 (peu développée, 41 % seulement), Chain-Ladder vanille tombe pile sur la vérité (0 % d'erreur), mais c'est un hasard. L'erreur standard Mack est de 297 k€ (CV 7,7 %) ce qui donne un IC large [3,10 ; 4,63 M€]. BF surestime de +9 % parce que l'a priori 60 % S/P est légèrement trop prudent.

En pratique, on retient BF pour les années récentes (typiquement les 2 dernières années de survenance) et CL pour les années matures. C'est la pratique courante.

## 4. Recommandations actuarielles pour le closing 2025

1. **Retenir Bornhuetter-Ferguson** comme méthode principale au niveau portefeuille (biais agrégé limité à −2 %).
2. **Investiguer la cohorte 2023** : extraire le top 10 des sinistres ouverts, vérifier la cohérence des estimations dossier-par-dossier (RBNS) vs charge ultime statistique. Si confirmation d'une sur-sinistralité réelle, renforcer la provision de 0,5 à 0,7 M€.
3. **Réintégrer une marge prudentielle de queue** : le facteur de queue de 4 % calé sur Sherman est probablement insuffisant pour du corporel pur. Tester une queue de 6-8 % en sensibilité.
4. **Documenter l'écart IC Mack vs réalité** pour le contrôle interne : l'auditeur externe posera la question.

## 5. Limites de l'analyse

- **Pas de segmentation matériel/corporel** dans cette première version. Or les deux garanties ont des patterns de développement très différents (court vs long tail). En pratique, on ferait deux triangles séparés.
- **Pas de modèle bayésien** (ex. Bühlmann sur les cohortes). Possible amélioration pour stabiliser BF.
- **Pas de IBNYR** (Incurred But Not Yet Reported) modélisé séparément de l'IBNER (Incurred But Not Enough Reported). Pour MTPL c'est acceptable car le délai de déclaration est court ; pour de la RC pro ou médicale il faudrait dissocier.
- **Tail factor Sherman** : la méthode présuppose une décroissance exponentielle des link ratios. Pas toujours vérifié en pratique (rebonds en cas de procès collectifs, etc.).

## 6. Fichiers produits

```
data/processed/
├── m2_synthese_provisionnement.csv     (toutes méthodes par cohorte)
└── m2_IBNR.csv                         (provisions par méthode)

outputs/
└── m2_comparaison_methodes.png         (figure 2-panels)
```

## 7. Module suivant : Module 3 — Liability Adequacy Test (IFRS 4)

Avec l'Ultimate estimé par BF (méthode retenue) et la décomposition par cohorte, on peut maintenant :
1. Calculer la provision pour sinistres à payer (PSAP) totale = somme des IBNR.
2. Évaluer la provision pour primes non acquises (UPR) sur les contrats en cours au 31/12/2025.
3. Comparer UPR vs best estimate des engagements futurs sur ces contrats → c'est le LAT IFRS 4 stricto sensu.
4. Identifier les segments en *premium deficiency* nécessitant une provision complémentaire (Unexpired Risk Reserve).
