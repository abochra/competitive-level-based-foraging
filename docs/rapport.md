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


À chaque épisode :
1. Les équipes choisissent des fioles selon leur stratégie.  
2. Les joueurs se déplacent vers les positions choisies.  
3. Le score est calculé.  
4. Les joueurs sont remis à leur position initiale.  

Afin d’éviter un avantage pour une équipe, l’ordre de jeu est inversé à chaque épisode avec la ligne de code :  
`priority=[0,1] if e % 2 == 0 else [1,0]`

Une fois les joueurs positionnés autour des fioles, nous calculons le score de chaque équipe.  
La fonction suivante permet de compter combien de joueurs de chaque équipe se trouvent autour d’une fiole :
*players_around_item()*  
Les règles de score dépendent du type de carte.

## Description des stratégies proposées

Pour changer la stratégie d'une équipe, il faut juste modifier la liste strategie_eq

**Stratégie têtue :** Le joueur refait le même choix indéfiniment en le mémorisant (reste têtu).
S'il n'a pas de choix mémorisé, il choisit une fiole au hasard et une position libre autour.

**Strategie_aleatoire_uniforme :** Chaque fois qu’on appelle la stratégie, elle choisit une fiole au hasard et une position libre autour.

**Strategie_aleatoire_coordination :** Tous les joueurs de l’équipe choisissent la même fiole.
Chacun prend une position libre différente autour de cette fiole (s’il n’y a plus de positions libres, on choisit une autre position au hasard sur une autre fiole).

**Stratégie_fictitious_play :** Le joueur choisit la fiole la moins visitée par l’adversaire, sinon au hasard si c’est le premier tour.

**Stratégie_regret_matching:** Plus une fiole a un regret élevé, plus elle a de chances d’être choisie par le joueur.

## Description des résultats
Comparaison entre les stratégies. Bien indiquer les cartes utilisées.


Équipe 0 = team[0] = stratégie dans strategie_eq[0]
Équipe 1 = team[1] = stratégie dans strategie_eq[1]



Test1 : strategie_eq = [strategie_aleatoire_uniforme, strategie_tetu]
Score final -> Eq0 : 4  | Eq1 : 6
Gagnant : Equipe 1 !

Test2 : strategie_eq = [strategie_aleatoire_uniforme, strategie_aleatoire_coordination]
Score final -> Eq0 : 12  | Eq1 : 6
Gagnant : Equipe 0 !

Test3 : strategie_eq = [strategie_aleatoire_uniforme, strategie_fictitious_play]
Score final -> Eq0 : 4  | Eq1 : 11
Gagnant : Equipe 1 


Tst4 : strategie_eq = [strategie_aleatoire_uniforme, strategie_regret_matching]
Score final -> Eq0 : 4  | Eq1 : 6
Gagnant : Equipe 1 !


Test5 : strategie_eq = [strategie_tetu, strategie_aleatoire_coordination]
Score final -> Eq0 : 7  | Eq1 : 6
Gagnant : Equipe 0 !

Test 6 : strategie_eq = [strategie_tetu, strategie_fictitious_play]
Score final -> Eq0 : 6  | Eq1 : 9
Gagnant : Equipe 1 !

Test 7 : strategie_eq = [strategie_tetu, strategie_regret_matching]
Score final -> Eq0 : 7  | Eq1 : 6
Gagnant : Equipe 0 !


Test 8 : strategie_eq = [strategie_aleatoire_coordination, strategie_fictitious_play]
Score final -> Eq0 : 5  | Eq1 : 6
Gagnant : Equipe 1 !


Test 9 : strategie_eq = [strategie_aleatoire_coordination, strategie_regret_matching]
Score final -> Eq0 : 7  | Eq1 : 8
Gagnant : Equipe 1 !

Test 10 : strategie_eq = [strategie_fictitious_play, strategie_regret_matching]
Score final -> Eq0 : 6  | Eq1 : 5
Gagnant : Equipe 0 !

Les stratégies adaptatives (fictitious_play et regret_matching) remportent souvent les parties contre les stratégies simples (aleatoire_uniforme, tetu).
La coordination est efficace mais moins constante contre des stratégies adaptatives.
Les stratégies aléatoires simples sont prévisibles et vulnérables sur plusieurs épisodes.
