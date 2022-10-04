"""
This is a python eventlog generator for INFS3604
"""

import csv

from numpy import void

# TODO: UPDATE THIS VALUE
NUM_ORDERS_PER_LOC = 18000

# TODO: UPDATE THIS VALUE
NUM_LOCATIONS = 1

STEP_OUTPUTS = {
    'A':'DETAILS_ENTERED',
    'B':'BOOKINGS CANCELLED',
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

def create_path(order):
    for key in STEP_OUTPUTS.keys():
        order.append(key)

def create_entries(orders_list):
    for location in range(NUM_LOCATIONS):
        orders_list.append([])
        for order in range(NUM_ORDERS_PER_LOC):
            orders_list[location].append([])
            create_path(orders_list[location][order])
            



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
