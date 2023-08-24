import os
import time
import git

# Define the paths to your local Git repository and the CSV file
repo_path = 'C:\\Users\\USER\\Desktop\\github repo3\\raceboard'
csv_file = 'scanned_data_log.csv'

def commit_and_push_changes():
    # Initialize the Git repository
    repo = git.Repo(repo_path)

    # Check if the CSV file has changed
    if repo.is_dirty(path=csv_file):
        try:
            # Stage the CSV file
            repo.index.add([csv_file])

            # Commit the changes
            repo.index.commit("Auto commit: Update CSV")

            # Push to GitHub (replace 'main' with your branch name)
            repo.remotes.origin.push('main')

            print("Changes committed and pushed to GitHub.")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("No changes detected in the CSV file.")

def watch_csv_file():
    while True:
        # Check for changes in the CSV file at regular intervals
        commit_and_push_changes()
        time.sleep(30)  # Adjust the interval as needed (e.g., every 5 minutes)

if __name__ == "__main__":
    watch_csv_file()
