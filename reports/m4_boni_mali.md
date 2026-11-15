# Module 4 — Note technique : Analyse boni-mali

**Périmètre :** mesure du résultat de run-off entre les clôtures du 31/12/2024 et du 31/12/2025, par année de survenance et par segment.

---

## 1. Synthèse exécutive

Le portefeuille affiche un **mali global de run-off de −780 387 €** sur l'exercice 2025. Autrement dit, les provisions constituées au 31/12/2024 se sont révélées **insuffisantes** : l'estimation de la charge ultime a été revue à la hausse de 0,78 M€ au cours de l'année.

Le mali est **concentré sur la cohorte 2023 (−418 k€, soit 54 % du mali total)** et, au sein de celle-ci, sur le **segment Particuliers (−344 k€)**.

> **En clair —** *Un « boni » signifie qu'on avait trop provisionné l'an dernier : bonne nouvelle, on libère de la provision, ça améliore le résultat. Un « mali » signifie qu'on avait trop peu provisionné : il faut renforcer la provision, ça dégrade le résultat. Ici, tout est en mali : le provisionnement 2024 était globalement trop optimiste.*

## 2. Méthode

On reconstruit le triangle des paiements tel qu'il était **visible à chaque date de clôture** :
- Au 31/12/2024 : triangle 4×4 (cohortes 2021-2024, en retirant la diagonale 2025).
- Au 31/12/2025 : triangle 5×5 (cohortes 2021-2025).

On estime l'Ultimate Chain-Ladder à chaque date, puis :
```
Boni-mali_i = Ultimate_i(clôture 2024) − Ultimate_i(clôture 2025)
```
Le test ne porte que sur les **cohortes communes** (2021-2024). La cohorte 2025 est nouvelle : sa charge relève de la sinistralité de l'exercice courant, pas du run-off sur exercices antérieurs.

## 3. Résultats par année de survenance

| Année | Ultimate clôture 2024 | Ultimate clôture 2025 | Boni-mali | Var % | Nature |
|---|---:|---:|---:|---:|:---:|
| 2021 | 2 940 776 € | 3 106 128 € | −165 353 € | −5,6 % | MALI |
| 2022 | 2 552 305 € | 2 630 329 € | −78 024 € | −3,1 % | MALI |
| **2023** | 4 225 982 € | 4 643 653 € | **−417 671 €** | **−9,9 %** | MALI |
| 2024 | 3 653 186 € | 3 772 526 € | −119 340 € | −3,3 % | MALI |
| **Total** | 13 372 250 € | 14 152 637 € | **−780 387 €** | — | MALI |

## 4. Décomposition par segment

| Segment | 2021 | 2022 | 2023 | 2024 | Total |
|---|---:|---:|---:|---:|---:|
| Flottes | −32 781 | −35 960 | −70 882 | −141 318 | **−280 940 €** |
| Particuliers | −132 572 | −43 573 | **−344 385** | +17 768 | **−502 763 €** |

Les Particuliers portent les deux tiers du mali, presque entièrement concentrés sur la cohorte 2023.

## 5. Diagnostic actuariel — Deux phénomènes distincts

> **À noter — Il faut séparer le biais de méthode du signal de risque réel.**
>
> **(a) Biais structurel de Chain-Ladder sans facteur de queue.** Le mali « de fond » présent sur toutes les cohortes (2021, 2022, 2024) provient en grande partie du fait que Chain-Ladder vanille tronque le développement à la dernière colonne observée. À mesure qu'une cohorte gagne une année de développement supplémentaire, l'Ultimate estimé monte mécaniquement. C'est un **artefact de méthode**, pas une dérive de sinistralité. Il aurait été largement neutralisé si on avait appliqué le facteur de queue dès la clôture 2024 (comme recommandé en M2).
>
> **(b) Signal de risque réel sur la cohorte 2023.** Le mali de −418 k€ sur 2023 est d'une ampleur **disproportionnée** (−9,9 % vs −3 à −5 % ailleurs). Il ne s'explique pas seulement par le biais de méthode : c'est la matérialisation de la sur-sinistralité corporelle déjà identifiée en M2 (vérité terrain hors IC 99,5 % de Mack). **Ce mali-là va se poursuivre** lors des prochaines clôtures.

