# Rapport de projet

## Groupe
* HADDOUCHI CELINE 
* ALIAOUI BOCHRA 

## Description des choix importants d'implémentation

La carte est chargée à partir de fichiers JSON représentant différentes configurations : yellow-map, red-map, green-map, blue-map, mixed-map.
La fonction ProblemeGrid2D utilise l'algo A* pour calculer le plus court chemin entre la positoin du joueur et celle de la fiole.

Les joueurs sont séparés en deux équipes(même nombre de joueurs) selon leur position initiale sur la carte :
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

## Description des résultats
Comparaison entre les stratégies.  
> Tous les tests expérimentaux ont été réalisés avec 10 épisodes de confrontation (en augmentant le game.fps pour plus de rapidité) et un nombre de joueurs dépendant du type de carte.  
> Score indiqué : score_equipe0/score_equipe1 (équipe0 utilise la stratégie en ligne et l'équipe 1 utilise la stratégie en colonne)

### Carte *yellow-map*
Nombre de joueurs = 16 (donc 8 par équipe) 

|   | Têtu | Aléatoire uniforme | Aléatoire coordination | Fictitious play | Regret matching |
| :--- | :---: | :---: | :---: | :---: | ---: |
| **Têtu** | 20/20 | 19/20 | 40/10 | 30/20 | 34/11
| **Aléatoire uniforme** | 
| **Aléatoire coordination** |
| **Fictitious play** |
| **Regret matching** |


### Carte *red-map*
Nombre de joueurs = 16 (8 par équipe)

|   | Têtu | Aléatoire uniforme | Aléatoire coordination | Fictitious play | Regret matching |
| :--- | :---: | :---: | :---: | :---: | ---: |
| **Têtu** |  |  | |  | 
| **Aléatoire uniforme** | 
| **Aléatoire coordination** |
| **Fictitious play** |
| **Regret matching** |


### Carte *green-map*
Nombre de joueurs =

|   | Têtu | Aléatoire uniforme | Aléatoire coordination | Fictitious play | Regret matching |
| :--- | :---: | :---: | :---: | :---: | ---: |
| **Têtu** |  |  | |  | 
| **Aléatoire uniforme** | 
| **Aléatoire coordination** |
| **Fictitious play** |
| **Regret matching** |

### Carte *blue-map*
Nombre de joueurs =

|   | Têtu | Aléatoire uniforme | Aléatoire coordination | Fictitious play | Regret matching |
| :--- | :---: | :---: | :---: | :---: | ---: |
| **Têtu** |  |  | |  | 
| **Aléatoire uniforme** | 
| **Aléatoire coordination** |
| **Fictitious play** |
| **Regret matching** |

### Carte *mixed-map*
Nombre de joueurs =

|   | Têtu | Aléatoire uniforme | Aléatoire coordination | Fictitious play | Regret matching |
| :--- | :---: | :---: | :---: | :---: | ---: |
| **Têtu** |  |  | |  | 
| **Aléatoire uniforme** | 
| **Aléatoire coordination** |
| **Fictitious play** |
| **Regret matching** |



## Conclusion

Les stratégies adaptatives (fictitious_play et regret_matching) remportent souvent les parties contre les stratégies simples (aleatoire_uniforme, tetu).
La coordination est efficace mais moins constante contre des stratégies adaptatives.
Les stratégies aléatoires simples sont prévisibles et vulnérables sur plusieurs épisodes.