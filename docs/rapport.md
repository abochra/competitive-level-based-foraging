# Rapport de projet

## Groupe
* HADDOUCHI CELINE 
* ALIAOUI BOCHRA 

## Description des choix importants d'implémentation

La carte est chargée à partir de fichiers JSON représentant différentes configurations : yellow-map, red-map, green-map, blue-map, mixed-map.
La fonction ProblemeGrid2D utilise l'algo A* pour calculer le plus court chemin entre la position du joueur et celle de la fiole.

Les joueurs sont séparés en deux équipes (même nombre de joueurs) selon leur position initiale sur la carte :
   - les joueurs sur la ligne du haut → Equipe 0
   - les joueurs sur la ligne du bas → Equipe 1

### Déroulement d'un épisode
À chaque épisode :
1. Les équipes choisissent des fioles selon leur stratégie.  
2. Les joueurs se déplacent vers les positions choisies.  
3. Le score est calculé.  
4. Les joueurs sont remis à leur position initiale.  


Afin d’éviter un avantage pour une équipe, l’ordre de jeu est inversé à chaque épisode avec la ligne de code :  
`priority=[0,1] if e % 2 == 0 else [1,0]`

### Calcul des scores
Une fois les joueurs positionnés autour des fioles, nous calculons le score de chaque équipe.  
La fonction suivante permet de compter combien de joueurs de chaque équipe se trouvent autour d’une fiole :
*players_around_item()*  
Les règles de score dépendent du type de carte.  

Deux structures d'états sont maintenues entre les épisodes :  
 - `fp_etat[t]`: dictionnaire `{fiole : nb_visites_adversaire}` par équipe pour le *fictitious play*  
 - `rm_etat[t][p]`: dictionnaire `{fiole : regret_cumulé}` par joueur par équipe pour le *regret matching* 

## Description des stratégies proposées

Pour changer la stratégie d'une équipe, il faut juste modifier la liste strategie_eq

**Stratégie têtue**  
Le joueur refait le même choix indéfiniment en le mémorisant (reste têtu).
S'il n'a pas de choix mémorisé au début, il choisit une fiole au hasard et une position libre autour.

**Strategie_aleatoire_uniforme**  
Chaque fois qu’on appelle la stratégie, elle choisit une fiole au hasard et une position parmi toutes les fioles disponibles, sans mémoire ni coordination.

**Strategie_aleatoire_coordination**  
Tous les joueurs de l’équipe choisissent la même fiole.
Chacun prend une position libre différente autour de cette fiole. S’il n’y a plus de positions libres autour de cette dernière, on choisit une autre position au hasard sur une autre fiole.

**Stratégie_fictitious_play**  
Stratégie de best response basée sur l'historique des fioles visitées par l'adversaire. Le joueur choisit la fiole la moins visitée par l’adversaire, sinon au hasard si c’est le premier tour.

**Stratégie_regret_matching**  
Stratégie adaptative basée sur les regrets cumulés par un joueur de ne pas avoir joué une fiole. Plus une fiole a un regret élevé, plus elle a de chances d’être choisie par le joueur. Si tous les regrets sont nuls, le choix de la fiole sera aléatoire.

**Stratégie_UCB** 
Stratégie déterministe qui consiste à exploiter les choix de fioles qui font gagner les agents et à explorer les choix peu explorées jusqu'à présent. 

