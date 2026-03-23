#List of library imports.
import os
import time
import hashlib
from datetime import datetime

LOG_FILE = "submission_log.txt"
SUBMISSION_DIR = "submissions"
LOGIN_ATTEMPTS = {}
FAILED_ATTEMPTS = {}

#This creates the submissions directory if it doesn't already exist.
os.makedirs(SUBMISSION_DIR, exist_ok=True)

def log_action(message):
    #This function logs actions to the submission_log.txt file with a timestamp for each event.
    with open(LOG_FILE, "a") as f:
        f.write(f"{datetime.now()} - {message}\n")


def is_valid_file(filepath):
    #This checks if the file exists, if it doesn't, then it rejects the submission and logs this action.
    if not os.path.exists(filepath):
        print("File does not exist.")
        return False

    #This checks if the file type is either PDF or DOCX, if it isn't, then it rejects the submission and logs this action.
    if not (filepath.endswith(".pdf") or filepath.endswith(".docx")):
        print("Invalid file type. Only PDF and DOCX allowed.")
        return False

    #This checks if the file size is under 5MB, if it isn't, then it rejects the submission and logs this action.
    if os.path.getsize(filepath) > 5 * 1024 * 1024:
        print("File too large. Must be under 5MB.")
        return False
    return True


#This function calculates the MD5 hash of a file, which is used to check for duplicate content in the submissions directory.
def get_file_hash(filepath):
    hasher = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(4096):
            hasher.update(chunk)
    return hasher.hexdigest()

#This function handles the submission of assignments, it checks for duplicate filenames and file content in the submissions directory, if it finds a duplicate filename or file content, then it rejects the submission and logs this action. If the submission is successful, it saves the file to the submissions directory and logs this action as well.
def submit_assignment():
    student_id = input("Enter Student ID: ")
    filepath = input("Enter file path: ")

    if not is_valid_file(filepath):
        return

    filename = os.path.basename(filepath)
    new_path = os.path.join(SUBMISSION_DIR, filename)

    new_hash = get_file_hash(filepath)

    #This checks for duplicate filenames and file content in the submissions directory, if it finds a duplicate filename or file content, then it rejects the submission and logs this action.
    for file in os.listdir(SUBMISSION_DIR):
        existing_path = os.path.join(SUBMISSION_DIR, file)
        if file == filename:
            print("Duplicate filename detected. Submission rejected.")
            log_action(f"{student_id} - Duplicate filename rejected: {filename}")
            return

        if get_file_hash(existing_path) == new_hash:
            print("Duplicate file content detected. Submission rejected.")
            log_action(f"{student_id} - Duplicate content rejected: {filename}")
            return

    # Save file
    with open(filepath, "rb") as src, open(new_path, "wb") as dst:
        dst.write(src.read())

    print("Submission successful.")
    log_action(f"{student_id} - Submitted: {filename}")


def check_submission():
    filename = input("Enter filename to check: ")

    #This checks if the file exists in the submissions directory, if it does, then it outputs that the file has already been submitted, if it doesn't, then it outputs that the file was not found.
    if filename in os.listdir(SUBMISSION_DIR):
        print("File has already been submitted.")
    else:
        print("File not found.")


def list_submissions():
    files = os.listdir(SUBMISSION_DIR)

    #This checks if there are any files in the submissions directory, if there aren't, then it outputs that there are no submissions yet.
    if not files:
        print("No submissions yet.")
        return

    #This lists all the submitted files in the submissions directory.
    print("\nSubmitted Files:")
    for f in files:
        print(f)


def login():
    username = input("Enter username: ")
    current_time = time.time()

    #This initialises the login attempts and failed attempts for the user if they don't already exist in the respective dictionaries.
    if username not in FAILED_ATTEMPTS:
        FAILED_ATTEMPTS[username] = 0
        LOGIN_ATTEMPTS[username] = []

    #This checks if the user has had 3 or more failed login attempts, if they have, then it locks the account and logs this action.
    if FAILED_ATTEMPTS[username] >= 3:
        print("Account locked due to multiple failed attempts.")
        log_action(f"{username} - Account locked")
        return

    password = input("Enter password: ")

    #This is a very basic login system for demonstration purposes. In a real system, you would want to securely store and hash passwords, and implement proper authentication mechanisms.
    if password == "admin":
        print("Login successful.")
        FAILED_ATTEMPTS[username] = 0
        log_action(f"{username} - Successful login")
    else:
        print("Login failed.")
        FAILED_ATTEMPTS[username] += 1
        LOGIN_ATTEMPTS[username].append(current_time)
        log_action(f"{username} - Failed login")

        #This checks if there have been 3 or more login attempts within the last 60 seconds, if there have been, then it logs this as suspicious activity.
        recent_attempts = [t for t in LOGIN_ATTEMPTS[username] if current_time - t < 60]
        if len(recent_attempts) >= 3:
            print("Suspicious activity detected (multiple attempts in 60s).")
            log_action(f"{username} - Suspicious login activity")


def exit_system():
    #Confirms with the user if they want to exit the system, if they say yes, then it exits, if they say no, then it returns to the main menu.
    confirm = input("Are you sure you want to exit? (Y/N): ")
    if confirm.lower() == "y":
        print("Exiting system...")
        exit()


def main():
    #Infinite loop to keep the system running until the user decides to exit.
    while True:
        print("\n===== SECURE SUBMISSION SYSTEM =====")
        print("1. Submit Assignment")
        print("2. Check Submission")
        print("3. List Submissions")
        print("4. Simulate Login Attempt")
        print("5. Exit")

        choice = input("Select an option: ")

        if choice == "1":
            submit_assignment()
        elif choice == "2":
            check_submission()
        elif choice == "3":
            list_submissions()
        elif choice == "4":
            login()
        elif choice == "5":
            exit_system()
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()