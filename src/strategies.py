import random

def strategie_tetu(player, items, around_pos_free_func, prev_choices=None):
    """
    Stratégie têtu : Le joueur choisit une fiole et une position au hasard au premier épisode et garde son choix mémorisé.
    Prend en arguments :
     - player -> joueur courant 
     - items -> liste des fioles disponibles
     - around_pos_free_func -> fonction déterminant les positions libres autour d'une fiole donnée
     - prev_choices -> dictionnaire {id(player): (fiole, pos)} partagé entre les joueurs d'une même équipe et mémorisé entre les épisodes par main.py
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
     - prev_choices -> dictionnaire {id(player): (fiole, pos)} partagé entre les joueurs d'une même équipe et mémorisé entre les épisodes par main.py
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
     - prev_choices -> dictionnaire {id(player): (fiole, pos)} partagé entre les joueurs d'une même équipe et mémorisé entre les épisodes par main.py
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


def strategie_fictitious_play(player, items, around_pos_free_func, prev_choices=None):
    """
    player : le joueur courant
    items : liste des fioles
    around_pos_free_func : fonction pour avoir les positions libres autour
    prev_choices : dictionnaire {item_id: nombre_de_visites}
    """
    if prev_choices is None or len(prev_choices) == 0:
        # premier tour : choisir aléatoirement
        f = random.choice(items)
    else:
        # choisir la fiole la moins souvent visitée par l'adversaire et donc gagner des points sur cette fiole
        min_visits = min(prev_choices.get(item, 0) for item in items)
        candidates = [item for item in items if prev_choices.get(item, 0) == min_visits]
        f = random.choice(candidates)
    
    pos = random.choice(around_pos_free_func(f.get_rowcol()))
    return (f, pos)

def strategie_regret_matching(player, items, around_pos_free_func, regrets=None):
    """
    regrets : dictionnaire {item_id: score_regret}
    """
    if regrets is None or len(regrets) == 0:
        # premier tour : aléatoire
        f = random.choice(items)
    else:
        regrets_pos = {item:max(0.0, regrets.get(item, 0.0)) for item in items}
        # pondération selon les regrets (plus le regret est élevé, plus on a de chance de choisir cette fiole)
        total_regret = sum(regrets_pos.values())
        if total_regret == 0:
            f = random.choice(items)
        else:
            r = random.uniform(0, total_regret)
            cumulative = 0
            f = items[-1] # Valeur par défaut
            for item in items:
                cumulative += regrets.get(item, 0)
                if r <= cumulative:
                    f = item
                    break
    
    pos = random.choice(around_pos_free_func(f.get_rowcol()))
    return (f, pos)