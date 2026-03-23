# -*- coding: utf-8 -*-

# Nicolas, 2026-02-09
from __future__ import absolute_import, print_function, unicode_literals

import random 
import numpy as np
import sys
from itertools import chain


import pygame

from pySpriteWorld.gameclass import Game,check_init_game_done
from pySpriteWorld.spritebuilder import SpriteBuilder
from pySpriteWorld.players import Player
from pySpriteWorld.sprite import MovingSprite
from pySpriteWorld.ontology import Ontology
import pySpriteWorld.glo

from search.grid2D import ProblemeGrid2D
from search import probleme

#-------------------------------
# Stratégies
from strategies import strategie_aleatoire_uniforme, strategie_tetu, strategie_aleatoire_coordination, strategie_fictitious_play, strategie_regret_matching

# Choisir une stratégie pour chaque équipe
strategie_eq = [strategie_fictitious_play, strategie_regret_matching]
# strategie_eq[0] correspond à la stratégie utilisée par l'équipe 0
# strategie_eq[1] correspond à la stratégie utilisée par l'équipe 1

#-------------------------------

# ---- ---- ---- ---- ---- ----
# ---- Main                ----
# ---- ---- ---- ---- ---- ----

game = Game()
name = None
score_total_eq0 = 0
score_total_eq1 = 0

