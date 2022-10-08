"""
This is a python eventlog generator for INFS3604
"""

import csv
from random import random

from numpy import void

# TODO: UPDATE THIS VALUE
NUM_ORDERS_PER_LOC = 3780

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
    'V':'EMAIL LINK TO PHOTOS SENT'
}

def invoice_handler(order_steps: list,atstudio,printed_photos,digital_photos):
    order_steps.append('E')

    # Invoice reminder + collections step
    invoice_reminder_count = 0
    while True:
        r=random()
        if r<0.15:
            invoice_reminder_count+=1
            if invoice_reminder_count > 5:
                order_steps.append('O')
                print("Collections order")
                return
            order_steps.append('N')
        else:
            break

    # People are now paying
    if printed_photos:
        r=random()
        if r < 0.50:
            order_steps.append('P')
            order_steps.append('Q')
        else:
            order_steps.append('Q')
            r=random()
            if r < 0.90:
                order_steps.append('S')
            else:
                while True:
                    r=random()
                    if r<0.1:
                        order_steps.append('T')
                    else:
                        break

    else:
        r=random()
        if r < 0.05:
            order_steps.append('P')
        order_steps.append('Q')

    if (printed_photos==0 and digital_photos==0):
        order_steps.append('R')

    if digital_photos:
        order_steps.append('V')

    order_steps.append('U')

    
        

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
                    invoice_handler(order_steps,atstudio,0,0)
                    return
    else:
        if r < 0.05:
            order_steps.append('D')
            if r < 0.02:
                r=random()
                if r < 0.35:
                    create_path(order_steps, atstudio)
                    return
                else:
                    invoice_handler(order_steps,atstudio,0,0)
                    return

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
                invoice_handler(order_steps, atstudio,0,0)
                return


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
        
        # Photos edited
        order_steps.append('K')

    # Printing / Digital step
    getting_printed = 1
    getting_digital = 1
    r=random()
    if r < 90:
        getting_printed = 0
    elif r < 95:
        getting_digital = 0

    if getting_printed:
        order_steps.append('L')

    if getting_digital:
        order_steps.append('M')

    invoice_handler(order_steps, atstudio, getting_printed, getting_digital)

def get_personal_or_corporate():
    # 10% orders are corporate
    # 90% are personal
    # 1% of corporate orders are cancelled
    # 5.5% of personal orders are cancelled
    # 100% of corporate orders are on location
    # 10% of personal orders are on location
    r=random()
    if r < 0.1:
        return 1
    else:
        return 0

def get_location_or_studio(is_corporate):

    if is_corporate:
        return 0
    else:
        r=random()
        if r < 0.9:
            return 1
        else:
            return 0



def create_order_object(order_id):
    is_corporate = get_personal_or_corporate()
    return {
        'order_num': order_id,
        'path': [],
        'is_corporate': is_corporate,
        'at_studio': get_location_or_studio(is_corporate),
        'printed_photos': 0,
        'digital_photos': 0,
        'invoice_value': 0,
        'booking_time': 0,
    }


def create_entries(orders_list):
    order_list_num = 1
    for location in range(NUM_LOCATIONS):
        orders_list.append([])
        for order in range(NUM_ORDERS_PER_LOC):
            orders_list[location].append(create_order_object(order_list_num))
            create_path(orders_list[location][order]['path'], orders_list[location][order]['at_studio'])
            order_list_num+=1


if __name__ == "__main__":
    
    print("Running eventlog.py")

    orders_list = []
    create_entries(orders_list)

    with open('eventlog.csv', 'w') as f:
        writer = csv.writer(f)

        corporate_orders = 0

        for location in orders_list:
            for order in location:
                for step in order['path']:
                    writer.writerow([f'{order["order_num"]};{STEP_OUTPUTS[step]}'])


        f.close()
