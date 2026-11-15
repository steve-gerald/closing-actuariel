# Module 3 — Note technique : Liability Adequacy Test (IFRS 4)

Périmètre : test d'adéquation des provisions techniques au 31/12/2025 sous référentiel IFRS 4 (§15-19), par segment de risque homogène (Particuliers / Flottes).

---

## 1. Synthèse exécutive

Le portefeuille présente une insuffisance de prime sur le segment Particuliers : la provision pour primes non acquises (UPR), nette des frais d'acquisition reportés (DAC), ne couvre pas entièrement la charge future attendue. Il faut comptabiliser une provision pour risque en cours (URR) de 92 795 €.

| Indicateur | Montant |
|---|---:|
| PSAP (sinistres à payer, méthode BF) | 5 172 066 € |
| UPR (primes non acquises) | 3 602 546 € |
| **URR (risque en cours, issu du LAT)** | **92 795 €** |
| **Provisions techniques totales** | **8 867 407 €** |

## 2. Rappel du cadre IFRS 4

Le Liability Adequacy Test (LAT) est une exigence d'IFRS 4. À chaque clôture, l'assureur doit vérifier que les passifs d'assurance comptabilisés sont suffisants pour couvrir les flux de trésorerie futurs estimés. Concrètement, pour le non-vie, cela revient à se demander : « la prime que j'ai encaissée mais pas encore "gagnée" (UPR) suffira-t-elle à payer les sinistres et frais à venir sur la période restante du contrat ? » Si non, on doit constituer une provision complémentaire.

Le test se réalise au niveau de portefeuilles de contrats soumis à des risques similaires (IFRS 4.15). Ici, on retient une segmentation Particuliers / Flottes, car leurs profils de sinistralité diffèrent fortement.

**Test formel, par segment :**
```
UPR_net_de_DAC  ≥  Best_Estimate_charges_futures   ?
```
- Si oui : adéquation satisfaite, aucune provision complémentaire.
- Si non : *premium deficiency*. On comptabilise une URR = Best Estimate − UPR net.

## 3. Hypothèse structurante introduite

Le Module 1 supposait une exposition d'un an plein par police, ce qui ne laisse aucune prime « non acquise ». Pour réaliser un LAT réaliste, ce module introduit une date de souscription répartie uniformément sur l'année (tirage du mois 1 à 12). La part de prime non écoulée au 31/12/2025 est calculée par la méthode 1/24 (souscription supposée au milieu du mois). Cette hypothèse n'affecte que le calcul de l'UPR ; le provisionnement des sinistres (M2) reste inchangé.

## 4. Calcul détaillé

### 4.1 Ratios S/P ultimes par segment

| Segment | Primes | Charge ultime | S/P |
|---|---:|---:|---:|
| Flottes | 13,6 M€ | 5,4 M€ | **40,1 %** |
| Particuliers | 19,2 M€ | 13,9 M€ | **72,5 %** |

Le S/P des Particuliers est 1,8 fois celui des Flottes. C'est ce qui fait basculer le LAT.

### 4.2 UPR et DAC (cohorte 2025)

| Segment | UPR brut | DAC (15 %) | UPR net |
|---|---:|---:|---:|
| Flottes | 1 519 279 € | 227 892 € | 1 291 387 € |
| Particuliers | 2 083 267 € | 312 490 € | 1 770 777 € |
| **Total** | **3 602 546 €** | **540 382 €** | **3 062 164 €** |

### 4.3 Best estimate des charges futures

Le ratio appliqué à l'UPR brut est le ratio combiné technique = S/P + frais de gestion (12 %) + frais de sinistres / ULAE (5 %). Les frais d'acquisition ne sont pas recomptés ici, car ils ont déjà été déduits via le DAC.

| Segment | Ratio combiné technique | Best Estimate |
|---|---:|---:|
| Flottes | 57,1 % | 868 092 € |
| Particuliers | **89,5 %** | 1 863 572 € |

## 5. Résultat du LAT

