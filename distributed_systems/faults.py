import random


FAULTS_ENABLED = True
DEBUG = False


def message_not_sent():
    failure = FAULTS_ENABLED and random.randint(0, 4) == 0
    if DEBUG and failure:
        print("[DEBUG] message not sent")
    return failure