def init(_boardname=None):
    global player,game, name
    name = _boardname if _boardname is not None else 'mixed-map'
    #game = Game('./Cartes/' + name + '.json', SpriteBuilder)
    game = Game('Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 100  # frames per second
    game.mainiteration()
    player = game.player
    
def main():
    global score_total_eq0, score_total_eq1, name

    #for arg in sys.argv:
    #iterations = 40 # nb de pas max par episode
    #if len(sys.argv) == 2:
    #    iterations = int(sys.argv[1])
    #print ("Iterations: ")
    #print (iterations)

    init()
    

    
    #-------------------------------
    # Initialisation
    #-------------------------------
    
    nb_lignes = game.spriteBuilder.rowsize
    nb_cols = game.spriteBuilder.colsize
    assert nb_lignes == nb_cols # a priori on souhaite un plateau carre
    lMin=2  # les limites du plateau de jeu (2 premieres lignes utilisees pour stocker le contour)
    lMax=nb_lignes-2
    cMin=2
    cMax=nb_cols-2
   
    
    players = [o for o in game.layers['joueur']]
    nb_players = len(players)


    items = [o for o in game.layers["ramassable"]]  #
    nb_fioles = len(items)

    nb_episodes = 10


    #-------------------------------
    # Fonctions permettant de récupérer les listes des coordonnées
    # d'un ensemble d'objets ou de joueurs
    #-------------------------------

    def item_states(items):
        # donne la liste des coordonnees des items
        return [o.get_rowcol() for o in items]
    
    def player_states(players):
        # donne la liste des coordonnees des joueurs
        return [p.get_rowcol() for p in players]
    


    #-------------------------------
    # Rapport de ce qui est trouve sut la carte
    #-------------------------------
    print("lecture carte")
    print("-------------------------------------------")
    print('joueurs:', nb_players)
    print("fioles:",nb_fioles)
    print("lignes:", nb_lignes)
    print("colonnes:", nb_cols)
    print("-------------------------------------------")

    #-------------------------------
    # Carte demo yellow
    # 2 x 8 joueurs
    # 5 fioles jaunes
    #-------------------------------

    team = [[], []]  # 2 équipes
    for o in players:
        (x, y) = o.get_rowcol()
        if x == 2:  # les joueurs de team0 sur la ligne du haut
            team[0].append(o)
        elif x == 18:  # les joueurs de team1 sur la ligne du bas
            team[1].append(o)

    assert len(team[0]) == len(team[1])  # on veut un match équilibré donc équipe de même taille
    nb_players_team = int(nb_players / 2)

    init_states = [[],[]]
    # print(teamA)
    init_states[0] = player_states(team[0])

    # print(teamB)
    init_states[1] = player_states(team[1])


    #-------------------------------
    

    #-------------------------------
    # Fonctions definissant les positions legales et placement aléatoire
    #-------------------------------

    def around_pos(pos):
        # donne la liste des positions autour d'une pos (x,y) donnee
        x,y=pos
        return [(x-1,y-1),(x-1,y),(x-1,y+1),(x,y-1),(x,y+1),(x+1,y-1),(x+1,y),(x+1,y+1)]

    def around_pos_free(pos):
        return [pos for pos in around_pos(pos) if legal_position(pos)]

    def busy(pos):
        return around_pos_free(pos) == []

    def legal_position(pos):
        row,col = pos
        # une position legale est dans la carte et pas sur une fiole ni sur un joueur
        return ((pos not in item_states(items)) and (pos not in player_states(players)) and row>lMin and row<lMax-1 and col>=cMin and col<cMax)


    def players_around_item(f):
        """
        :param f: objet fiole
        :return: nombre d'objet de chaque team
        """
        are_here = [0,0]
        pos = f.get_rowcol()
        for i in [0,1]:
            for j in team[i]:
                if j.get_rowcol() in around_pos(pos):
                    are_here[i]+=1
        return are_here

    # -------------------------------
    # ETATS DES STRATEGIES
    # -------------------------------
    # Pour la stratégie têtu, on aura besoin d'une liste de deux dictionnaires qui contiennent les positions pour chaque joueur de l'équipe {player : (fiole,pos)} 
    tetu_etat = [{},{}]

    # Pour la stratégie fictitious play, on aura besoin d'une liste de deux dictionnaires qui contiennent le nombre de visites par l'adversaire pour chaque fiole {fiole : nb_visites_adversaire}
    # Donc fp_etat[0] contient le nombre de visites par fiole de l'équipe 1
    fp_etat = [{},{}]

    # Pour la stratégie regret matching, on aura besoin d'une liste de deux listes de nb_players_team dictionnaires (un pour chaque joueur) qui contiennent le regret cumulé pour chaque fiole {fiole : regret_cumule}
    rm_etat = [[{} for _ in range(nb_players_team)] for _ in range(2)]

    # Pour mettre à jour les regrets et le nombre de visites de chaque fiole par chaque équipe, il faut une liste de deux listes (choix) et un dictionnaire (pour les scores à chaque fiole)
    # choix_etats = [[],[]]
    # scores_etats = {}  # On aura {fiole : (pts_eq0, pts_eq1)}

    # -------------------------------
    # EPISODES
    # -------------------------------

    for e in range(nb_episodes):
        priority=[0,1] if e % 2 == 0 else [1,0] # ordre de priorité inversé à chaque épisode

        # Si ce n'est pas le premier épisode, il faut mettre à jour les états pour les stratégies fictitious play et regret matching
        if e > 0:
            for t in [0,1]: # Pour chaque équipe
                adversaire = 1 - t
                # Fictitious play -> on doit mettre à jour le nombre de visites pour les fioles de l'équipe adverse
                if strategie_eq[t].__name__ == "strategie_fictitious_play":
                    for fiole_advers in choix_fiole[adversaire]:  # Pour chaque fiole visitée par l'équipe adversaire, on incrémente le compteur de visites
                        fp_etat[t][fiole_advers] = fp_etat[t].get(fiole_advers, 0) + 1

                # Regret matching : calculer et cumuler les regrets
                if strategie_eq[t].__name__ == "strategie_regret_matching":
                    for p in range(nb_players_team):  # Pour chaque joueur de l'équipe t
                        fiole_p = choix_fiole[t][p]   # On récupère la fiole jouée par le joueur p dans l'équipe t à l'épisode précédent
                        score_obtenu = scores_etats.get(fiole_p, (0,0))[t]  # On récupère le score obtenu du joueur p dans l'équipe t à l'épisode précédent
                        for f in items:
                            score_hypothese = scores_etats.get(f, (0,0))[t]  # Calcul du score qu'on aurait pu avoir en allant sur la fiole f
                            regret = max(0.0, score_hypothese - score_obtenu)   # Calcul du regret de n'avoir pas joué la fiole f
                            rm_etat[t][p][f] = rm_etat[t][p].get(f, 0.0) + regret   # Stockage du regret cumulé du joueur p de l'équipe t de n'avoir pas joué la fiole f 

        # Chaque équipe va choisir sa position et sa fiole cible simultanément
        choix_fiole = [[],[]]
        choix_pos = [[],[]]

        for t in [0,1]:
            nom = strategie_eq[t].__name__
            print(f"Team {t} utilise la stratégie : {nom}")
            
            # Selon la stratégie, on va faire appel à la fonction avec les bons arguments
            if nom == "strategie_tetu":
                for p in range(nb_players_team):
                    f, pos = strategie_eq[t](team[t][p], items, around_pos_free, prev_choices=tetu_etat[t])
                    choix_fiole[t].append(f)
                    choix_pos[t].append(pos)

            elif nom == "strategie_aleatoire_uniforme":
                for p in range(nb_players_team):
                    f, pos = strategie_eq[t](team[t][p], items, around_pos_free)
                    choix_fiole[t].append(f)
                    choix_pos[t].append(pos)

            elif nom == "strategie_aleatoire_coordination":
                choix = strategie_eq[t](team[t], items, around_pos_free)
                for f, pos in choix:
                    choix_fiole[t].append(f)
                    choix_pos[t].append(pos)
            
            elif nom == "strategie_fictitious_play":
                for p in range(nb_players_team):
                    f, pos = strategie_eq[t](team[t][p], items, around_pos_free, prev_choices_adv=fp_etat[t])
                    choix_fiole[t].append(f)
                    choix_pos[t].append(pos)
            
            elif nom == "strategie_regret_matching":
                for p in range(nb_players_team):
                    f, pos = strategie_eq[t](team[t][p], items, around_pos_free, regrets=rm_etat[t][p])
                    choix_fiole[t].append(f)
                    choix_pos[t].append(pos)

        # -------------------------------
        # DEPLACEMENTS VERS LES POSITIONS ET FIOLES CIBLES
        # -------------------------------

        for t in priority:
            print("Team ",t)
            path = []
            for p in range(nb_players_team):
                pos_player = team[t][p].get_rowcol()
                pos_cible = choix_pos[t][p]
                fiole_cible = choix_fiole[t][p]
                print("Player ", p, " starting from ", pos_player, " going to potion ", fiole_cible.get_rowcol(), " at ", pos_cible)

                # -------------------------------
                # calcul A* pour le joueur
                # -------------------------------

                g = np.ones((nb_lignes, nb_cols), dtype=bool)  # une matrice remplie par defaut a True
                for i in range(nb_lignes):  # on exclut aussi les bordures du plateau
                    g[0][i] = False
                    g[1][i] = False
                    g[nb_lignes - 1][i] = False
                    g[nb_lignes - 2][i] = False
                    g[i][0] = False
                    g[i][1] = False
                    g[i][nb_lignes - 1] = False
                    g[i][nb_lignes - 2] = False
                prob = ProblemeGrid2D(pos_player, pos_cible, g, 'manhattan')
                path.append(probleme.astar(prob, verbose=False))
                print("Chemin trouvé:", path[p])

                #-------------------------------
                # Boucle principale de déplacements
                #-------------------------------
                # on fait bouger le joueur jusqu'à son but
                # en suivant le chemin trouve avec A*

                for i in range(len(path[p])):  # si le joueur n'est pas deja arrive
                    (row, col) = path[p][i]
                    team[t][p].set_rowcol(row, col)
                    print("pos joueur:",row, col)

                    # mise à jour du plateau de jeu
                    game.mainiteration()


        # -------------------------------
        # CALCUL DES SCORES
        # -------------------------------

        # Calcul du nombre de joueurs autour de chaque fiole
        for o in items:
            print(players_around_item(o))

        # Calcul des points
        liste_fioles = list() # Liste des tuples (nb_joueurs_eq0, nb_joueurs_eq1) pour chaque fiole
        score_eq0 = 0
        score_eq1 = 0
        for o in items:
            liste_fioles.append(players_around_item(o))

        # S'il y a égalité après vérification des conditions, aucune équipe ne prend le point
        if name == "yellow-map":    # Map avec seulement des fioles jaunes
            for nb_eq0, nb_eq1 in liste_fioles:
                if nb_eq0 < 1 :
                    if nb_eq1 >= 1:
                        score_eq1 += 1
                elif nb_eq1 < 1:
                    score_eq0 += 1
                elif nb_eq0 > nb_eq1:
                    score_eq0 += 1
                elif nb_eq1 > nb_eq0:
                    score_eq1 += 1
        elif name == "red-map":     # Map avec seulement des fioles rouges
            for nb_eq0, nb_eq1 in liste_fioles:
                cond0 = nb_eq0 >= 2
                cond1 = nb_eq1 >= 2
                if cond0 and cond1:
                    if nb_eq0 > nb_eq1:
                        score_eq0 += 1
                    elif nb_eq1 > nb_eq0:
                        score_eq1 += 1
                elif cond0:
                    score_eq0 += 1
                elif cond1:
                    score_eq1 += 1
        elif name == "green-map":   # Map avec seulement des fioles vertes
            for nb_eq0, nb_eq1 in liste_fioles:
                total = nb_eq0 + nb_eq1
                if total >= 3:
                    if nb_eq0 > nb_eq1:
                        score_eq0 += 1
                    elif nb_eq1 > nb_eq0:
                        score_eq1 += 1
        elif name == "blue-map":    # Map avec seulement des fioles bleues
            for nb_eq0, nb_eq1 in liste_fioles:
                cond0 = nb_eq0 >= 2
                cond1 = nb_eq1 >= 2
                if nb_eq0 == 1 and cond1:
                    score_eq0 += 1
                elif nb_eq1 == 1 and cond0:
                    score_eq1 += 1
                elif cond0 and cond1:
                    if nb_eq0 > nb_eq1:
                        score_eq0 += 1
                    elif nb_eq1 > nb_eq0:
                        score_eq1 += 1
                elif cond0:
                    score_eq0 += 1
                elif cond1:
                    score_eq1 += 1
        elif name == "mixed-map":
            couleurs_mixed = ["yellow", "green", "yellow", "red", "blue", "red", "yellow", "green", "yellow"]  # On stocke l'ordre des couleurs des fioles dans une liste
            for i, (nb_eq0, nb_eq1) in enumerate(liste_fioles):
                couleur_fiole = couleurs_mixed[i]
                if couleur_fiole == "yellow":
                    if nb_eq0 < 1 :
                        if nb_eq1 >= 1:
                            score_eq1 += 1
                    elif nb_eq1 < 1:
                        score_eq0 += 1
                    elif nb_eq0 > nb_eq1:
                        score_eq0 += 1
                    elif nb_eq1 > nb_eq0:
                        score_eq1 += 1
                elif couleur_fiole == "red":
                    cond0 = nb_eq0 >= 2
                    cond1 = nb_eq1 >= 2
                    if cond0 and cond1:
                        if nb_eq0 > nb_eq1:
                            score_eq0 += 1
                        elif nb_eq1 > nb_eq0:
                            score_eq1 += 1
                    elif cond0:
                        score_eq0 += 1
                    elif cond1:
                        score_eq1 += 1
                elif couleur_fiole == "green":
                    total = nb_eq0 + nb_eq1
                    if total >= 3:
                        if nb_eq0 > nb_eq1:
                            score_eq0 += 1
                        elif nb_eq1 > nb_eq0:
                            score_eq1 += 1
                elif couleur_fiole == "blue":
                    cond0 = nb_eq0 >= 2
                    cond1 = nb_eq1 >= 2
                    if nb_eq0 == 1 and cond1:
                        score_eq0 += 1
                    elif nb_eq1 == 1 and cond0:
                        score_eq1 += 1
                    elif cond0 and cond1:
                        if nb_eq0 > nb_eq1:
                            score_eq0 += 1
                        elif nb_eq1 > nb_eq0:
                            score_eq1 += 1
                    elif cond0:
                        score_eq0 += 1
                    elif cond1:
                        score_eq1 += 1

        print(f" Score épisode {e} == Eq0 : {score_eq0} | Eq1 : {score_eq1}")
        score_total_eq0 += score_eq0
        score_total_eq1 += score_eq1

        # -------------------------------
        # SAUVEGARDE DES CHOIX ET DES SCORES DE CHAQUE EQUIPE
        # -------------------------------
        # Après chaque épisode, il faut sauvegarder les choix et les scores pour les utiliser dans les stratégies de regret_matching et fictitious play au prochain épisode
        choix_etats = [list(choix_fiole[0]), list(choix_fiole[1])]
        scores_etats = {}

        for i, o in enumerate(items):
            nb_eq0, nb_eq1 = liste_fioles[i]
            # On va recalculer les points pour chaque fiole individuellement pour le regret-matching
            # On va donc reprendre la même logique que pour le calcul de scores
            pts0, pts1 = 0, 0
            couleur = "yellow"
            if name == "yellow-map": couleur = "yellow"
            elif name == "green-map": couleur = "green"
            elif name == "blue-map": couleur = "blue"
            elif name == "red-map": couleur = "red"
            elif name == "mixed-map":
                couleurs_mixed = ["yellow", "green", "yellow", "red", "blue", "red", "yellow", "green", "yellow"]
                couleur = couleurs_mixed[i]
            
            if couleur == "yellow":
                if nb_eq0 < 1 :
                    if nb_eq1 >= 1:
                        pts1 = 1
                elif nb_eq1 < 1:
                    pts0 = 1
                elif nb_eq0 > nb_eq1:
                    pts0 = 1
                elif nb_eq1 > nb_eq0:
                    pts1 = 1
            elif couleur == "red":
                cond0, cond1 = nb_eq0 >= 2, nb_eq1 >= 2
                if cond0 and cond1:
                    if nb_eq0 > nb_eq1:
                        pts0 = 1
                    elif nb_eq1 > nb_eq0:
                        pts1 = 1
                elif cond0:
                    pts0 = 1
                elif cond1:
                    pts1 = 1
            elif couleur == "green":
                total = nb_eq0 + nb_eq1
                if total >= 3:
                    if nb_eq0 > nb_eq1:
                        pts0 = 1
                    elif nb_eq1 > nb_eq0:
                        pts1 = 1
            elif couleur == "blue":
                cond0, cond1 = nb_eq0 >= 2, nb_eq1 >= 2
                if nb_eq0 == 1 and cond1:
                    pts0 = 1
                elif nb_eq1 == 1 and cond0:
                    pts1 = 1
                elif cond0 and cond1:
                    if nb_eq0 > nb_eq1:
                        pts0 = 1
                    elif nb_eq1 > nb_eq0:
                        pts1 = 1
                elif cond0:
                    pts0 = 1
                elif cond1:
                    pts1 = 1
            # On le stocke donc comme valeur de la fiole correspondante
            scores_etats[o] = (pts0, pts1)

        # Remettre les joueurs à leur position initiale a la fin de l'episode
        for i in [0,1]:
            j=0
            for p in team[i]:
                x,y = init_states[i][j]
                p.set_rowcol(x,y)
                j+=1

    print(f"Score final -> Eq0 : {score_total_eq0}  | Eq1 : {score_total_eq1}")
    if score_total_eq0 > score_total_eq1:
        print("Gagnant : Equipe 0 !")
    elif score_total_eq1 > score_total_eq0:
        print("Gagnant : Equipe 1 !")
    else:
        print("Egalité entre les deux équipes 0 et 1 !")

    pygame.quit()

    
    #-------------------------------

    
   

if __name__ == '__main__':
    main()
    


