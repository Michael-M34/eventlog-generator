import simpy
import random

NUM_STUDIOS = 4
NUM_ORDERS = 100

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

# 
def use_fotof(env, fotof_studio, customer):
    start_time = env.now

    with fotof_studio.photographer.request() as request:
        yield request
        yield env.process(fotof_studio.take_photos(True, customer))

    

    with fotof_studio.editor.request() as request:
        yield request
        yield env.process(fotof_studio.edit_photos(True, customer))


def simulate_fotof_studio(env, fotof_studio, orders: list):
    for customer in orders:
        yield env.timeout(1)
        env.process(use_fotof(env, fotof_studio, customer))



def get_num_photographers():
    return 1

def get_num_editors():
    return 1

if __name__ == "__main__":
    # Create environment to be simulated
    env = simpy.Environment()

    # Create the 4 different studios
    fotof_studios = []
    for i in range(NUM_STUDIOS):
        fotof_studios.append(Fotof_studio(env, get_num_photographers(), get_num_editors()))

    # Order ids contains the order ids for each studio
    order_ids = [[],[],[],[]]

    # Give each studio their orders and their ids
    for i in range(NUM_ORDERS):
        order_ids[random.randint(0, (NUM_STUDIOS-1))].append(i+1)


    # Simulate the 4 studios
    for studio_num in range(NUM_STUDIOS):
        print(f"Starting studio: {studio_num+1}\nNum orders: {len(order_ids[studio_num])}")
        env.process(simulate_fotof_studio(env, fotof_studios[studio_num], order_ids[studio_num]))
        env.run()