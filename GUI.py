import PySimpleGUI as sg
import serial
import threading
import serial.tools.list_ports
import time
import datetime
import csv
import os

racer_info = {}

def detect_com_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def format_time(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

def save_data(racer_info, scanned_time, tag_code, name, motor_type, laptime, totaltime, format_time_laptime, format_time_totaltime, scan_count):
    with open('scanned_data_log.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([scanned_time, tag_code, name, motor_type, laptime, totaltime, format_time_laptime, format_time_totaltime, scan_count])

    if tag_code in racer_info:
        existing_racer = racer_info[tag_code]
        if scan_count > existing_racer['scan_count']:
            existing_racer["name"] = name
            existing_racer["motor_type"] = motor_type
            existing_racer["totaltime"] = totaltime
            existing_racer["laptime"] = laptime
            existing_racer["format_time_totaltime"] = format_time_totaltime
            existing_racer["format_time_laptime"] = format_time_laptime
            existing_racer["scan_count"] = scan_count
    elif tag_code not in racer_info:
        racer_info[tag_code] = {
            "name": name,
            "motor_type": motor_type,
            "totaltime": totaltime,
            "laptime": laptime,
            "format_time_totaltime": format_time_totaltime,
            "format_time_laptime": format_time_laptime,
            "scan_count": scan_count,
        }
    return racer_info  # Return updated racer_info

def update_tag_number():
    global is_running
    while is_running:
        if ser.in_waiting:
            data = ser.read(46)
            hex_data = data.hex().upper()
            filtered_data = hex_data[18:-4]
            if len(filtered_data)>24:
                filtered_data = filtered_data[0:24]
            print("Scanned Tag: ", filtered_data)
            window['-TAG_NUMBER-'].update(filtered_data)

def load_data_from_csv(file_path):
    rfid_names = {}
    rfid_motor_types = {}

    try:
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                rfid_names[row['Card Code']] = row['Name']
                rfid_motor_types[row['Card Code']] = row['Motor Type']

    except Exception as e:
        sg.popup_error(f"Error loading data from CSV: {str(e)}")

    return rfid_names, rfid_motor_types

stop_store_race_thread = False

def store_race_info_thread():
    starttime = time.time()
    lasttime = {}
    scan_counts = {}
    last_scan_time = {}
    scanned_time = None
    try:
        time.sleep(20)
        ser = serial.Serial(selected_port, baudrate=57600, timeout=1)
        while not stop_store_race_thread:
            data = ser.read(46)
            if data:
                hex_data = data.hex().upper()
                tag_code = hex_data[18:-4]

                current_time = datetime.datetime.now()
                global racer_info
                if len(tag_code) > 24:
                    tag_code = tag_code[:24]

                if tag_code in last_scan_time:
                    # Calculate the time elapsed since the last scan
                    time_elapsed = current_time - last_scan_time[tag_code]

                    # Check if at least one minute has passed
                    if time_elapsed >= datetime.timedelta(minutes=2):
                        name = rfid_names.get(tag_code, "Unknown")
                        motor_type = rfid_motor_types.get(tag_code, "Unknown")

                        scanned_time = datetime.datetime.now()

                        totaltime = round((time.time() - starttime), 2)
                        laptime = round((time.time() - lasttime.get(tag_code, starttime)), 2)

                        scan_counts[tag_code] = scan_counts.get(tag_code, 0) + 1

                        print("Scanned RFID Tag:", tag_code)
                        print("Name:", name)
                        print("Motor Type:", motor_type)
                        print("Total Time:", format_time(totaltime))
                        print("Lap Time:", format_time(laptime))
                        print("Number of laps for", name + ":", scan_counts[tag_code])
                        print("*" * 20)
                        last_scan_time[tag_code] = current_time  # Update the last scan time
                        racer_info = save_data(racer_info, scanned_time, tag_code, name, motor_type, laptime, totaltime,
                                       format_time(laptime), format_time(totaltime), scan_counts[tag_code])
                        sorted_racers = sorted(racer_info.values(), key=lambda x: (-x['scan_count'], x['totaltime']))
                        sorted_racers_as_list = [
                            [rank + 1, racer['name'], racer['motor_type'], racer['format_time_totaltime'], racer['format_time_laptime'], racer['scan_count']]
                            for rank, racer in enumerate(sorted_racers)
                        ]
                        lasttime[tag_code] = time.time()
                        window_race['-RACE_INFO-'].update(values=sorted_racers_as_list)

                else:
                    # If the tag hasn't been scanned before, print it and record the time
                    if tag_code in rfid_names:
                        name = rfid_names.get(tag_code)
                        motor_type = rfid_motor_types.get(tag_code)

                        scanned_time = datetime.datetime.now()

                        totaltime = round((time.time() - starttime), 2)
                        laptime = round((time.time() - lasttime.get(tag_code, starttime)), 2)

                        scan_counts[tag_code] = scan_counts.get(tag_code, 0) + 1

                        print("Scanned RFID Tag:", tag_code)
                        print("Name:", name)
                        print("Motor Type:", motor_type)
                        print("Total Time:", format_time(totaltime))
                        print("Lap Time:", format_time(laptime))
                        print("Number of laps for", name + ":", scan_counts[tag_code])
                        print("*" * 20)
                        last_scan_time[tag_code] = current_time
                        racer_info = save_data(racer_info, scanned_time, tag_code, name, motor_type, laptime, totaltime,
                                       format_time(laptime), format_time(totaltime), scan_counts[tag_code])
                        sorted_racers = sorted(racer_info.values(), key=lambda x: (-x['scan_count'], x['totaltime']))
                        sorted_racers_as_list = [
                            [rank + 1, racer['name'], racer['motor_type'], racer['format_time_totaltime'], racer['format_time_laptime'], racer['scan_count']]
                            for rank, racer in enumerate(sorted_racers)
                        ]
                        lasttime[tag_code] = time.time()
                        window_race['-RACE_INFO-'].update(values=sorted_racers_as_list)

    except KeyboardInterrupt:
        ser.close()

# First code snippet: Select COM port
sg.theme('DarkGrey10')

layout_racer = [
    [sg.Text('Plug in your UHF RFID into port.')],
    [sg.Text('Choose from dropdown the port of your UHF RFID:'), sg.OptionMenu(values=detect_com_ports(), key="-PORT-")],
    [sg.Button('Continue'), sg.Button('Exit')]
]

window_racer = sg.Window('RFID Racing Leaderboard - Port Selection', layout_racer)

selected_port = None
open_registration = False
race_started = False

while True:
    event_port, values_port = window_racer.read()
    if event_port in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event_port == 'Continue':
        selected_port = values_port["-PORT-"]
        open_registration = True
        break

window_racer.close()

# Open the Registration window only if the flag is set
if open_registration:
    
    # Second code snippet: Update and Add Racer
    sg.theme('DarkGrey10')

    # Create headers for the table
    table_headers = ['Tag Code', 'Name', 'Motor Type']

    # Create an empty data list for the table
    table_data = []
    working_directory = os.getcwd()
    layout = [
        [sg.Text('Scan one tag at a time and input name and motor type for the corresponding tag and click \'Add Racer\'.')],
        [sg.Column([[sg.Text('Tag number:')],[sg.Text('Enter full name:')],[sg.Text('Motor type:')]]),sg.Column([[sg.InputText('', key='-TAG_NUMBER-', do_not_clear=False, size=(50, 1))],[sg.Input(key="-NAME-", do_not_clear=False, size=(50, 1))],[sg.OptionMenu(values=['400 cc', '600 cc', '1000 cc'], default_value='400 cc', key='-MOTOR_TYPE-')]]), sg.Push(), sg.Button('Add Racer'), sg.Button('Exit')]
    ]

    rfid_names = {}
    rfid_motor_types = {}

    layout += [
        [sg.Table(values=table_data, headings=table_headers, auto_size_columns=False,
          justification='left', num_rows=15, display_row_numbers=False, select_mode=sg.TABLE_SELECT_MODE_EXTENDED, key='-RACER_TABLE-', col_widths=[30, 25, 10])],
        [sg.Button('Delete Racer'), sg.Push(), sg.Text('Filter by Motor Type:'), sg.Combo(['All', '400 cc', '600 cc', '1000 cc'], default_value='All', key='-FILTER_TYPE-'), sg.Button('Apply Filter')],
        [sg.Text('Or browse for the CSV file containing the tag code, name, and motor type and click \'Submit\'.')],
        [sg.InputText(key='-FILE_PATH-',size=(62, 1)), sg.FileBrowse(initial_folder=working_directory, file_types = [("CSV Files", "*.csv")]), sg.Button('Submit')],
        [sg.Push(),sg.Column([[sg.Button('Start Race', font=('Helvetica', 15))]], element_justification='center'),sg.Push()]
    ]

    window = sg.Window('Registration', layout)

    ser = serial.Serial(selected_port, baudrate=57600, timeout=1)
    is_running = True

    update_thread = threading.Thread(target=update_tag_number)
    update_thread.start()

    while True:
        event, values = window.read()
        csv_file_path = ''
        if event in (sg.WIN_CLOSED, 'Exit'):
            is_running = False
            window.close()
            break
        elif event == 'Start Race':
            is_running = False
            race_started = True
            ser.close()
            window.close()
            break
        elif event == 'Add Racer':
            rfid_number = values['-TAG_NUMBER-']
            motor_type = values['-MOTOR_TYPE-']

            if rfid_number:
                if rfid_number in rfid_names:
                    sg.popup(f"This {rfid_number} has already been added! Please scan a new tag.")
                else:
                    rfid_names[rfid_number] = values['-NAME-']
                    rfid_motor_types[rfid_number] = motor_type
                    table_data.append([rfid_number, values['-NAME-'], motor_type])
                    window['-RACER_TABLE-'].update(values=table_data)
        elif event == 'Delete Racer':
            selected_rows = values['-RACER_TABLE-']
            if selected_rows:
                for row_index in selected_rows:
                    rfid_number = table_data[row_index][0]
                    del rfid_names[rfid_number]
                    del rfid_motor_types[rfid_number]
                
                updated_data = [row for index, row in enumerate(table_data) if index not in selected_rows]
                table_data = updated_data
                window['-RACER_TABLE-'].update(values=table_data)
        elif event == 'Submit':
            csv_address = values['-FILE_PATH-']
            rfid_names, rfid_motor_types = load_data_from_csv(csv_address)
            table_data = [[rfid, name, motor_type] for rfid, name in rfid_names.items() for motor_type in [rfid_motor_types.get(rfid, "")]]
            window['-RACER_TABLE-'].update(values=table_data)
        elif event == 'Apply Filter':
            filter_type = values['-FILTER_TYPE-']
            if filter_type == 'All':
                filtered_data = table_data
            else:
                filtered_data = [row for row in table_data if row[2] == filter_type]
            window['-RACER_TABLE-'].update(values=filtered_data)
        

# Start Race Window
if race_started:
    with open('scanned_data_log.csv', 'w', newline='') as csvfile:
        header = ['Scanned Time', 'Tag Code', 'Name', 'Motor Type', 'Lap Time (sec)', 'Total Time (sec)', 'Lap Time (hh:mm:ss)', 'Total Time (hh:mm:ss)', 'Lap Count']
        writer = csv.writer(csvfile)
        writer.writerow(header)
        print("CSV file created.")
    
    sg.theme('DarkGrey10')

    # Create headers for the table
    table_headers = ['Rank', 'Name', 'Motor Type', 'Total Time', 'Lap Time', 'Lap Count ']

    # Create an empty data list for the table
    table_data = []

    layout_race = [
        [sg.Push(),sg.Text('00:00:00', size=(10, 1), justification='center', font=('Helvetica', 36), key='-TIMER-'),sg.Push()],
        [sg.Table(values=table_data, headings=table_headers, auto_size_columns=False,
              justification='center', num_rows=15, display_row_numbers=False, key='-RACE_INFO-', font=('Helvetica', 15), col_widths=[5, 25, 10, 10, 10, 10])],
        [sg.Button('Start Race'), sg.Button('End Race'), sg.Button('Exit')]
    ]

    window_race = sg.Window('Start Race', layout_race, resizable=True)

    timer_running = False
    start_time = 0

    def update_timer():
        global timer_running
        global start_time

        while timer_running:
            elapsed_time = int(time.time() - start_time)
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f'{hours:02}:{minutes:02}:{seconds:02}'
            window_race['-TIMER-'].update(time_str)
            time.sleep(1)

    timer_thread = None

    while True:
        event, values = window_race.read()

        if event == 'End Race':
            if timer_thread:
                timer_running = False
                timer_thread.join()

            stop_store_race_thread = True

        elif event == 'Start Race':
            if not timer_running:
                start_time = time.time()
                timer_running = True
                timer_thread = threading.Thread(target=update_timer, daemon=True)
                timer_thread.start()

                # Start the store_race_info_thread
                store_race_thread = threading.Thread(target=store_race_info_thread, daemon=True)
                store_race_thread.start()

        # Handle the message from the store_race_info_thread
        elif event in (sg.WIN_CLOSED, 'Exit'):
            break

    window_race.close()
    if timer_thread:
        timer_running = False
        timer_thread.join()
