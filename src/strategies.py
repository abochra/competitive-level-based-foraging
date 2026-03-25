import random
import math

def strategie_tetu(player, items, around_pos_free_func, prev_choices=None):
    """
    Stratégie têtu : Le joueur choisit une fiole et une position au hasard au premier épisode et garde son choix mémorisé.
    Prend en arguments :
     - player -> joueur courant 
     - items -> liste des fioles disponibles
     - around_pos_free_func -> fonction déterminant les positions libres autour d'une fiole donnée
     - prev_choices -> dictionnaire {player: (fiole, pos)} partagé entre les joueurs d'une même équipe et mémorisé entre les épisodes par main.py
    Retourne un tuple (f, pos) : une fiole et une position attribuées au joueur
    """
    if prev_choices is None: # Dictionnaire toujours pas initialisé
        prev_choices = {}

    # Si le joueur a déjà un choix mémorisé, on le joue sans vérification de la position libre dans la carte car on doit respecter l'hypothèse de simultanéité, les conflits de positions seront gérés par le main
    if player in prev_choices:
        return prev_choices[player]
    
    # Si on a toujours pas de position et de fiole pour ce joueur, on choisit au hasard et on le stocke dans le dictionnaire      
    f = random.choice(items)  # Choisit au hasard une fiole
    pos = random.choice(around_pos_free_func(f.get_rowcol()))  # Choisit au hasard une position autour de la fiole f
    prev_choices[player] = (f,pos)   # Stocke le choix dans le dictionnaire pour le joueur concerné
    return (f, pos)

def strategie_aleatoire_uniforme(player, items, around_pos_free_func, prev_choices=None):
    """
    Stratégie aléatoire uniforme : Ne mémorise pas les choix de chaque joueur, tire aléatoirement parmi toutes les fioles à chaque épisode, indépendamment des épisodes précédents.
    Prend en arguments :
     - player -> joueur courant 
     - items -> liste des fioles disponibles
     - around_pos_free_func -> fonction déterminant les positions libres autour d'une fiole donnée
     - prev_choices -> dictionnaire {player: (fiole, pos)} partagé entre les joueurs d'une même équipe et mémorisé entre les épisodes par main.py
    Retourne un tuple (f, pos) : une fiole et une position attribuées au joueur
    """
    f = random.choice(items)  # Choisit au hasard une fiole
    pos = random.choice(around_pos_free_func(f.get_rowcol()))  # Choisit au hasard une position autour de la fiole f
    return (f, pos)

def strategie_aleatoire_coordination(team_players, items, around_pos_free_func, prev_choices=None):
    """
    Stratégie aléatoire coordination : Toute l'équipe choisit la même fiole et se disperse autour de celle-ci pour maximiser les chances de gagner autour de cette fiole. Si les cases sont toutes occupées autour de cette fiole, ils vont sur une autre.
    Prend en arguments :
     - team_players -> joueurs de l'équipe courante
     - items -> liste des fioles disponibles
     - around_pos_free_func -> fonction déterminant les positions libres autour d'une fiole donnée
     - prev_choices -> dictionnaire {player: (fiole, pos)} partagé entre les joueurs d'une même équipe et mémorisé entre les épisodes par main.py
    Retourne une liste de tuple (f, pos) : une fiole et une position attribuées à chaque joueur de cette équipe
    """
    f = random.choice(items)
    positions_libres = around_pos_free_func(f.get_rowcol())  # Positions libres autour de la fiole f
    choix = []   # Choix de positions et de fiole pour chaque joueur de cette équipe
    positions_attribuees = []   # Liste des positions déjà attribuées aux joueurs de cette équipe
    for p in team_players:
        positions_dispos = [pos for pos in positions_libres if pos not in positions_attribuees]   # Positions disponibles pour les joueurs restants de l'équipe
        if positions_dispos:
            pos = positions_dispos.pop(0)
            positions_attribuees.append(pos)
            choix.append((f, pos))
        else:       # S'il n'y a plus de positions disponibles autour de la fiole f alors on choisit une autre fiole au hasard
            autre_fioles = [fiole for fiole in items if fiole != f]
            fi = random.choice(autre_fioles)
            pos = random.choice(around_pos_free_func(fi.get_rowcol()))
            choix.append((fi, pos))
    return choix


def strategie_fictitious_play(player, items, around_pos_free_func, prev_choices_adv=None):
    """
    Stratégie fictitious play : Stratégie best-response basée sur l'historique de choix de l'adversaire. Un joueur va aller sur la fiole la moins visitée par l'équipe adverse pour maximiser ses chances de gagner la fiole.
    Prend en arguments :
     - player -> joueur courant 
     - items -> liste des fioles disponibles
     - around_pos_free_func -> fonction déterminant les positions libres autour d'une fiole donnée
     - prev_choices_adv -> dictionnaire {fiole: nombre_de_visites_par_adversaire} partagé entre les joueurs d'une même équipe en mémorisant les choix de l'équipe adverse (mise à jour à chaque épisode par main.py)
    Retourne un tuple (f, pos) : une fiole et une position attribuées au joueur
    """
    if prev_choices_adv is None or len(prev_choices_adv) == 0:
        # Premier tour : on choisit aléatoirement
        f = random.choice(items)
    else:
        # Les autres tours, on choisit la fiole la moins souvent visitée par l'adversaire et donc gagner des points sur cette fiole
        min_visits = min(prev_choices_adv.get(item, 0) for item in items)  # On récupère le nombre minimum de visites sur une fiole qui existe
        candidates = [item for item in items if prev_choices_adv.get(item, 0) == min_visits]  # On stocke dans une liste les fioles qui ont été visités min_visits fois
        f = random.choice(candidates)   # On choisit aléatoirement une fiole qui a été visité le moins de fois
    
    pos = random.choice(around_pos_free_func(f.get_rowcol()))
    return (f, pos)

