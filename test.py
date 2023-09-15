import csv
import datetime
import time

file_name = 'scanned_data_log.csv'

# Get the current maximum counter value from the existing CSV (if any)
try:
    with open(file_name, mode='r') as file:
        reader = csv.reader(file)
        lines = list(reader)
        if len(lines) > 1:  # Check if there is data in the CSV (excluding the header)
            last_row = lines[-1]
            if len(last_row) >= 9:  # Check if the row has at least 9 elements
                last_counter = int(last_row[-1])
            else:
                last_counter = 0
        else:
            last_counter = 0
except FileNotFoundError:
    last_counter = 0

while True:
    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)

        # Generate a new row of data
        time_str = "45:27.9"
        ID = "0008338911"
        name = "Anuar"
        category = "1000 cc"
        speed1 = "488.09"
        speed2 = "1759.76"  # Change this value as needed
        time1 = "0:00:19"
        time2 = "0:00:19"
        
        last_counter += 1  # Increment the counter sequentially

        writer.writerow([time_str, ID, name, category, speed1, speed2, time1, time2, last_counter])

    print(f'Added a new row with counter {last_counter} to {file_name}')
    time.sleep(180)  # Wait for one minute before adding the next row
