import simpy
import random

class Fotof_studio(object):
    def __init__(self, env, num_photographers, num_editors):
        self.env = env 
        self.photographer = simpy.Resource(env, num_photographers)
        self.editor = simpy.Resource(env, num_editors)

    def take_photos(self, in_studio: bool, customer):
        yield self.env.timeout(random.randint(1,3))

    def edit_photos(self, in_studio: bool, customer):
        yield self.env.timeout(random.randint(3,4))

def use_fotof(env, fotof_studio, customer):
    start_time = env.now

    print(f"Starting customer: {customer}")

    with fotof_studio.photographer.request() as request:
        yield request
        print(f"Customer: {customer} starting photos at {env.now}")
        yield env.process(fotof_studio.take_photos(True, customer))

    

    with fotof_studio.editor.request() as request:
        yield request
        print(f"Customer: {customer} starting editiing at {env.now}")
        yield env.process(fotof_studio.edit_photos(True, customer))

    print(f"Customer: {customer} finished at {env.now}")


def simulate_fotof(env, fotof_studio):
    customer = 0
    while True:
        yield env.timeout(1)

        env.process(use_fotof(env, fotof_studio, customer))

        customer += 1

if __name__ == "__main__":
    env = simpy.Environment()
    fotof1 = Fotof_studio(env, 4, 4)

    env.process(simulate_fotof(env, fotof1))
    env.run(until=90)