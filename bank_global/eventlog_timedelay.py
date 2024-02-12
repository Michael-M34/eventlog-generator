from eventlog_step import EventlogStep
from event_generator import generate_event
import simpy


class EventlogDelay(EventlogStep):
    def __init__(self, step_id: int, step_name: str, time_length: int):
        print("Creating delay with id ", step_id, " and delay length ", time_length)
        self.step_name = step_name
        self.step_id = step_id
        self.next_steps = []
        self.time_length = time_length


    def add_next_steps(self, next_steps_list: list):
        """
        Adds the list of possible next steps to the current step's next step list

        Paramaters:
        next_steps_list (list): List of next steps in the form of a tuple (step_id, probability)
        """
        for step in next_steps_list:
            self.next_steps.append(step)

    def complete_step(self, customer_id, env, writer) -> int:
        print(f"Doing {self.step_name} at {env.now}")

        
        yield env.timeout(self.time_length)

        # print("Next possible steps are: ", [x[0] for x in self.next_steps])

        if len(self.next_steps) == 0:
            return -1
        
        return generate_event(self.next_steps)