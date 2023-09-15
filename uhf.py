import serial
import time
from datetime import datetime, timedelta

# Replace 'COMx' with the correct COM port assigned to your RFID scanner.
# Check the Device Manager to find the COM port name.
ser = serial.Serial('COM2', baudrate=57600, timeout=1)

# Define a dictionary to store the last scanned time for each tag
last_scan_time = {}

try:
    while True:
        data = ser.read(46)  # Read a chunk of data from the serial port

        if data:
            # Convert the received data to a hexadecimal string
            hex_data = data.hex().upper()
            tag_code = hex_data[18:-4]
            
            # Get the current time
            current_time = datetime.now()

            if len(tag_code) > 24:
                tag_code = tag_code[:24]

            # Check if the tag has been scanned before
            if tag_code in last_scan_time:
                # Calculate the time elapsed since the last scan
                time_elapsed = current_time - last_scan_time[tag_code]

                # Check if at least one minute has passed
                if time_elapsed >= timedelta(minutes=2):
                    print("Received Data from tag:", tag_code)
                    last_scan_time[tag_code] = current_time  # Update the last scan time
                      # Wait for 10 seconds
                
            else:
                # If the tag hasn't been scanned before, print it and record the time
                print("Received Data from tag:", tag_code)
                last_scan_time[tag_code] = current_time
                  # Wait for 10 seconds

except KeyboardInterrupt:
    ser.close()
