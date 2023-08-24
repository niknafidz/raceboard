import os
import time
import subprocess

local_csv_path = r'C:\Users\USER\Desktop\github repo2\leaderboard2\scanned_data_log.csv'
remote_repo_url = 'https://github.com/niknafidz/leaderboard2.git'

def update_remote_csv():
    subprocess.run(['git', 'add', local_csv_path])
    subprocess.run(['git', 'commit', '-m', 'Update CSV file'])
    subprocess.run(['git', 'push', remote_repo_url, 'main'])

# Initialize last_contents
last_contents = None

while True:
    try:
        with open(local_csv_path, 'r') as file:
            file_contents = file.read()
            # Check for changes in the CSV file content
            # You could use additional logic to compare contents or timestamps
            if file_contents != last_contents:
                update_remote_csv()
                last_contents = file_contents
        time.sleep(10)  # Check every 10 seconds
    except KeyboardInterrupt:
        break