| Segment | UPR net | Best Estimate | Marge | URR | Test |
|---|---:|---:|---:|---:|:---:|
| Flottes | 1 291 387 € | 868 092 € | +423 295 € | 0 € | OK |
| **Particuliers** | 1 770 777 € | 1 863 572 € | **−92 795 €** | **92 795 €** | DEFICIENCY |
| **Total** | 3 062 164 € | 2 731 664 € | +330 500 € | 92 795 € | — |

**Le test agrégé masque une insuffisance segmentaire.**

Au global, l'UPR net (3,06 M€) dépasse le best estimate (2,73 M€) de 331 k€, et on pourrait s'arrêter là. Mais IFRS 4 demande le test par portefeuille homogène, et par segment les Particuliers sont déficitaires de 93 k€.

La marge des Flottes ne compense pas le déficit des Particuliers : chaque segment déficitaire doit être provisionné. Un test fait seulement au global sous-provisionne, et l'auditeur le relèvera.

## 6. Lecture pour la direction

Le segment Particuliers est sous-tarifé : avec un S/P de 72,5 % et un ratio combiné technique de 89,5 %, la marge technique avant frais d'acquisition n'est que de 10,5 %. Une fois les 15 % de frais d'acquisition pris en compte, le combiné dépasse 100 % → le segment perd de l'argent sur la période non couverte.

**Recommandations :**
1. **Comptabiliser l'URR de 92 795 €** au passif du bilan 2025 (poste « provision pour risque en cours »).
2. **Réviser la tarification Particuliers** : hausse tarifaire ciblée de l'ordre de 3 à 5 % pour ramener le combiné sous 100 % sur la prochaine génération de contrats.
3. **Analyser la sous-segmentation Particuliers** : l'insuffisance peut être concentrée sur certains profils (jeunes conducteurs, zones urbaines). Un pricing GLM affiné permettrait de cibler les hausses.
4. **Surveiller le segment Flottes** : sa marge (+423 k€) laisse de la place pour développer le segment, à condition de surveiller les gros sinistres.

## 7. Limites

- **Best estimate non actualisé** : l'horizon de l'UPR étant inférieur à un an, l'impact de l'actualisation est négligeable. Sous IFRS 17 (qui remplace IFRS 4), l'actualisation deviendrait obligatoire même à court terme.
- **S/P ultime supposé constant** entre cohortes passées et risque futur. En présence d'inflation des sinistres (calée à 2,5 % en M1), le S/P prospectif pourrait être légèrement supérieur → URR sous-estimée. Test de sensibilité recommandé.
- **Pas de marge pour risque explicite** (Risk Adjustment au sens IFRS 17). Le best estimate retenu est une espérance, sans coussin prudentiel.
- **UPR limitée à la cohorte 2025** : cohérent avec l'hypothèse M1 d'exposition annuelle. Un portefeuille réel aurait des contrats pluriannuels à traiter.

## 8. Transition IFRS 4 → IFRS 17

IFRS 4 est une norme transitoire, remplacée par IFRS 17 depuis 2023 pour la plupart des assureurs européens. Sous IFRS 17, la logique du LAT est remplacée par le test de l'« onerous contract » au sein du modèle général (BBA) ou de l'approche par allocation des primes (PAA). Le segment Particuliers déficitaire serait identifié comme un groupe de contrats onéreux dès la comptabilisation initiale, et la perte serait reconnue immédiatement en résultat (Loss Component). Le résultat économique est proche ; c'est le traitement comptable qui change.

## 9. Fichiers produits

```
data/processed/
├── m3_liability_adequacy_test.csv           (détail du test par segment)
└── m3_provisions_techniques_totales.csv     (PSAP + UPR + URR)

outputs/
└── m3_liability_adequacy_test.png           (figure 2-panels)
```

## 10. Module suivant : Module 4 — Analyse boni-mali

Avec les provisions techniques consolidées au 31/12/2025, le Module 4 simulera une clôture précédente (31/12/2024) afin de mesurer la variation des Ultimate entre deux exercices :
```
Boni-mali = Ultimate(clôture N-1) − Ultimate(clôture N)
```
On décomposera cette variation par année de survenance et par segment, en isolant notamment le mali attendu sur la cohorte 2023 (anomalie identifiée en M2 : vérité terrain hors IC 99,5 % de Mack).