## 6. Confrontation à la vérité terrain : les malis ne sont pas finis

| Année | Ultimate 2025 (CL) | Vérité terrain | Écart résiduel | Diagnostic |
|---|---:|---:|---:|:---|
| 2021 | 3 106 128 € | 3 361 654 € | +255 525 € | Mali futur probable |
| 2022 | 2 630 329 € | 2 767 420 € | +137 090 € | Mali futur probable |
| **2023** | 4 643 653 € | 5 378 177 € | **+734 524 €** | **Mali futur probable** |
| 2024 | 3 772 526 € | 3 965 069 € | +192 543 € | Mali futur probable |

> **Constat de pilotage majeur —** *L'estimation Chain-Ladder vanille au 31/12/2025 reste inférieure à la vérité terrain sur TOUTES les cohortes. Le portefeuille est donc encore globalement sous-provisionné de ~1,3 M€ à cette date. Si rien n'est corrigé dans la méthode, les clôtures 2026, 2027… continueront d'enregistrer des malis. La cohorte 2023 à elle seule porte +734 k€ de mali latent.*

## 7. Recommandations

1. **Corriger immédiatement la méthode** : appliquer le facteur de queue (M2) à toutes les cohortes dès la clôture 2025. Cela relèverait l'Ultimate de ~3 % et neutraliserait le mali « de méthode » des exercices suivants.
2. **Renforcer spécifiquement la cohorte 2023** : au-delà de la queue, passer une provision complémentaire ciblée pour absorber la sur-sinistralité corporelle. Ordre de grandeur : +0,5 à 0,7 M€.
3. **Documenter le mali pour le contrôle interne** : un mali de −9,9 % sur une cohorte est une exception qui doit être expliquée au comité de provisionnement et à l'auditeur. Joindre l'analyse des gros sinistres corporels 2023.
4. **Mettre en place un suivi trimestriel du run-off** : le boni-mali doit être calculé à chaque clôture, par cohorte et par segment, avec un seuil d'alerte (par ex. mali > 5 % d'une cohorte → investigation obligatoire).
5. **Réviser la tarification Particuliers 2023+** : le mali concentré sur ce segment confirme le diagnostic de sous-tarification du LAT (M3). Cohérence des deux analyses.

## 8. Articulation avec les autres modules

Ce module recoupe et confirme les signaux des modules précédents :
- **M2 (provisionnement)** avait identifié la cohorte 2023 hors IC 99,5 % de Mack → le mali de M4 le matérialise.
- **M3 (LAT)** avait identifié le segment Particuliers en *premium deficiency* → le mali de M4 est porté à 64 % par ce même segment.

Cette convergence de trois analyses indépendantes vers le même diagnostic (Particuliers 2023 sous-provisionné et sous-tarifé) est exactement le type de **triangulation d'indicateurs** qu'une équipe de Technical Risk Monitoring produit pour étayer une recommandation auprès du management.

## 9. Limites

- **Boni-mali calculé sur Chain-Ladder vanille** : le mali de méthode pollue le signal. Une analyse professionnelle utiliserait la méthode retenue en production (BF avec queue) aux deux clôtures pour isoler le run-off « pur ».
- **Pas de décomposition fréquence/coût** : on ne distingue pas si le mali vient d'un nombre de sinistres plus élevé que prévu (IBNYR) ou d'un coût moyen revu à la hausse (IBNER). Cette décomposition serait utile pour la cohorte 2023.
- **Pas d'effet d'actualisation ni d'inflation explicite** dans le calcul du run-off.

## 10. Fichiers produits

```
data/processed/
├── m4_boni_mali_global.csv          (par année de survenance)
└── m4_boni_mali_par_segment.csv     (croisé segment × année)

outputs/
└── m4_boni_mali.png                 (figure 2-panels)
```

## 11. Prochaine étape : Module 5 — Résultat technique

Le boni-mali constitue l'une des composantes du compte technique. Le Module 5 assemblera le **P&L technique trimestriel complet** :
```
Résultat technique = Primes acquises
                   − Charge de sinistres de l'exercice
                   ± Boni-mali sur exercices antérieurs   ← issu de M4
                   − Frais (acquisition + gestion)
                   ± Résultat de réassurance
```
avec calcul des ratios S/P, frais et combiné, et comparaison entre trimestres.
