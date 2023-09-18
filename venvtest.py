import simpy
import random
import math
from generate_events import *
from datetime import datetime, timedelta

import csv

NUM_STUDIOS = 1
NUM_ORDERS = 3600*NUM_STUDIOS

NUM_TECHS = 2

class Fotof_studio(object):
    """
    Fotof studio class:

    Contains the resources required to complete the eventlog:
    - photographers
    - editors
    """
    def __init__(self, env, num_photographers, num_techs):
        self.env = env 
        self.photographer = simpy.PriorityResource(env, num_photographers)
        self.tech = simpy.PriorityResource(env, num_techs)

    def take_photos(self, in_studio: bool, customer):
        yield self.env.timeout(random.randint(1,3))

    def edit_photos(self, in_studio: bool, customer):
        yield self.env.timeout(random.randint(3,4))

    def wait(self, customer, time_mins):
        yield self.env.timeout(time_mins)

# HELPER FUNCTIONS 

def get_num_photographers():
    return random.randint(3,4)

def get_studio_or_location(is_personal):
    if not(is_personal):
        return AT_STUDIO
    else:
        return generate_outcome(PERSONAL_ON_LOCATION)

def hours_to_mins(hours):
    return hours*60

def disp_day(time_mins):
    days_dict = {
        "0": "Monday",
        "1": "Tuesday",
        '2': 'Wednesday',
        '3': 'Thursday',
        '4': 'Friday',
        '5': 'Saturday',
        '6': 'Sunday',
    }

    time = time_mins % days_to_mins(7)

    return days_dict[str(int(time/(days_to_mins(1))))]



    
def disp_time(env_time_mins):
    """
    Returns the env time in string format to be printed to the eventlog
    """
    time = datetime(2018, 1, 1, 0, 0, 0, 0)

    time += timedelta(seconds=(env_time_mins*60))

    return time.strftime("%Y-%m-%dT%H:%M:%S")

def days_to_mins(num_days):
    return num_days*24*60



def in_photographer_working_hours(time_mins):
    # Bring down to a week time frame
    new_time = time_mins % days_to_mins(7)

    # Return false if saturday or sunday
    if new_time >= days_to_mins(5):
        return False
    
    # Bring down to a day time frame
    new_time = new_time % days_to_mins(1)

    # Return false if time of day is before 9am or after 4pm
    if new_time > hours_to_mins(16) or new_time < hours_to_mins(9):
        return False 

    # If this point is reached, then it is working hours, therefore return true
    return True

def in_tech_working_hours(time_mins):
    # Bring down to a week time frame
    new_time = time_mins % days_to_mins(7)

    # Return false if saturday or sunday
    if new_time >= days_to_mins(5):
        return False
    
    # Bring down to a day time frame
    new_time = new_time % days_to_mins(1)

    # Return false if time of day is before 9am or after 4pm
    if new_time > hours_to_mins(15.5) or new_time < hours_to_mins(8.5):
        return False 

    # If this point is reached, then it is working hours, therefore return true
    return True

