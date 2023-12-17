import random


FAULTS_ENABLED = False

def message_not_sent():
    return FAULTS_ENABLED and random.randint(0, 4) == 0