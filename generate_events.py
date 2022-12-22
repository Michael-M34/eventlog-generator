import random

# All the probabilities for each step

PERSONAL_OR_CORPORATE = [0.1, 0.9]

PERSONAL_ON_LOCATION = [0.2, 0.8]

COROPRATE_BOOKING = [0.97, 0.01, 0.02]
PERSONAL_BOOKING = [0.925, 0.055, 0.02]

STUDIO_CHECK_IN = [0.77, 0.1, 0.13]
LOCATION_CHECK_IN = [0.95, 0.02, 0.03]

REMINDER_OF_PHOTOS = [0.75, 0.25]

CUSTOMER_AFTER_REMINDER = [0.25, 0.075, 0.675]

NEEDS_EDITING_INITIALLY = [0.5, 0.5]

NEEDS_TO_TALK_WITH_TECHNICIAN = [0.25, 0.75]

NEEDS_ANOTHER_TECHNICIAN_TALK = [0.1, 0.9]

GETTING_PRINTED = [0.1, 0.9]

GETTING_DIGITAL = [0.95, 0.05]

INVOICE_REMINDER = [0.15, 0.85]

DIGITAL_OR_FEE_STRAIGHT_TO_UPDATE = [0.95, 0.05]

PRINTED_STRAIGHT_TO_UPDATE = [0.5, 0.5]

SEND_PRINTOUT_OR_PICKUP = [0.9, 0.1]

PHOTOS_REMINDER_SENT = [0.1, 0.9]

# Special names for each outcome (to make code easier to read)

# Personal or corporate orders
IS_PERSONAL = 1
IS_CORPORATE = 0

# On location or at a studio
ON_LOCATION = 0
AT_STUDIO = 1

# Booking step outcomes
BOOKING_MADE = 0
BOOKING_CANCELLED = 1
BOOKING_REPEATED = 2

# Check-in step outcomes
CHECK_IN_SUCCESSFUL = 0
CHECK_IN_LATE = 1
CHECK_IN_NO_SHOW = 2

# Photo reminder 
CUSTOMER_ORDERS = 0
CUSTOMER_REMINDED = 1

# Customer after the reminder
CUSTOMER_ORDERS = 0
CUSTOMER_INVOICED_BUT_ORDERS = 1
CUSTOMER_INVOICED = 2

# Initial editing
EDITING_REQUIRED = 0
EDITING_NOT_REQUIRED = 1

# When a customer requires editing, whether they need to speak to a technician or not
# ALSO IS USED FOR REPEAT STEP
TECHNICIAN_REQUIRED = 0
TECHNICIAN_NOT_REQUIRED = 1

# Printed/Digital Photos

GETTING_PRINTED = 0
NOT_GETTING_PRINTED = 1

GETTING_DIGITAL = 0
NOT_GETTING_DIGITAL = 1

# For the invoice step

NEEDS_INVOICE_REMINDER = 0
DOESNT_NEED_INVOICE_REMINDER = 1

# Whether order is updated immediately or not

ORDER_UPDATED = 0
ORDER_NOT_UPDATED = 1

# Whether printout is sent or photos are picked up

PRINTOUT_SENT = 0
PRINTS_TO_BE_PICKED_UP = 1

# Whether reminder is sent or not (for pickup)

PICKUP_REMINDER_SENT = 0
PICKUP_SUCCESSFUL = 1

# Function that generates outcome

def generate_outcome(probabilites) -> int:
    """
    Generates a certain outcome given a list of probabilities
    """
    
    # Quick sanity check to ensure probabilities add up to 1
    if sum(probabilites) != 1:
        raise ValueError

    r = random.random()

    for i in range(len(probabilites)):
        if r < sum(probabilites[0:i+1]):
            return i
    
    # If this point is reached, there is an error
    raise ValueError


    