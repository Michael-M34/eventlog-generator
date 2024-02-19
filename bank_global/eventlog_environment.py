from eventlog_step import EventlogStep
from eventlog_resource import EventlogResource
from evennt_log_tillnextday_delay import TillNextDayDelay
from eventlog_timedelay import EventlogDelay
import csv
import simpy
import random


class EventlogEnvironment:
    steps: list
    num_steps: int
    csv_writer: csv.writer

    def __init__(self, eventlog_filename="eventlog.csv"):
        self.steps = []
        self.num_steps = 0
        self.file = open(eventlog_filename, 'w')
        self.csv_writer = csv.writer(self.file)
        self.resource_infos = []
        self.resources = []

        # Write header line here
        self.csv_writer.writerow(['CaseId;EventName;Timestamp'])

    def get_step_id_from_name(self, step_name: str) -> int:
        """
        Returns step id given a step name (Assumes step exists)

        Params:
        step_name (str): The name of the step whose id we're searching for

        Returns:
        step_id (int): The name of the step whose id we're searching for

        """
        for step in self.steps:
            if step_name == step.get_step_name():
                return step.get_step_id()
            
        return -1


    def add_step(self, step_name: str, time_length: int):
        """
        Add a certain step to the list of possible steps to be executed

        Parameters:
        step_name (str): The name of the step (or what will be printed in the eventlog)

        Returns:
        None
        """
        self.steps.append(EventlogStep(self.num_steps, step_name, time_length))
        self.num_steps += 1

    def create_next_steps(self, source_step: str, dest_steps: list):
        """
        Creates a list of next steps and their respective weightings

        Parameters:
        source_step (str): The name of the step we're adding paths from
        dest_steps (list): List of tuples in the form (step_name, probability) (probability has to be <= 1)

        Returns:
        None

        """

        step = self.steps[self.get_step_id_from_name(source_step)]

        step.add_next_steps([(self.get_step_id_from_name(dest_step[0]), dest_step[1]) for dest_step in dest_steps])

    def add_eventlog_resource(self, num_resources, start_hour, end_hour, associated_steps: list, minute_interval):
        self.resource_infos.append({"num_resources": num_resources, 
                               "start_hour": start_hour, 
                               "end_hour": end_hour,
                               "associated_steps": associated_steps,
                               "minute_interval": minute_interval})
        
    def add_till_next_day_delay(self, step_name: str, source_step: str, dest_steps: list, start_hour: int, end_hour: int):
        step = self.steps[self.get_step_id_from_name(source_step)]
        new_step = TillNextDayDelay(self.num_steps, step_name, start_hour, end_hour)
        self.steps.append(new_step)
        self.num_steps += 1

        step.add_next_steps([(new_step.get_step_id(), 1)])
        new_step.add_next_steps([(self.get_step_id_from_name(dest_step[0]), dest_step[1]) for dest_step in dest_steps])


    def add_time_delay(self, delay_name: str, source_step: str, dest_steps: list, time_delay: int):
        step = self.steps[self.get_step_id_from_name(source_step)]

        new_step = EventlogDelay(self.num_steps, delay_name, time_delay)
        self.steps.append(new_step)
        self.num_steps += 1

        step.add_next_steps([(new_step.get_step_id(), 1)])
        new_step.add_next_steps([(self.get_step_id_from_name(dest_step[0]), dest_step[1]) for dest_step in dest_steps])


    def complete_orders(self, customer_ids: list, wait_between_orders: int):
        print("Starting orders")
        self.env = simpy.Environment()
        # Create the eventlog resources and add them to each declared step
        for resource_info in self.resource_infos:
            new_resource = EventlogResource(resource_info["num_resources"], self.env, resource_info["start_hour"], 
                                            resource_info["end_hour"], resource_info["minute_interval"])
            for step in resource_info["associated_steps"]:
                step = self.steps[self.get_step_id_from_name(step)]
                step.add_resource_to_step(new_resource)
            

        # Complete the orders for each customer
        for customer_id in customer_ids:
            self.env.process(self.complete_run(customer_id, random.choice(["Application Received", "Customer contacted"])))
        
        self.env.run()



    def complete_run(self, user_id: int, entry_point: str):
        """
        Complete a process run-through for a user

        Parameters:
        user_id (int): User's id
        entry_point (str): Name of the first step user will complete
        """

        step_id = self.get_step_id_from_name(entry_point)

        while (step_id != -1):
            print(user_id, ": ", end="")
            step_id = yield self.env.process(self.steps[step_id].complete_step(user_id, self.env, self.csv_writer))

    def __del__(self):
        print()
        print("Finished generation: Closing now")









    

