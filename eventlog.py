"""
This is a python eventlog generator for INFS3604
"""

import csv
from random import random

from numpy import void

# TODO: UPDATE THIS VALUE
NUM_ORDERS_PER_LOC = 3600

# TODO: UPDATE THIS VALUE
NUM_LOCATIONS = 1

STEP_OUTPUTS = {
    'A':'DETAILS ENTERED',
    'B':'BOOKING CANCELLED',
    'C':'PHOTOGRAPHER CHECKED IN',
    'D':'CONTACTED CUSTOMER',
    'E':'INVOICE ISSUED',
    'F':'PHOTOS UPLOADED',
    'G':'CUSTOMER NOTIFIED OF GALLERY',
    'H':'CUSTOMER REMINDED OF GALLERY',
    'I':'ORDER PLACED',
    'J':'CUSTOMER ASKED FOR INFORMATION',
    'K':'PHOTOS EDITED',
    'L':'PHOTOS PRINTED',
    'M':'PHOTOS UPLOADED TO DROPBOX',
    'N':'INVOICE REMINDER SENT',
    'O':'INVOICE REFERRED TO COLLECTIONS',
    'P':'INSTORE PAYMENT PROCESSED',
    'Q':'ORDER UPDATED',
    'R':'FEE RECEIVED',
    'S':'PHOTOS SHIPPED',
    'T':'REMINDER TO PICK UP PHOTOS SENT',
    'U':'ORDER CLOSED',
}

def invoice_handler(order_steps: list,atstudio,printed_photos):
    order_steps.append('E')

def create_path(order_steps: list, atstudio):
    """
    Creates the path for the order to take
    """
    
    # DETAILS ENTERED STEP

    order_steps.append('A')

    while (True):
        r=random()

        if r < 0.94:
            break
        elif r < 0.99:
            order_steps.append('B')
            return


    # Check-in step
    order_steps.append('C')

    
    # Contact customer step
    r=random()
    if atstudio:
        if r < 0.23:
            order_steps.append('D')
            if r < 0.13:
                r=random()
                if r < 0.35:
                    create_path(order_steps, atstudio)
                    return
                else:
                    invoice_handler(order_steps,atstudio,0)
    else:
        if r < 0.05:
            order_steps.append('D')
            if r < 0.02:
                r=random()
                if r < 0.35:
                    create_path(order_steps, atstudio)
                    return
                else:
                    invoice_handler(order_steps,atstudio,0)

    # Uploaded photos and notified customer
    order_steps.append('F')
    order_steps.append('G')

    # Customer reminded step
    r=random()
    if r < 0.25:
        order_steps.append('H')
        r=random()
        if r < 0.75:
            if r < 0.075:
                order_steps.append('E')
            else:
                invoice_handler(order_steps, atstudio,0)


    # Placing order step
    order_steps.append('I')

    # Editing step
    r=random()
    if r < 0.5:
        r=random()
        if r < 0.25:
            while True:
                order_steps.append('J')
                r=random()
                if r < 0.9:
                    break

        order_steps.append('K')

    

    

            

    


def create_entries(orders_list):
    for location in range(NUM_LOCATIONS):
        orders_list.append([])
        for order in range(NUM_ORDERS_PER_LOC):
            orders_list[location].append([])
            create_path(orders_list[location][order], 1)
            



if __name__ == "__main__":
    
    print("Running eventlog.py")

    orders_list = []
    create_entries(orders_list)

    with open('eventlog.csv', 'w') as f:
        writer = csv.writer(f)

        for location in orders_list:
            for order in location:
                for step in order:
                    writer.writerow([STEP_OUTPUTS[step]])


        f.close()
