import simpy

class EventlogResource:

    def __init__(self, num_resources: int, env, start_hour: int, end_hour: int, steps: list, minute_interval:int=60):
        self.resouce = simpy.Resource(env, num_resources)
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.associated_steps = steps
        self.minute_interval = minute_interval

    def is_resource_for_step(self, step) -> bool:
        return step in self.associated_steps
    
    def hours_to_mins(self, time):
        return 60*time

    def days_to_mins(self, days):
        return days*self.hours_to_mins(24)
    
    def in_resource_working_hours(self, time):
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
    
    def wait_until_resouce_working_hours(self, env):

        while (self.in_resource_working_hours(env.now) == False) or ((env.now % self.minute_interval) != 0):
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

            # The only other option is that we're not exactly on the hour, hence wait until the next hour
            else:
                yield env.timeout(self.hours_to_mins(1) - (time_mins % self.minute_interval))


    def complete_job(self, env, job_time_mins=None):
        if job_time_mins == None:
            job_time_mins = self.minute_interval

        


    