# Simulate the use of a fotof studio for a single customer
def use_fotof(env, fotof_studio, customer, writer, obj_writer):
    # Get info about the order 
    is_personal = bool(generate_outcome(PERSONAL_OR_CORPORATE))
    at_studio = bool(get_studio_or_location(is_personal))

    printed = False
    digital = False

    while True:

        # Booking stage
        while True:
            if is_personal:
                booking_status = generate_outcome(PERSONAL_BOOKING)
            else:
                booking_status = generate_outcome(COROPRATE_BOOKING)
            
            if booking_status == BOOKING_MADE:
                writer.writerow([f'{customer:05d};DETAILS ENTERED;{disp_time(env.now)}'])
                break
            elif booking_status == BOOKING_CANCELLED:
                writer.writerow([f'{customer:05d};DETAILS ENTERED;{disp_time(env.now)}'])

                # Wait 3-20 days to cancel
                yield env.timeout(random.randint(3*60*24, 20*60*24))

                writer.writerow([f'{customer:05d};BOOKING CANCELLED;{disp_time(env.now)}'])
                return

        # Wait 3-40 days
        yield env.timeout(60*random.randint(3*24, 40*24))

        if is_personal:
            duration = 1 if at_studio else random.randint(2,3)
        else:
            duration = random.randint(2,4)

        
        job_queue_priority = 10
        

        while True:
            # Wait for a photographer and try grab a slot, if not able to, wait until the next day and try again
            with fotof_studio.photographer.request(priority =  job_queue_priority) as photographer:
                yield photographer
                if (env.now % 60 != 0):
                    yield env.timeout(60 - (env.now % 60))

                if in_photographer_working_hours(env.now) and in_photographer_working_hours(env.now + hours_to_mins(duration-1)):
                    writer.writerow([f'{customer:05d};PHOTOGRAPHER CHECKED IN;{disp_time(env.now)}'])
                    # print(f'Customer {customer} checked in for a {duration} hour job')
                    yield env.timeout(hours_to_mins(duration))
                    break

            if in_photographer_working_hours(env.now) and not(in_photographer_working_hours(env.now+hours_to_mins(duration))):
                    yield env.timeout(hours_to_mins(duration+1))

            if not(in_photographer_working_hours(env.now)):
                yield env.process(wait_until_photographer_working_hours(env))

            job_queue_priority = 0

        # Photographer checked in stage (mark back in time when the customer contacted if late so that the photographer resource step works)

        if at_studio:
            checkin_status = generate_outcome(STUDIO_CHECK_IN)
        else:
            checkin_status = generate_outcome(LOCATION_CHECK_IN)

        if checkin_status == CHECK_IN_LATE:
            writer.writerow([f'{customer:05d};CONTACTED CUSTOMER;{disp_time(env.now - hours_to_mins(duration) + random.randint(5, 15))}'])
        
        elif checkin_status == CHECK_IN_NO_SHOW:
            writer.writerow([f'{customer:05d};CONTACTED CUSTOMER;{disp_time(env.now - hours_to_mins(duration) + random.randint(5, 15))}'])
            
            if generate_outcome(NO_SHOW_RESCHEDULED) == RESCHEDULED:
                # Delay until midnight then wait until between 8:30 and 10:30am
                yield env.timeout(hours_to_mins(24 + 8.5)-(env.now % hours_to_mins(24)) + random.randint(0, hours_to_mins(2)))
                continue
            else:
                break

        # Since job would've finished by 5pm, wait until photos get sent to editor at 5pm at the end of the day
        yield env.timeout(hours_to_mins(17) - (env.now % hours_to_mins(24)))

        # INITIAL PHOTO EDIT

        tech_job_duration = random.randint(15,30) if at_studio else random.randint(25,60)

        with fotof_studio.tech.request() as tech:
            yield tech

            # If duration won't fit into working hours, delay over to out of hours
            if in_tech_working_hours(env.now) and not(in_tech_working_hours(env.now + tech_job_duration - 15)):
                yield env.timeout(tech_job_duration + 15)
                

            # Delay until start of next working day if out of hours
            if not(in_tech_working_hours(env.now)):
                yield env.process(wait_until_tech_working_hours(env))
                

            yield env.timeout(tech_job_duration)

        # Photos are uploaded
        writer.writerow([f'{customer:05d};PHOTO_UPLOADED;{disp_time(env.now)}'])

        yield env.timeout(random.randint(1,3))

        # Customer is notified of photos
        writer.writerow([f'{customer:05d};CUSTOMER NOTIFIED OF GALLERY;{disp_time(env.now)}'])

        # Reminder step

        if generate_outcome(REMINDER_OF_PHOTOS) == CUSTOMER_REMINDED:

            yield env.timeout(days_to_mins(24) + hours_to_mins(24 + 8.5)-(env.now % hours_to_mins(24)) + random.randint(0, hours_to_mins(1)))

            writer.writerow([f'{customer:05d};CUSTOMER REMINDED OF GALLERY;{disp_time(env.now)}'])

            after_reminder_status = generate_outcome(CUSTOMER_AFTER_REMINDER)
            
            if after_reminder_status != CUSTOMER_ORDERS:
                yield env.timeout(days_to_mins(4) + hours_to_mins(24 + 9.5)-(env.now % hours_to_mins(24)) + random.randint(0, hours_to_mins(1)))
                
                if after_reminder_status == CUSTOMER_INVOICED:
                    break

                writer.writerow([f'{customer:05d};INVOICE ISSUED;{disp_time(env.now)}'])

                # Wait some time until customer goes and orders
                yield env.timeout(random.randint(hours_to_mins(3), days_to_mins(6)))

                if not(in_photographer_working_hours(env.now)):
                    yield env.process(wait_until_photographer_working_hours(env))
                    yield env.timeout(random.randint(hours_to_mins(0.5), hours_to_mins(1.5)))
            else:
                # Wait between 3 hours after invoice and 1 hour before customer orders
                yield env.timeout(random.randint(hours_to_mins(3), days_to_mins(4)))

                if not(in_photographer_working_hours(env.now)):
                    yield env.process(wait_until_photographer_working_hours(env))
        else:
            # Wait a random time between 3hours after customer is notified and 1 hour before a reminder is sent
            
            # Initial wait
            yield env.timeout(random.randint(hours_to_mins(3), days_to_mins(24)))

            if not(in_photographer_working_hours(env.now)):
                yield env.process(wait_until_photographer_working_hours(env))

        # Order is now placed   
        writer.writerow([f'{customer:05d};ORDER PLACED;{disp_time(env.now)}'])

        # EDITING STEP
        if generate_outcome(NEEDS_EDITING_INITIALLY) == EDITING_REQUIRED:

            tech_job_duration = random.randint(15,40)

            with fotof_studio.tech.request() as tech:
                yield tech

                # If duration won't fit into working hours, delay over to out of hours
                if in_tech_working_hours(env.now) and not(in_tech_working_hours(env.now + tech_job_duration - 30)):
                    yield env.timeout(tech_job_duration + 30)
                    

                # Delay until start of next working day if out of hours
                if not(in_tech_working_hours(env.now)):
                    yield env.process(wait_until_tech_working_hours(env))
                    

                yield env.timeout(tech_job_duration)

                writer.writerow([f'{customer:05d};PHOTOS EDITED;{disp_time(env.now)}'])   

                if generate_outcome(NEEDS_TO_TALK_WITH_TECHNICIAN) == TECHNICIAN_REQUIRED:

                    while True:
                        tech_call_duration = random.randint(3,15)
                         # If duration won't fit into working hours, delay over to out of hours
                        if in_tech_working_hours(env.now) and not(in_tech_working_hours(env.now + tech_call_duration - 30)):
                            yield env.timeout(tech_call_duration + 30)
                            

                        # Delay until start of next working day if out of hours
                        if not(in_tech_working_hours(env.now)):
                            yield env.process(wait_until_tech_working_hours(env))
                            
                        yield env.timeout(tech_call_duration)

                        writer.writerow([f'{customer:05d};CUSTOMER ASKED FOR INFORMATION;{disp_time(env.now)}'])   

                        tech_job_duration = random.randint(10,40)

                        # If duration won't fit into working hours, delay over to out of hours
                        if in_tech_working_hours(env.now) and not(in_tech_working_hours(env.now + tech_job_duration - 30)):
                            yield env.timeout(tech_job_duration + 30)
                            

                        # Delay until start of next working day if out of hours
                        if not(in_tech_working_hours(env.now)):
                            yield env.process(wait_until_tech_working_hours(env))

                        yield env.timeout(tech_job_duration)

                        writer.writerow([f'{customer:05d};PHOTOS EDITED;{disp_time(env.now)}'])   

                        if generate_outcome(NEEDS_ANOTHER_TECHNICIAN_TALK) == TECHNICIAN_NOT_REQUIRED:
                            break


        # Provide info as to whether photos are printed or not
        printed = (generate_outcome(PHOTOS_GETTING_PRINTED) == GETTING_PRINTED)
        digital = (generate_outcome(PHOTOS_GETTING_DIGITAL) == GETTING_DIGITAL)

        # Provide relevant info for printed/digital photos
        if digital:
            with fotof_studio.tech.request() as tech:
                yield tech
                upload_duration = 3
                # If duration won't fit into working hours, delay over to out of hours
                if in_tech_working_hours(env.now) and not(in_tech_working_hours(env.now + upload_duration - 30)):
                    yield env.timeout(upload_duration + 30)
                    

                # Delay until start of next working day if out of hours
                if not(in_tech_working_hours(env.now)):
                    yield env.process(wait_until_tech_working_hours(env))
                    

                yield env.timeout(upload_duration)

                writer.writerow([f'{customer:05d};PHOTOS UPLOADED TO DROPBOX;{disp_time(env.now)}'])   

        if printed:
            with fotof_studio.tech.request() as tech:
                yield tech
                print_duration = 15
                # If duration won't fit into working hours, delay over to out of hours
                if in_tech_working_hours(env.now) and not(in_tech_working_hours(env.now + print_duration - 30)):
                    yield env.timeout(print_duration + 30)
                    

                # Delay until start of next working day if out of hours
                if not(in_tech_working_hours(env.now)):
                    yield env.process(wait_until_tech_working_hours(env))
                    

                yield env.timeout(print_duration)
            writer.writerow([f'{customer:05d};PHOTOS PRINTED;{disp_time(env.now)}'])   

        yield env.timeout(hours_to_mins(24 + 9.5)-(env.now % hours_to_mins(24)) + random.randint(0, hours_to_mins(1)))

        break
        
    # Invoice step

    # Initial invoice issued
    writer.writerow([f'{customer:05d};INVOICE ISSUED;{disp_time(env.now)}']) 

    # Reminder step

    invoice_reminder_count = 0

    while generate_outcome(INVOICE_REMINDER) == NEEDS_INVOICE_REMINDER:
        if invoice_reminder_count == 5:
            yield env.timeout(days_to_mins(6) + hours_to_mins(24 + 9.5)-(env.now % hours_to_mins(24)) + random.randint(0, hours_to_mins(1)))
            writer.writerow([f'{customer:05d};INVOICE REFERRED TO COLLECTIONS;{disp_time(env.now)}'])
            return

        invoice_reminder_count += 1
        yield env.timeout(days_to_mins(6) + hours_to_mins(24 + 9.5)-(env.now % hours_to_mins(24)) + random.randint(0, hours_to_mins(1)))
        writer.writerow([f'{customer:05d};INVOICE REMINDER SENT;{disp_time(env.now)}'])  

    # Actual ordering/payment step

    if printed:
        collect_payment_status = generate_outcome(PRINTED_STRAIGHT_TO_UPDATE)
    else:
        collect_payment_status = generate_outcome(DIGITAL_OR_FEE_STRAIGHT_TO_UPDATE)


    yield env.timeout(random.randint(hours_to_mins(3), days_to_mins(6)))

    if not(in_photographer_working_hours(env.now)):
        yield env.process(wait_until_photographer_working_hours(env))
        yield env.timeout(random.randint(0, hours_to_mins(6)))

    if collect_payment_status == ORDER_NOT_UPDATED:
        writer.writerow([f'{customer:05d};COLLECTED PAYMENT;{disp_time(env.now)}'])  
        yield env.timeout(random.randint(1,2))

    # Order updated step
    writer.writerow([f'{customer:05d};ORDER UPDATED;{disp_time(env.now)}'])  

    # Dropbox link step
    if digital:
        with fotof_studio.tech.request() as tech:
            yield tech
            upload_duration = random.randint(2,3)
            # If duration won't fit into working hours, delay over to out of hours
            if in_photographer_working_hours(env.now) and not(in_photographer_working_hours(env.now + upload_duration - 30)):
                yield env.timeout(upload_duration + 30)
                

            # Delay until start of next working day if out of hours
            if not(in_photographer_working_hours(env.now)):
                yield env.process(wait_until_photographer_working_hours(env))

            yield env.timeout(upload_duration)
        writer.writerow([f'{customer:05d};DROPBOX LINK TO PHOTOS SENT;{disp_time(env.now)}'])  
    
    # Printed photos received
    if printed:
        if collect_payment_status == ORDER_UPDATED:
            if generate_outcome(SEND_PRINTOUT_OR_PICKUP) == PRINTOUT_SENT:
            
                print_duration = random.randint(8,12)

                if in_photographer_working_hours(env.now) and not(in_photographer_working_hours(env.now + print_duration - 30)):
                    yield env.timeout(print_duration + 30)
                

                # Delay until start of next working day if out of hours
                if not(in_photographer_working_hours(env.now)):
                    yield env.process(wait_until_photographer_working_hours(env))
                
                yield env.timeout(print_duration)
                writer.writerow([f'{customer:05d};PRINTOUTS SENT;{disp_time(env.now)}'])  
            else:
                while generate_outcome(PHOTOS_REMINDER_SENT) == PICKUP_REMINDER_SENT:
                    writer.writerow([f'{customer:05d};PICKUP REMINDER SENT;{disp_time(env.now)}']) 
                    yield env.timeout(days_to_mins(6) + hours_to_mins(24 + 9.5)-(env.now % hours_to_mins(24)) + random.randint(0, hours_to_mins(1))) 

                yield env.timeout(random.randint(hours_to_mins(3), days_to_mins(6)))

                if not(in_photographer_working_hours(env.now)):
                    yield env.process(wait_until_photographer_working_hours(env))
                    yield env.timeout(random.randint(0, hours_to_mins(6)))

                
            
    # Close order if customer ended up receiving something

    if digital or printed:
        yield env.timeout(random.randint(1,2))
        writer.writerow([f'{customer:05d};ORDER CLOSED;{disp_time(env.now)}'])  

