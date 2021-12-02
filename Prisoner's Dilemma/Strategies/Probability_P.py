import random

def strategy(history, memory):
    p = 0.75
    choice = random.uniform(0,1)
    if choice < p:
        return 0, None
    else:
        return 1, None