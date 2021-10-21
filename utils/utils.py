# Tutti gli usi di random sono incapsulati in questo file
# nel caso ci fosse la necessità di cambiare fonte randmom
import random


# Return True with a probability of prob
def probability_boolean(prob):
    return random.random() < prob


# Trova tuttle le sottosequenze di una sub-stringa in un'altra stringa


def find_all(a_str, sub):
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1:
            return
        yield start
        start += len(sub)  # use start += 1 to find overlapping matches


def randint(a, b):
    return random.randint(a, b)


def shuffle(lst):
    random.shuffle(lst)


def random_choice(lst):
    return random.choice(lst)


def weighted_choice(choice_dict):
    # L'input è un dizionario dove ogni chiave è associata ad un peso intero
    min = 0
    max = sum(choice_dict.values())
    randNumber = randint(min, max)
    choice = None
    keys = iter(list(choice_dict.keys()))
    while choice == None:
        current = next(keys)
        randNumber -= choice_dict[current]
        if (randNumber <= 0):
            choice = current
    return current


def find_all(a_str: str, sub: str) -> int:
    """ Ritorna tutte le iterazioni di una sottostringa all'interno di una stringa"""
    start = 0
    while True:
        start = a_str.find(sub, start)
        if start == -1:
            return
        yield start
        start += len(sub)