def generate_delay_between_customers(index):
    initial_delay = int(30*(3-math.sin(3*math.pi*index)))

    return random.randint(initial_delay-1, initial_delay+1)



# Simulate the operation of the entire fotof studio for a list of orders
def simulate_fotof_studio(env, fotof_studio, orders: list, writer, obj_writer):
    for i in range(len(orders)):
        yield env.timeout(generate_delay_between_customers(i))
        env.process(use_fotof(env, fotof_studio, orders[i], writer, obj_writer))

def wait_until_photographer_working_hours(env):
    # Keep adding delays until we're within business hours
    while (in_photographer_working_hours(env.now) == False) or ((env.now % 60) != 0):
        # Bring timeframe down to the week scale so we can run a bunch of checks
        time_mins = env.now % days_to_mins(7)
        # print("Customer ", customer,  " Can't get out at time ", disp_time(env.now), " ", print_day_of_week(time_mins))

        # If the current time is after friday 4pm, wait until monday morning at 9am
        if time_mins > days_to_mins(4) + hours_to_mins(16):
            yield env.timeout((days_to_mins(7) + hours_to_mins(9)) - time_mins)
        
        # If it's before 9am on a business day, wait until 9am
        elif (time_mins % days_to_mins(1)) < hours_to_mins(9):
            yield env.timeout(hours_to_mins(9) - (time_mins % days_to_mins(1)))

        # If it's after 4pm on a business day, wait until 9am
        elif (time_mins % days_to_mins(1)) > hours_to_mins(16):
            yield env.timeout(days_to_mins(1) + hours_to_mins(9) - (time_mins % days_to_mins(1)))

        # The only other option is that we're not exactly on the hour, hence wait until the next hour
        else:
            yield env.timeout(hours_to_mins(1) - (time_mins % 60))

