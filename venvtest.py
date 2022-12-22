import simpy
import random
from generate_events import *

import csv

NUM_STUDIOS = 1
NUM_ORDERS = 100

NUM_EDITORS = 2

class Fotof_studio(object):
    """
    Fotof studio class:

    Contains the resources required to complete the eventlog:
    - photographers
    - editors
    """
    def __init__(self, env, num_photographers, num_editors):
        self.env = env 
        self.photographer = simpy.Resource(env, num_photographers)
        self.editor = simpy.Resource(env, num_editors)

    def take_photos(self, in_studio: bool, customer):
        yield self.env.timeout(random.randint(1,3))

    def edit_photos(self, in_studio: bool, customer):
        yield self.env.timeout(random.randint(3,4))

# HELPER FUNCTIONS 

def get_num_photographers():
    return random.randint(3,4)

def get_studio_or_location(is_personal):
    if not(is_personal):
        return 1
    else:
        if generate_outcome(PERSONAL_ON_LOCATION) == ON_LOCATION:
            return 1
        else:
             return 0


# Simulate the use of a fotof studio for a single customer
def use_fotof(env, fotof_studio, customer, writer):
    
    is_personal = generate_outcome(PERSONAL_OR_CORPORATE)



    with fotof_studio.photographer.request() as request:
        yield request
        yield env.process(fotof_studio.take_photos(True, customer))

    

    with fotof_studio.editor.request() as request:
        yield request
        yield env.process(fotof_studio.edit_photos(True, customer))


# Simulate the operation of the entire fotof studio for a list of orders
def simulate_fotof_studio(env, fotof_studio, orders: list, writer):
    for customer in orders:
        yield env.timeout(1)
        env.process(use_fotof(env, fotof_studio, customer, writer))


if __name__ == "__main__":
    # Create environment to be simulated
    env = simpy.Environment()

    # Create the different studios
    fotof_studios = []
    for i in range(NUM_STUDIOS):
        fotof_studios.append(Fotof_studio(env, get_num_photographers(), NUM_EDITORS))

    # Order ids contains the order ids for each studio
    order_ids = [[] for _ in range(NUM_STUDIOS)]

    # Give each studio their orders and their ids
    for i in range(NUM_ORDERS):
        order_ids[random.randint(0, (NUM_STUDIOS-1))].append(i+1)

    with open('eventlog.csv', 'w') as file:
        writer = csv.writer(file)

        # Simulate the studios
        for studio_num in range(NUM_STUDIOS):
            print(f"Starting studio: {studio_num+1}\nNum orders: {len(order_ids[studio_num])}")
            env.process(simulate_fotof_studio(env, fotof_studios[studio_num], order_ids[studio_num], writer))
            env.run()

        file.close()