# All the probabilities for each step

PERSONAL_OR_CORPORATE = [0.1, 0.9]

COROPRATE_BOOKING = [0.97, 0.01, 0.02]
PERSONAL_BOOKING = [0.925, 0.055, 0.02]

STUDIO_CHECK_IN = [0.77, 0.1, 0.13]
LOCATION_CHECK_IN = [0.95, 0.02, 0.03]

REMINDER_OF_PHOTOS = [0.75, 0.25]

CUSTOMER_AFTER_REMINDER = [0.25, 0.075, 0.675]

NEEDS_EDITING_INITIALLY = [0.5, 0.5]

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

# Function that generates outcome

def generate_outcome(*args) -> int:
    """
    Generates a certain outcome given a list of probabilities
    """
    
    # Quick sanity check to ensure probabilities add up to 1
    if args.sum != 1:
        raise ValueError

    r = random.random()

    for i in range(args):
        if r < args[0:i].sum:
            return i
    
    # If this point is reached, there is an error
    raise ValueError


    