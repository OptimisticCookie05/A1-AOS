#!/bin/bash

#List of variables (equivalent to imports/initial setup)
LOG_FILE="submission_log.txt"
SUBMISSION_DIR="submissions"

#Associative arrays for login tracking
declare -A LOGIN_ATTEMPTS
declare -A FAILED_ATTEMPTS

#This creates the submissions directory if it doesn't already exist.
mkdir -p "$SUBMISSION_DIR"

log_action() {
    # This function logs actions to the submission_log.txt file with a timestamp for each event.
    echo "$(date) - $1" >> "$LOG_FILE"
}

is_valid_file() {
    local filepath="$1"

    #This checks if the file exists, if it doesn't, then it rejects the submission.
    if [[ ! -f "$filepath" ]]; then
        echo "File does not exist."
        return 1
    fi

    #This checks if the file type is either PDF or DOCX, if it isn't, then it rejects the submission.
    if [[ "$filepath" != *.pdf && "$filepath" != *.docx ]]; then
        echo "Invalid file type. Only PDF and DOCX allowed."
        return 1
    fi

    #This checks if the file size is under 5MB, if it isn't, then it rejects the submission.
    size=$(wc -c < "$filepath")
    if (( size > 5242880 )); then
        echo "File too large. Must be under 5MB."
        return 1
    fi

    return 0
}

#This function calculates the MD5 hash of a file, which is used to check for duplicate content in the submissions directory.
get_file_hash() {
    md5sum "$1" | awk '{print $1}'
}

#This function handles the submission of assignments, it checks for duplicate filenames and file content.
submit_assignment() {
    read -p "Enter Student ID: " student_id
    read -p "Enter file path: " filepath

    is_valid_file "$filepath" || return

    filename=$(basename "$filepath")
    new_path="$SUBMISSION_DIR/$filename"

    new_hash=$(get_file_hash "$filepath")

    #This checks for duplicate filenames and file content in the submissions directory.
    for file in "$SUBMISSION_DIR"/*; do
        [[ ! -e "$file" ]] && break

        existing_name=$(basename "$file")

        if [[ "$existing_name" == "$filename" ]]; then
            echo "Duplicate filename detected. Submission rejected."
            log_action "$student_id - Duplicate filename rejected: $filename"
            return
        fi

        if [[ "$(get_file_hash "$file")" == "$new_hash" ]]; then
            echo "Duplicate file content detected. Submission rejected."
            log_action "$student_id - Duplicate content rejected: $filename"
            return
        fi
    done

    #Save file.
    cp "$filepath" "$new_path"

    echo "Submission successful."
    log_action "$student_id - Submitted: $filename"
}

check_submission() {
    read -p "Enter filename to check: " filename

    #This checks if the file exists in the submissions directory.
    if [[ -f "$SUBMISSION_DIR/$filename" ]]; then
        echo "File has already been submitted."
    else
        echo "File not found."
    fi
}

list_submissions() {
    files=("$SUBMISSION_DIR"/*)

    #This checks if there are any files in the submissions directory.
    if [[ ! -e "${files[0]}" ]]; then
        echo "No submissions yet."
        return
    fi

    #This lists all the submitted files.
    echo "Submitted Files:"
    for f in "${files[@]}"; do
        basename "$f"
    done
}

login() {
    read -p "Enter username: " username
    current_time=$(date +%s)

    #This initialises login tracking if not already set.
    [[ -z "${FAILED_ATTEMPTS[$username]}" ]] && FAILED_ATTEMPTS[$username]=0
    [[ -z "${LOGIN_ATTEMPTS[$username]}" ]] && LOGIN_ATTEMPTS[$username]=""

    #This checks if the user has had 3 or more failed login attempts.
    if (( FAILED_ATTEMPTS[$username] >= 3 )); then
        echo "Account locked due to multiple failed attempts."
        log_action "$username - Account locked"
        return
    fi

    read -p "Enter password: " password

    #Basic login simulation (password = admin)
    if [[ "$password" == "admin" ]]; then
        echo "Login successful."
        FAILED_ATTEMPTS[$username]=0
        log_action "$username - Successful login"
    else
        echo "Login failed."
        ((FAILED_ATTEMPTS[$username]++))
        LOGIN_ATTEMPTS[$username]="${LOGIN_ATTEMPTS[$username]} $current_time"
        log_action "$username - Failed login"

        #This checks for repeated login attempts within 60 seconds.
        count=0
        for t in ${LOGIN_ATTEMPTS[$username]}; do
            (( current_time - t < 60 )) && ((count++))
        done

        if (( count >= 3 )); then
            echo "Suspicious activity detected (multiple attempts in 60s)."
            log_action "$username - Suspicious login activity"
        fi
    fi
}

exit_system() {
    #Confirms if the user wants to exit.
    read -p "Are you sure you want to exit? (Y/N): " confirm
    if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
        echo "Exiting system..."
        exit 0
    fi
}


main() {
    #Infinite loop to keep system running.
    while true; do
        echo ""
        echo "SECURE SUBMISSION SYSTEM"
        echo "1. Submit Assignment"
        echo "2. Check Submission"
        echo "3. List Submissions"
        echo "4. Simulate Login Attempt"
        echo "5. Exit"

        read -p "Select an option: " choice

        case $choice in
            1) submit_assignment ;;
            2) check_submission ;;
            3) list_submissions ;;
            4) login ;;
            5) exit_system ;;
            *) echo "Invalid option. Try again." ;;
        esac
    done
}

main