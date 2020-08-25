def get_reward(res):
    # reward = 0
    if res.name == 'Victory':
        return 1
    elif res.name == 'Defeat':
        return -1
    else:
        return 0
