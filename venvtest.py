import simpy
import random
from generate_events import *

import csv

NUM_STUDIOS = 1
NUM_ORDERS = 100

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

# HELPER FUNCTIONS 

def get_num_photographers():
    return random.randint(3,4)

def get_studio_or_location(is_personal):
    if not(is_personal):
        return AT_STUDIO
    else:
        return generate_outcome(PERSONAL_ON_LOCATION)


# Simulate the use of a fotof studio for a single customer
def use_fotof(env, fotof_studio, customer, writer):
    
    # Get info about the order 
    is_personal = bool(generate_outcome(PERSONAL_OR_CORPORATE))
    at_studio = bool(get_studio_or_location(is_personal))

    printed = False
    digital = False

    time = 0

    while True:

        # Booking stage
        while True:
            if is_personal:
                booking_status = generate_outcome(PERSONAL_BOOKING)
            else:
                booking_status = generate_outcome(COROPRATE_BOOKING)
            
            if booking_status == BOOKING_MADE:
                writer.writerow([f'{customer:05d};"DETAILS ENTERED";"2020-01-01T00:00:{time:02d}"'])
                break
            elif booking_status == BOOKING_CANCELLED:
                writer.writerow([f"{customer:05d}: DETAILS ENTERED"])
                writer.writerow([f"{customer:05d}: BOOKING CANCELLED"])
                return

        # Check-in stage

        writer.writerow([f"{customer:05d}: PHOTOGRAPHER CHECKED IN"])

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