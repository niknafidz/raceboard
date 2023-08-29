import os
import time
import subprocess

# Set the path to your local repository and CSV file
repo_path = 'C:\\Users\\USER\\Desktop\\githubrepo4\\raceboard'
csv_file = 'scanned_data_log.csv'

while True:
    # Check if the CSV file has changed
    if os.path.exists(os.path.join(repo_path, csv_file)):
        # Add, commit, and push changes
        subprocess.call(['git', 'add', csv_file], cwd=repo_path)
        subprocess.call(['git', 'commit', '-m', 'Auto-update CSV'], cwd=repo_path)
        subprocess.call(['git', 'push', 'origin', 'main'], cwd=repo_path)

    # Sleep for a certain interval (e.g., 1 hour)
    time.sleep(60)  # 3600 seconds = 1 hour


