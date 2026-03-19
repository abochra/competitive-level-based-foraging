import random

def strategie_tetu(player, items, around_pos_free_func, prev_choices=None):
    """
    prev_choices : dictionnaire {id(player): (fiole, pos)} mémorisé entre les épisodes
    Si le joueur a déjà un choix mémorisé, on le réutilise sinon on tire au hasard et on mémorise la (fiole,pos) tiré
    """
    if prev_choices is None:
        prev_choices = {}
    # Si le joueur a déjà un choix mémorisé, on le joue
    if player in prev_choices:
        return prev_choices[player]
    
    # Si on a toujours pas de position et de fiole pour ce joueur, on choisit au hasard et on le stocke dans le dictionnaire      
    f = random.choice(items)
    pos = random.choice(around_pos_free_func(f.get_rowcol()))
    prev_choices[player] = (f,pos)
    return (f, pos)

def strategie_aleatoire_uniforme(player, items, around_pos_free_func, prev_choices=None):
    """
    Ne mémorise pas les choix de chaque joueur, tire aléatoirement parmi toutes les fioles à chaque épisode
    """
    f = random.choice(items)
    pos = random.choice(around_pos_free_func(f.get_rowcol()))
    return (f, pos)

def strategie_aleatoire_coordination(team_players, items, around_pos_free_func, prev_choices=None):
    f = random.choice(items)
    positions = around_pos_free_func(f.get_rowcol())
    choix = []
    for p in team_players:
        if positions:
            pos = positions.pop(0)
        else:
            pos = random.choice(around_pos_free_func(f.get_rowcol()))
        choix.append((f, pos))
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
        # choisir la fiole la plus souvent visitée par l'adversaire
        max_visits = max(prev_choices.values())
        candidates = [item for item in items if prev_choices.get(item, 0) == max_visits]
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
        # pondération selon les regrets (plus le regret est élevé, plus on a de chance de choisir cette fiole)
        total_regret = sum(regrets.values())
        if total_regret == 0:
            f = random.choice(items)
        else:
            r = random.uniform(0, total_regret)
            cumulative = 0
            for item in items:
                cumulative += regrets.get(item, 0)
                if r <= cumulative:
                    f = item
                    break
    
    pos = random.choice(around_pos_free_func(f.get_rowcol()))
    return (f, pos)