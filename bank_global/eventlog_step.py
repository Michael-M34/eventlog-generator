from event_generator import generate_event
import simpy
from datetime import datetime, timedelta


class EventlogStep():
    step_id: int
    step_name: str
    next_steps: list
    
    def __init__(self, step_id: int, step_name: str, time_length: int):
        print("Creating step ", step_name, " with id ", step_id)
        self.step_name = step_name
        self.step_id = step_id
        self.next_steps = []
        self.resource = None
        self.time_length = time_length

    def get_step_name(self) -> str:
        return self.step_name
    
    def get_step_id(self) -> int:
        return self.step_id

    def add_next_steps(self, next_steps_list: list):
        """
        Adds the list of possible next steps to the current step's next step list

        Paramaters:
        next_steps_list (list): List of next steps in the form of a tuple (step_id, probability)
        """
        for step in next_steps_list:
            self.next_steps.append(step)

    def add_resource_to_step(self, resource):
        self.resource = resource

    def disp_time(self, env_time_mins):
        """
        Returns the env time in string format to be printed to the eventlog
        """
        time = datetime(2018, 1, 1, 0, 0, 0, 0)

        time += timedelta(seconds=(env_time_mins*60))

        return time.strftime("%Y-%m-%dT%H:%M:%S")

        
    def complete_step(self, customer_id, env, writer) -> int:
        print(f"Doing {self.step_name} at {env.now}")

        if self.resource != None: 
            yield env.process(self.resource.complete_job(env, self.time_length))
        else:
            yield env.timeout(self.time_length)
        writer.writerow([f'{customer_id:05d};{self.step_name};{self.disp_time(env.now)}'])

        # print("Next possible steps are: ", [x[0] for x in self.next_steps])

        if len(self.next_steps) == 0:
            return -1
        
        return generate_event(self.next_steps)

        
