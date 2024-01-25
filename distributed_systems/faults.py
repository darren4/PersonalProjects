import random


FAULTS_ENABLED = False
DEBUG = False


def message_not_sent():
    failure = FAULTS_ENABLED and random.randint(0, 3) == 0
    if DEBUG and failure:
        print("[DEBUG] message not sent")
    return failure


def wait_time_before_kill_process():
    return random.randint(2, 2)
