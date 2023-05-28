import simpy
import random
from generate_events import *
from datetime import datetime, timedelta

import csv

NUM_STUDIOS = 1
NUM_ORDERS = 20

NUM_EDITORS = 2

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

"""

THERE APPEARS TO BE SOME ISSUES IN THE LIBRARY THAT DOESN"T ALLOW FOR LOTS OF NESTING, HENCE THIS SECTION IS COMMENTED OUT FOR NOW

def wait_until_working_hours(env):
    print("HELLo")
    # Keep adding delays until we're within business hours
    while not in_photographer_working_hours(env.now):
        # Bring down to week time frame
        time_mins = env.now % 10080

        print(f"TIME AFTER WEEK FRAME: {disp_time(time_mins)}")
        if True:
            print("HI")

        if time_mins > 6870:
            yield env.timeout(1)

        # If after 5pm on friday, wait until monday morning
        # if time_mins > 6780:
        #     # Get time difference between time and Monday 9am delay that time until monday morning
        #     yield env.timeout(10620 - time_mins)
    #     # Case where it's before 9am in the day
    #     elif (time_mins % 1440) < 540:
    #         # Wait the difference between now and 9am
    #         yield env.timeout(540 - (time_mins % 1440))
    #     # Case where it's after 5pm on a day
    #     elif (time_mins % 1440) > 1020:
    #         yield env.timeout(1980 - (time_mins % 1440))

"""

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

        # Check to see if we're at a specific hour mark otherwise wait until the next business hour

        if in_photographer_working_hours(env.now):
            print(f'{customer} in working hours')
            print(f'{(env.now % 60)}')
            if (env.now % 60) == 0:
                print(f'{customer} on the hour')
        
        while (in_photographer_working_hours(env.now) == False) and ((env.now % 60) != 0):
            # Bring timeframe down to the week scale so we can run a bunch of checks
            time_mins = env.now % days_to_mins(7)
            print("Customer ", customer,  " Can't get out at time ", disp_time(env.now))

            # If the current time is after friday 4pm, wait until monday morning at 9am
            if time_mins > days_to_mins(5) + hours_to_mins(16):
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

            

        # print(f"Current time before wait: {disp_time(env.now)}")
        # wait_until_working_hours(env)
        # print(f"Time after waiting until business hours: {disp_time(env.now)}")

        print(f'{customer} got out at {disp_time(env.now)}')

        # Check-in stage


        writer.writerow([f'{customer:05d};"PHOTOGRAPHER CHECKED IN";"{disp_time(env.now)}"'])

        if at_studio:
            checkin_status = generate_outcome(STUDIO_CHECK_IN)
        else:
            checkin_status = generate_outcome(LOCATION_CHECK_IN)

        if checkin_status == CHECK_IN_LATE:
            writer.writerow([f"{customer:05d}: CONTACTED CUSTOMER"])
        
        elif checkin_status == CHECK_IN_NO_SHOW:
            writer.writerow([f"{customer:05d}: CONTACTED CUSTOMER"])
            
            if generate_outcome(NO_SHOW_RESCHEDULED) == RESCHEDULED:
                continue
            else:
                break

        # Photos are uploaded
        writer.writerow([f"{customer:05d}: PHOTOS UPLOADED"])

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

        

    

    with fotof_studio.photographer.request() as request:
        yield request
        yield env.process(fotof_studio.take_photos(True, customer))

    

    with fotof_studio.editor.request() as request:
        yield request
        yield env.process(fotof_studio.edit_photos(True, customer))

    # Invoice stage


# Simulate the operation of the entire fotof studio for a list of orders
def simulate_fotof_studio(env, fotof_studio, orders: list, writer):
    for customer in orders:
        yield env.timeout(1)
        env.process(use_fotof(env, fotof_studio, customer, writer))


if __name__ == "__main__":
    # Create environment to be simulated
    env = simpy.Environment()

    # Create the different studios
    fotof_studios = []
    for i in range(NUM_STUDIOS):
        fotof_studios.append(Fotof_studio(env, get_num_photographers(), NUM_EDITORS))

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