import simpy
import random
from generate_events import *
from datetime import datetime, timedelta

import csv

NUM_STUDIOS = 1
NUM_ORDERS = 2000

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
        self.photographer = simpy.Resource(env, num_photographers)
        self.tech = simpy.Resource(env, num_techs)

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
def use_fotof(env, fotof_studio, customer, writer):
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
                writer.writerow([f'{customer:05d};"DETAILS ENTERED";"{disp_time(env.now)}"'])
                break
            elif booking_status == BOOKING_CANCELLED:
                writer.writerow([f'{customer:05d};"DETAILS ENTERED";"{disp_time(env.now)}"'])

                # Wait 3-20 days to cancel
                yield env.timeout(random.randint(3*60*24, 20*60*24))

                writer.writerow([f'{customer:05d};"BOOKING CANCELLED";"{disp_time(env.now)}"'])
                return

        # Wait 3-40 days
        yield env.timeout(60*random.randint(3*24, 40*24))

        if is_personal:
            duration = 1 if at_studio else random.randint(4,6)
        else:
            duration = random.randint(4,8)
        

        # # Wait until a photographer is free then grab a slot
        # with fotof_studio.photographer.request() as photographer:
        #         yield photographer

        #         # Wait until next exact hour mark if not on it already
        #         if (env.now % 60 != 0):
        #             yield env.timeout(60 - env.now % 60)

        #         # If duration won't fit into working hours, delay over to out of hours
        #         if in_photographer_working_hours(env.now) and not(in_photographer_working_hours(env.now+hours_to_mins(duration))):
        #             yield env.timeout(hours_to_mins(duration+1))

        #         # Delay until start of next working day if out of hours
        #         if not(in_photographer_working_hours(env.now)):
        #             yield env.process(wait_until_photographer_working_hours(env))

        #             # Assuming we're at 9am, make it look like job doesn't just start at 9am
        #             yield env.timeout(hours_to_mins(random.randint(0, 8-duration)))

        # print(f'{customer} Before waiting for photographer {disp_time(env.now)} with duration {duration} hours')

        while True:
            # Wait for a photographer and try grab a slot, if not able to, wait until the next day and try again
            with fotof_studio.photographer.request() as photographer:
                yield photographer
                if (env.now % 60 != 0):
                    yield env.timeout(60 - (env.now % 60))

                if in_photographer_working_hours(env.now) and in_photographer_working_hours(env.now + hours_to_mins(duration-1)):
                    writer.writerow([f'{customer:05d};"PHOTOGRAPHER CHECKED IN";"{disp_time(env.now)}"'])
                    yield env.timeout(hours_to_mins(duration))
                    break

            if in_photographer_working_hours(env.now) and not(in_photographer_working_hours(env.now+hours_to_mins(duration))):
                    yield env.timeout(hours_to_mins(duration+1))

            if not(in_photographer_working_hours(env.now)):
                yield env.process(wait_until_photographer_working_hours(env))
                yield env.timeout(hours_to_mins(random.randint(0, 8-duration)))

        # Photographer checked in stage (mark back in time when the customer contacted if late so that the photographer resource step works)
        print(f'Photographer finished on ', disp_day(env.now))

        if at_studio:
            checkin_status = generate_outcome(STUDIO_CHECK_IN)
        else:
            checkin_status = generate_outcome(LOCATION_CHECK_IN)

        if checkin_status == CHECK_IN_LATE:
            writer.writerow([f'{customer:05d};"CONTACTED CUSTOMER";"{disp_time(env.now - hours_to_mins(duration) + random.randint(5, 15))}"'])
        
        elif checkin_status == CHECK_IN_NO_SHOW:
            writer.writerow([f'{customer:05d};"CONTACTED CUSTOMER";"{disp_time(env.now - hours_to_mins(duration) + random.randint(5, 15))}"'])
            
            if generate_outcome(NO_SHOW_RESCHEDULED) == RESCHEDULED:
                # Delay until midnight then wait until between 8:30 and 10:30am
                yield env.timeout(hours_to_mins(24 + 8.5)-(env.now % hours_to_mins(24)) + random.randint(0, hours_to_mins(2)))
                continue
            else:
                break

        # Since job would've finished by 5pm, wait until photos get sent to editor at 5pm at the end of the day
        yield env.timeout(hours_to_mins(17) - (env.now % hours_to_mins(24)))

        # INITIAL PHOTO EDIT


        # with fotof_studio.tech.request() as tech:
        #     yield tech
        #     if (env.now % 60 != 0):
        #         yield env.timeout(60 - (env.now % 60))

        #     if in_tech_working_hours(env.now) and in_tech_working_hours(env.now + hours_to_mins()):
                
        #         yield env.timeout(hours_to_mins(duration))
        #         writer.writerow([f'{customer:05d};"PHOTO_UPLOADED";"{disp_time(env.now)}"'])
        #         break

        # if in_photographer_working_hours(env.now) and not(in_photographer_working_hours(env.now+hours_to_mins(duration))):
        #         yield env.timeout(hours_to_mins(duration+1))

        # if not(in_photographer_working_hours(env.now)):
        #     yield env.process(wait_until_photographer_working_hours(env))

        tech_job_duration = random.randint(15,30)

        # print(f"{customer} waiting for tech at {disp_time(env.now)}")
        with fotof_studio.tech.request() as tech:
            yield tech
            # print(f"Tech starting {customer} at {disp_time(env.now)}")

            # If duration won't fit into working hours, delay over to out of hours
            if in_tech_working_hours(env.now) and not(in_tech_working_hours(env.now + tech_job_duration - 15)):
                # print(f"Job {customer} couldn't fit {duration} mins")
                yield env.timeout(tech_job_duration + 15)
                

            # Delay until start of next working day if out of hours
            if not(in_tech_working_hours(env.now)):
                # print(f"Job {customer} out of hours at {disp_time(env.now)}")
                yield env.process(wait_until_tech_working_hours(env))
                # print(f'{customer} done waiting until business hours')
                

            yield env.timeout(tech_job_duration)

        
        print(f'Tech done with customer {customer} at {disp_time(env.now)} on {disp_day(env.now)}')

        # Photos are uploaded
        writer.writerow([f'{customer:05d};"PHOTO_UPLOADED";"{disp_time(env.now)}"'])

        # Customer is notified of photos
        writer.writerow([f"{customer:05d}: CUSTOMER NOTIFIED OF GALLERY"])

        # Reminder step

        if generate_outcome(REMINDER_OF_PHOTOS) == CUSTOMER_REMINDED:
            writer.writerow([f"{customer:05d}: CUSTOMER REMINDED OF GALLERY"])
            after_reminder_status = generate_outcome(CUSTOMER_AFTER_REMINDER)
            
            if after_reminder_status != CUSTOMER_ORDERS:
                
                if after_reminder_status == CUSTOMER_INVOICED:
                    break

                writer.writerow([f"{customer:05d}: INVOICE ISSUED"])

        # Order is now placed   
        writer.writerow([f"{customer:05d}: ORDER PLACED"])

        # EDITING STEP
        if generate_outcome(NEEDS_EDITING_INITIALLY) == EDITING_REQUIRED:
            if generate_outcome(NEEDS_TO_TALK_WITH_TECHNICIAN) == TECHNICIAN_REQUIRED:
                while True:
                    writer.writerow([f"{customer:05d}: CUSTOMER ASKED FOR INFORMATION"])
                    if generate_outcome(NEEDS_ANOTHER_TECHNICIAN_TALK) == TECHNICIAN_NOT_REQUIRED:
                        break

            writer.writerow([f"{customer:05d}: PHOTOS EDITED"])

        # Provide info as to whether photos are printed or not
        printed = (generate_outcome(PHOTOS_GETTING_PRINTED) == GETTING_PRINTED)
        digital = (generate_outcome(PHOTOS_GETTING_DIGITAL) == GETTING_DIGITAL)

        # Provide relevant info for printed/digital photos
        if digital:
            writer.writerow([f"{customer:05d}: PHOTOS UPLOADED TO DROPBOX"])

        if printed:
            writer.writerow([f"{customer:05d}: PHOTOS PRINTED"])

        break
        
    # Invoice step

    # Initial invoice issued
    writer.writerow([f"{customer:05d}: INVOICE ISSUED"])

    # Reminder step

    invoice_reminder_count = 0

    while generate_outcome(INVOICE_REMINDER) == NEEDS_INVOICE_REMINDER:
        if invoice_reminder_count == 5:
            writer.writerow([f"{customer:05d}: INVOICE REFERRED TO COLLECTIONS"])
            return

        invoice_reminder_count += 1
        writer.writerow([f"{customer:05d}: INVOICE REMINDER SENT"])

    # Actual ordering/payment step

    if printed:
        collect_payment_status = generate_outcome(PRINTED_STRAIGHT_TO_UPDATE)
    else:
        collect_payment_status = generate_outcome(DIGITAL_OR_FEE_STRAIGHT_TO_UPDATE)

    if collect_payment_status == ORDER_NOT_UPDATED:
        writer.writerow([f"{customer:05d}: COLLECTED PAYMENT"])

    # Order updated step
    writer.writerow([f"{customer:05d}: ORDER UPDATED"])

    # Dropbox link step
    if digital:
        writer.writerow([f"{customer:05d}: DROPBOX LINK TO PHOTOS SENT"])
    
    # Printed photos received
    if printed:
        if collect_payment_status == ORDER_UPDATED:
            if generate_outcome(SEND_PRINTOUT_OR_PICKUP) == PRINTOUT_SENT:
                writer.writerow([f"{customer:05d}: PRINTOUTS SENT"])
            else:
                while generate_outcome(PHOTOS_REMINDER_SENT) == PICKUP_REMINDER_SENT:
                    writer.writerow([f"{customer:05d}: PICKUP REMINDER SENT"])
            
    # Close order if customer ended up receiving something

    if digital or printed:
        writer.writerow([f"{customer:05d}: ORDER CLOSED"])


    # Invoice stage


