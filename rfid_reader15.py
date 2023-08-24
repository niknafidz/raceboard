import csv
import serial
import datetime
import time

def filter_non_printable(s):
    # Filter out non-printable characters from the string
    return ''.join(c for c in s if c.isprintable())

def load_rfid_names_from_csv(filename):
    rfid_names = {}
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rfid_names[row['Card Code']] = row['Name']
    return rfid_names

def load_rfid_motor_types_from_csv(filename):
    rfid_motor_types = {}
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rfid_motor_types[row['Card Code']] = row['Motor Type']
    return rfid_motor_types

def update_lap_data(csv_filename, tag_code, laptime, scan_count):
    # Read the existing CSV data
    rows = []
    with open(csv_filename, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append(row)

    # Update or create a new row for the tag
    for row in rows:
        if row['Card Code'] == tag_code:
            row['Lap Time'] = laptime
            row['Scan Count'] = scan_count

    # Write the updated data back to the CSV file
    fieldnames = ['Card Code', 'Name', 'Total Time', 'Lap Time', 'Scan Count']
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def seconds_to_minutes_and_seconds(seconds):
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:02}"

def format_time(seconds):
    # Convert seconds to hours, minutes, and seconds format
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

def log_data(scanned_time, tag_code, name, motor_type, laptime, totaltime, format_time_laptime, format_time_totaltime, scan_count):
    # Append the data to a CSV file for data logging
    with open('scanned_data_log.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([scanned_time, tag_code, name, motor_type, laptime, totaltime, format_time_laptime, format_time_totaltime, scan_count])

ser = serial.Serial('COM2', baudrate=9600, timeout=0.2)  # Update to use COM7

# Load RFID names from the CSV file
rfid_names = load_rfid_names_from_csv('rfid_names.csv')

# Load RFID names from the CSV file
rfid_motor_types = load_rfid_motor_types_from_csv('rfid_names.csv')

# Display instructions to the user
print("Type 'start' and press 'Enter' to start the race.")
print("Type 'finish' and press 'Enter' at any time to finish the race.")

user_input = input("Enter a command: ")

if user_input.lower() == 'start':
    starttime = time.time()
    lasttime = {}
    scan_counts = {}
    print("*"*20)
    print("Race has started!")
    print("*"*20)

    try:
        while True:
            data = ser.readline().decode('utf8', errors='ignore').strip()
            if data:
                # Filter out non-printable characters before printing the data
                filtered_data = filter_non_printable(data)
                tag_code = filtered_data[:-1]  # Remove the last two characters '_Y'

                # Look up the name corresponding to the RFID code from the dictionary
                name = rfid_names.get(tag_code, "Unknown")

                # Look up the motor type corresponding to the RFID code from the dictionary
                motor_type = rfid_motor_types.get(tag_code, "Unknown")

                # Get the current date and time
                scanned_time = datetime.datetime.now()

                # The current total time
                totaltime = round((time.time() - starttime), 2)

                # The current lap time
                laptime = round((time.time() - lasttime.get(tag_code, starttime)), 2)
                
                

                # Update the scan count for the tag
                scan_counts[tag_code] = scan_counts.get(tag_code, 0) + 1

                print("Scanned RFID Tag:", tag_code)
                print("Name:", name)
                print("Motor Type:", motor_type)
                print("Total Time:", format_time(totaltime))
                print("Lap Time:", format_time(laptime))
                print("Number of laps for", name + ":", scan_counts[tag_code])
                print("*"*20)

                # Log the data to a file
                log_data(scanned_time, tag_code, name, motor_type, laptime, totaltime, format_time(laptime), format_time(totaltime), scan_counts[tag_code])

                # Update the last scan time for lap time calculation
                lasttime[tag_code] = time.time()

    except KeyboardInterrupt:
        ser.close()

else:
    print("Race not started. Exiting.")
