import random

def strategie_tetu(player, items, around_pos_free_func, prev_choice=None, prev_choices=None):
    if prev_choice is not None:
        return prev_choice
    f = random.choice(items)
    pos = random.choice(around_pos_free_func(f.get_rowcol()))
    return (f, pos)

def strategie_aleatoire_uniforme(player, items, around_pos_free_func, prev_choice=None, prev_choices=None):
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