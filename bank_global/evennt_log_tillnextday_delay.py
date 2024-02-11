from eventlog_step import EventlogStep
from event_generator import generate_event
import simpy

class TillNextDayDelay(EventlogStep):

    def __init__(self, step_id: int, start_hour: int, end_hour: int):
        print("Creating step delay with id ", step_id)
        self.step_id = step_id
        self.next_steps = []
        self.start_hour = start_hour
        self.end_hour = end_hour

    def hours_to_mins(self, time):
        return 60*time

    def days_to_mins(self, days):
        return days*self.hours_to_mins(24)

    def in_working_hours(self, time):
        # Bring down to a week time frame
        new_time = time % self.days_to_mins(7)

        # Return false if saturday or sunday
        if new_time >= self.days_to_mins(5):
            return False
        
        # Bring down to a day time frame
        new_time = new_time % self.days_to_mins(1)

        # Return false if time of day is before 9am or after 4pm
        if new_time > (self.hours_to_mins(self.end_hour) - 1) or new_time < self.hours_to_mins(self.start_hour):
            return False 

        # If this point is reached, then it is working hours, therefore return true
        return True
    
    def wait_until_working_hours(self, env):

        while (self.in_working_hours(env.now) == False):
            # Bring timeframe down to the week scale so we can run a bunch of checks
            time_mins = env.now % self.days_to_mins(7)

            # If the current time is after friday end hour, wait until monday morning at start hour
            if time_mins > self.days_to_mins(4) + self.hours_to_mins(self.end_hour) - 1:
                yield env.timeout((self.days_to_mins(7) + self.hours_to_mins(self.start_hour)) - time_mins)
            
            # If it's before start hour on a business day, wait until start hour
            elif (time_mins % self.days_to_mins(1)) < self.hours_to_mins(self.start_hour):
                yield env.timeout(self.hours_to_mins(self.start_hour) - (time_mins % self.days_to_mins(1)))

            # If it's after end hour on a business day, wait until start hour next day
            elif (time_mins % self.days_to_mins(1)) > self.hours_to_mins(self.end_hour):
                yield env.timeout(self.days_to_mins(1) + self.hours_to_mins(self.start_hour) - (time_mins % self.days_to_mins(1)))

    def complete_step(self, customer_id, env, writer) -> int:
        print(f"Doing delay at {env.now}")

        if self.in_working_hours(env.now):
            yield env.timeout(self.hours_to_mins(8))

        yield env.process(self.wait_until_working_hours(env))

        # print("Next possible steps are: ", [x[0] for x in self.next_steps])

        if len(self.next_steps) == 0:
            return -1
        
        return generate_event(self.next_steps)

    