def wait_until_tech_working_hours(env):
    # Keep adding delays until we're within business hours
    while (in_tech_working_hours(env.now) == False):
        # Bring timeframe down to the week scale so we can run a bunch of checks
        time_mins = env.now % days_to_mins(7)

        # If the current time is after friday 3:45pm, wait until monday morning at 8:30am
        if time_mins > (days_to_mins(4) + hours_to_mins(15.5)):
            yield env.timeout((days_to_mins(7) + hours_to_mins(8.5)) - time_mins)
        
        # If it's before 8:30am on a business day, wait until 8:30am
        elif (time_mins % days_to_mins(1)) < hours_to_mins(8.5):
            yield env.timeout(hours_to_mins(8.5) - (time_mins % days_to_mins(1)) + 10)

        # If it's after 3:30pm on a business day, wait until 8:30am
        elif (time_mins % days_to_mins(1)) > hours_to_mins(15.5):
            yield env.timeout(days_to_mins(1) + hours_to_mins(8.5) - (time_mins % days_to_mins(1)))


if __name__ == "__main__":
    

    # Create the different studios
    fotof_studios = []

    # Order ids contains the order ids for each studio
    order_ids = [[] for _ in range(NUM_STUDIOS)]

    # Give each studio their orders and their ids
    for i in range(NUM_ORDERS):
        order_ids[random.randint(0, (NUM_STUDIOS-1))].append(i+1)

    with open('eventlog.csv', 'w') as file:
        writer = csv.writer(file)
        with open('object.csv', 'w') as object_file:
            obj_writer = csv.writer(object_file)

            # Write the first row
            writer.writerow(['CaseId;EventName;Timestamp'])

            # Simulate the studios
            for studio_num in range(NUM_STUDIOS):
                # Create environment to be simulated
                env = simpy.Environment()
                fotof_studios.append(Fotof_studio(env, get_num_photographers(), NUM_TECHS))
                print(f"Starting studio: {studio_num+1}\nNum orders: {len(order_ids[studio_num])}")
                env.process(simulate_fotof_studio(env, fotof_studios[studio_num], order_ids[studio_num], writer, obj_writer))
                env.run()

            object_file.close()

        file.close()