import random

def generate_event(events: list) -> int:
    value = random.random()

    if sum([x[1] for x in events]) != 1:
        raise ValueError

    for i in range(len(events)):
        if value < sum([event[1] for event in events[0:i+1]]):
            return events[i][0]

    return -1