def strategie_regret_matching(player, items, around_pos_free_func, regrets=None):
    """
    Stratégie regret matching : Stratégie best-response basée sur les regrets cumulés pour chaque fiole pour chaque joueur. On joue, pour un joueur, chaque fiole avec une probabilité proportionnelle à son regret cumulé positif.
    Cela signifie qu'on va positionner le joueur sur une fiole qu'il aurait dû jouer pour avoir un score plus élevé.
    Prend en arguments :
     - player -> joueur courant 
     - items -> liste des fioles disponibles
     - around_pos_free_func -> fonction déterminant les positions libres autour d'une fiole donnée
     - regrets -> dictionnaire {fiole: score_regret_cumule} propre à chaque joueur (on va mettre à jour le regret cumulé après chaque épisode dans le main.py)
    Retourne un tuple (f, pos) : une fiole et une position attribuées au joueur
    """
    if regrets is None or len(regrets) == 0:
        # Premier tour : choix aléatoire
        f = random.choice(items)
    else:
        # On ne garde que les regrets positifs 
        regrets_pos = {item:max(0.0, regrets.get(item, 0.0)) for item in items}
        total_regret = sum(regrets_pos.values())

        if total_regret == 0:
            # Tous les regrets sont nuls : aucune fiole n'est favorisée donc on tire une fiole aléatoirement pour la jouer
            f = random.choice(items)
        else:
            # Tirage aléatoire pondéré par les regrets : plus le regret est élevé, plus on a de chance de choisir cette fiole
            # Chaque fiole a une proba regret(fiole) / total_regret d'être choisie
            r = random.uniform(0, total_regret)  # Seuil r tiré aléatoirement entre [0, total_regret]
            cumulative = 0
            f = items[-1] # Valeur par défaut si on ne sort pas de la boucle
            # On parcourt les fioles en cumulant les probabilités jusqu'à dépasser le seuil r 
            for item in items:
                cumulative += regrets_pos.get(item, 0)
                if r <= cumulative:
                    f = item
                    break
    
    pos = random.choice(around_pos_free_func(f.get_rowcol()))  # Choix d'une position libre autour de la fiole f
    return (f, pos)


def strategie_UCB(player, items, around_pos_free_func, ucb_etat = None, t=0):
    """
    Stratégie UCB (Upper Confidence Bound) : apprentissage par renforcement, sélection déterministe de la fiole avec le meilleur score UCB avec la formule : wins/visits + sqrt(log(t)/visits)
    On commence d'abord par explorer les fioles puis par les exploiter (notamment aller vers la fiole avec le meilleur score UCB)
    Prend en arguments :
     - player -> joueur courant 
     - items -> liste des fioles disponibles
     - around_pos_free_func -> fonction déterminant les positions libres autour d'une fiole donnée
     - ucb_etat -> dictionnaire {fiole: {'wins' : int, 'visits' : int}} propre à chaque joueur mis à jour par main.py
     - t -> nombre total d'itérations (épisodes ici)
    Retourne un tuple (f, pos) : une fiole et une position attribuées au joueur
    """
    if ucb_etat is None: 
        ucb_etat = {}
    
    # On initialise le dictionnaire au premier appel
    for item in items:
        if item not in ucb_etat:
            ucb_etat[item] = {'wins': 0, 'visits': 0}
    
    # On explore chaque fiole au moins une fois
    non_visitees = [item for item in items if ucb_etat[item]['visits'] == 0]  # Liste des fioles jamais visitées
    if non_visitees:  # S'il reste encore des fioles jamais visitées
        f = random.choice(non_visitees)
    else:  # Si on a exploré toutes les fioles, on va choisir la fiole avec le meilleur score UCB
        max_score = float('-inf')
        best_fiole = None
        for item in items:
            w = ucb_etat[item]['wins']   # On récupère le nombre de fois qu'on a gagné sur cette fiole
            v = ucb_etat[item]['visits']   # On récupère le nombre de fois qu'on a visité cette fiole
            score = w / v + math.sqrt(math.log(t + 1)/ v)  # Calcul du score UCB (log(t + 1) pour éviter d'avoir log(0))
            if score > max_score:  # Si le score calculé est supérieur au score max, on a une nouvelle meilleure fiole
                max_score = score
                best_fiole = item
        f = best_fiole
    
    pos = random.choice(around_pos_free_func(f.get_rowcol()))  # Choix d'une position libre autour de la fiole f
    return (f, pos)
