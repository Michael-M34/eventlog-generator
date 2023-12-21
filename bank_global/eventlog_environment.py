from eventlog_step import EventlogStep
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


    def add_step(self, step_name: str):
        """
        Add a certain step to the list of possible steps to be executed

        Parameters:
        step_name (str): The name of the step (or what will be printed in the eventlog)

        Returns:
        None
        """
        self.steps.append(EventlogStep(self.num_steps, step_name))
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



    def complete_orders(self, customer_ids: list, wait_between_orders: int):
        print("Starting orders")
        self.env = simpy.Environment()
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









    

