"""
This is a python eventlog generator for INFS3604
"""


import csv

LOCATIONS = []

def add_to_queue():
    pass



if __name__ == "__main__":
    
    print("Starting...")

    with open('eventlog.csv', 'w') as f:
        writer = csv.writer(f)

        writer.writerow(['Line here'])

        f.close()