# Simulate the operation of the entire fotof studio for a list of orders
def simulate_fotof_studio(env, fotof_studio, orders: list, writer):
    for customer in orders:
        yield env.timeout(1)
        env.process(use_fotof(env, fotof_studio, customer, writer))

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
    # Create environment to be simulated
    env = simpy.Environment()

    # Create the different studios
    fotof_studios = []
    for i in range(NUM_STUDIOS):
        fotof_studios.append(Fotof_studio(env, get_num_photographers(), NUM_TECHS))

    # Order ids contains the order ids for each studio
    order_ids = [[] for _ in range(NUM_STUDIOS)]

    # Give each studio their orders and their ids
    for i in range(NUM_ORDERS):
        order_ids[random.randint(0, (NUM_STUDIOS-1))].append(i+1)

    with open('eventlog.csv', 'w') as file:
        writer = csv.writer(file)

        # Write the first row
        writer.writerow(['CaseId;\"EventName\";\"Timestamp\"'])

        # Simulate the studios
        for studio_num in range(NUM_STUDIOS):
            print(f"Starting studio: {studio_num+1}\nNum orders: {len(order_ids[studio_num])}")
            env.process(simulate_fotof_studio(env, fotof_studios[studio_num], order_ids[studio_num], writer))
            env.run()

        file.close()