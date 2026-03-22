# Rapport de projet

## Groupe
* HADDOUCHI CELINE 
* ALIAOUI BOOCHRA 

## Description des choix importants d'implémentation

La carte est chargée à partir de fichiers JSON représentant différentes configurations : yellow-map, red-map, green-map, blue-map, mixed-map

la fonction ProblemeGrid2D utilise l'algo A* pour calculer le plus court chemin entre la positoin du joueur et celle de la fiole.

La carte est chargée à partir de fichiers JSON représentant différentes configurations :yellow-map, red-map, green-map, blue-map, mixed-map


Les joueurs sont séparés en deux équipes(même nb joueurs) selon leur position initiale sur la carte :
les joueurs sur la ligne du haut → Equipe 0
les joueurs sur la ligne du bas → Equipe 1


À chaque épisode :
Les équipes choisissent des fioles selon leur stratégie.
Les joueurs se déplacent vers les positions choisies.
Le score est calculé.
Les joueurs sont remis à leur position initiale.
Afin d’éviter un avantage pour une équipe, l’ordre de jeu est inversé à chaque épisode :
priority=[0,1] if e % 2 == 0 else [1,0]
Une fois les joueurs positionnés autour des fioles, nous calculons le score de chaque équipe.
La fonction suivante permet de compter combien de joueurs de chaque équipe se trouvent autour d’une fiole :
players_around_item()
les règles de score dépendent du type de carte

## Description des stratégies proposées

Pour changer la stratégie, il faut modifier juste la liste strategie_eq

Stratégie têtue : Si le joueur a déjà un choix (prev_choice), il le refait (reste têtu).
Sinon, il choisit une fiole au hasard et une position libre autour.

Strategie_aleatoire_uniforme : Chaque fois qu’on appelle la stratégie, elle choisit une fiole au hasard et une position libre autour

strategie_aleatoire_coordination : Tous les joueurs de l’équipe choisissent la même fiole.
Chacun prend une position libre différente autour de cette fiole (s’il n’y a plus de positions libres, on choisit une autre position au hasard).

stratégie_fictitious_play : le joueur choisit la fiole la plus visitée par l’adversaire, sinon au hasard si c’est le premier tour.

stratégie_regret_matching: plus une fiole a un regret élevé, plus elle a de chances d’être choisie.

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