## Description des résultats
Comparaison entre les stratégies.  
> Tous les tests expérimentaux ont été réalisés avec 10 épisodes de confrontation (en augmentant le game.fps pour plus de rapidité) et un nombre de joueurs dépendant du type de carte.  
> Score indiqué : score_equipe0/score_equipe1 (équipe0 utilise la stratégie en ligne et l'équipe 1 utilise la stratégie en colonne)

### Carte *yellow-map*
Nombre de joueurs = 16 (8 par équipe) 

|   | Têtu | Aléatoire uniforme | Aléatoire coordination | Fictitious play | Regret matching |
| :--- | :---: | :---: | :---: | :---: | ---: |
| **Têtu** | — | 22/16 | 40/10 | 37/11 | 29/16 |
| **Aléatoire uniforme** |  16/22 | — | 33/10 | 28/14 | 29/11 |
| **Aléatoire coordination** | 10/40 | 10/33 | — | 10/26 | 10/33 |
| **Fictitious play** | 11/37 | 14/28 | 26/10 | — | 11/35 |
| **Regret matching** | 16/29 | 11/29 | 33/10 | 35/11 | — |

### Carte *red-map*
Nombre de joueurs = 16 (8 par équipe)

|   | Têtu | Aléatoire uniforme | Aléatoire coordination | Fictitious play | Regret matching |
| :--- | :---: | :---: | :---: | :---: | ---: |
| **Têtu** | — | 21/14 | 15/10 | 19/24 | 19/18 |
| **Aléatoire uniforme** | 14/21 | — | 20/10 | 17/11 | 16/13 |
| **Aléatoire coordination** | 10/15 | 10/20 | — | 9/16 | 10/18 |
| **Fictitious play** | 24/19 | 11/17 | 16/9 | — | 19/17 |
| **Regret matching** | 18/19 | 13/16 | 18/10 | 17/19 | — |


### Carte *green-map*
Nombre de joueurs = 34 (17 par équipe)

|   | Têtu | Aléatoire uniforme | Aléatoire coordination | Fictitious play | Regret matching |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Têtu** | — | 21/37 | 41/18 | 29/22 | 30/29 |
| **Aléatoire uniforme** | 37/21 | — | 28/23 | 26/16 | 21/19 |
| **Aléatoire coordination** | 18/41 | 23/28 | — | 13/13 | 20/18 |
| **Fictitious play** | 22/29 | 16/26 | 13/13 | — | 26/24 |
| **Regret matching** | 29/30 | 19/21 | 18/20 | 24/26 | — |

  
### Carte *blue-map*
Nombre de joueurs = 34 (17 par équipe)

|   | Têtu | Aléatoire uniforme | Aléatoire coordination | Fictitious play | Regret matching |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Têtu** | — | 28/34 | 30/25 | 77/1 | 16/34 |
| **Aléatoire uniforme** | 34/28 | — | 20/39 | 47/8 | 27/31 |
| **Aléatoire coordination** | 25/30 | 39/20 | — | 34/11 | 34/18 |
| **Fictitious play** | 1/77 | 8/47 | 11/34 | — | 14/22 |
| **Regret matching** | 34/16 | 31/27 | 18/34 | 22/14 | — |

---

### Carte *mixed-map*
Nombre de joueurs = 34 (17 par équipe)

|   | Têtu | Aléatoire uniforme | Aléatoire coordination | Fictitious play | Regret matching |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Têtu** | — | 29/37 | 39/30 | 39/11 | 40/25 |
| **Aléatoire uniforme** | 37/29 | — | 34/31 | 52/14 | 31/34 |
| **Aléatoire coordination** | 30/39 | 31/34 | — | 38/16 | 28/33 |
| **Fictitious play** | 11/39 | 14/52 | 16/38 | — | 18/53 |
| **Regret matching** | 25/40 | 34/31 | 33/28 | 53/18 | — |



## Conclusion

Les résultats montrent que les stratégies adaptatives sont globalement les plus performantes.  
Les stratégies simples comme aléatoire uniforme et têtu sont souvent battues car elles ne s’adaptent pas au comportement adverse. La stratégie têtue peut être efficace dans certains cas, mais elle reste prévisible.  
La stratégie aléatoire coordination est efficace lorsque le jeu favorise la présence en groupe, mais elle devient vulnérable face à des stratégies plus intelligentes.  
Les stratégies fictitious play et regret matching utilisent l’historique des parties pour s’améliorer.  
Parmi elles, regret matching est la plus robuste car elle apprend progressivement les meilleures décisions.  