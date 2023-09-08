import csv
import subprocess

# Specify the path to your CSV file and the remote repository URL
csv_file_path = 'scanned_data_log.csv'
remote_repo_url = 'https://github.com/niknafidz/raceboard.git'  # Replace with your repo URL

try:
    # Step 1: Delete the content of the CSV file
    with open(csv_file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows([])  # Write an empty list to clear the content

    print(f"Content of '{csv_file_path}' has been deleted.")

    # Step 2: Commit the changes to the local Git repository
    commit_message = "Deleted CSV file content"
    subprocess.run(['git', 'add', csv_file_path])
    subprocess.run(['git', 'commit', '-m', commit_message])

    print(f"Changes committed to the local Git repository: {commit_message}")

    # Step 3: Push the changes to the remote Git repository
    subprocess.run(['git', 'push', 'origin', 'main'])  # Replace 'main' with your branch name

    print("Changes pushed to the remote Git repository.")
except FileNotFoundError:
    print(f"'{csv_file_path}' does not exist.")
except Exception as e:
    print(f"An error occurred: {str(e)}")
