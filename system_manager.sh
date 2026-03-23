#!/bin/bash

#This file is used to store all the actions performed.
LOG_FILE="system_monitor_log.txt"

#Directory to store archived log files.
ARCHIVE_DIR="ArchiveLogs"




#=======PART 3 - LOGGING SYSTEM=======
#Using the LOG_FILE variable, it records every action with a timestamp.
log_action() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

# Prevent killing critical processes.
is_critical() {
    if [ "$1" -le 100 ]; then
        return 0
    else
        return 1
    fi
}




#=======PART 1 - PROCESS MONITORING AND MANAGEMENT=======
#This extracts CPU and memory usage for a quick overview of system load.
show_system_usage() {
    echo "SYSTEM USAGE"
    top -bn1 | grep "Cpu"
    top -bn1 | grep "Mem"
    log_action "Viewed system usage."
}

#This outputs the top 10 processes consuming the most memory, sorted in descending order.
show_top_processes() {
    echo "TOP 10 MEMORY CONSUMING PROCESSES"
    ps -eo pid,user,%cpu,%mem --sort=-%mem | head -n 11
    log_action "Viewed top processes."
}

#This kills a process safely through the PID, checks its valid, confirms with the user before accidental termination, and also prevents termination for critical processes.
kill_process() {
    read -p "Enter PID to terminate: " pid

    if ! ps -p $pid > /dev/null; then
        echo "Invalid PID."
        return
    fi

    if is_critical $pid; then
        echo "Cannot terminate critical system process!"
        log_action "Attempted to kill critical process PID $pid."
        return
    fi

    read -p "Are you sure you want to terminate process $pid? (y/n): " confirm
    if [[ "$confirm" == "Y" || "$confirm" == "y" ]]; then
        kill $pid
        echo "Process terminated."
        log_action "Terminated process PID $pid."
    else
        echo "Termination cancelled."
    fi
}




#=======PART 2 - DISK INSPECTION AND LOG ARCHIVING=======
#This checks if a directory path exists and then displays the total disk usage.
check_disk_usage() {
    read -p "Enter directory path: " dir

    if [ ! -d "$dir" ]; then
        echo "Invalid directory."
        return
    fi

    du -sh "$dir"
    log_action "Checked disk usage for $dir."
}

#This searches for .log files larger than 50MB in a specified directory. Checks if ArchiveLogs already exists, creates it if not. ALso compresses the file and displays a warning if directory is larger than 1GB.
archive_logs() {
    read -p "Enter directory to scan for log files: " dir

    #Checks if directory is valid.
    if [ ! -d "$dir" ]; then
        echo "Invalid directory"
        return
    fi

    #This creates ArchiveLogs directory if it doesn't already exist.
    mkdir -p "$ARCHIVE_DIR"

    found=false

    find "$dir" -type f -name "*.log" -size +50M | while read file; do
        found=true
        timestamp=$(date +%Y%m%d_%H%M%S)
        filename=$(basename "$file")

        gzip -c "$file" > "$ARCHIVE_DIR/${filename}_${timestamp}.gz"

        echo "Archived: $file"
        log_action "Archived $file"
    done

    if [ "$found" = false ]; then
        echo "No large log files found."
    fi

    #This gets the size of the ArchiveLogs directory in MB.
    size=$(du -sm "$ARCHIVE_DIR" | cut -f1)

    if [ "$size" -gt 1024 ]; then
        echo "WARNING: ArchiveLogs exceeds 1GB!"
        log_action "ArchiveLogs exceeded 1GB"
    fi
}




#=======PART 4 - EXIT MECHANISM=======
#An exit mechanism with confirmation to prevent accidental termination.
exit_system() {
    read -p "Are you sure you want to exit? (y/n): " confirm
    if [[ "$confirm" == "Y" || "$confirm" == "y" ]]; then
        log_action "Exited system."
        echo "Goodbye have a nice day!"
        exit 0
    fi
}

#MAIN MENU
#The main menu the user is greeted with, using a while loop continuously until an input is accepted.
while true; do
    echo ""
    echo "SYSTEM MANAGEMENT MENU"
    echo "1. Display CPU and Memory Usage"
    echo "2. Show Top 10 Processes"
    echo "3. Terminate a Process"
    echo "4. Check Disk Usage"
    echo "5. Archive Large Log Files"
    echo "6. EXIT"
    echo ""
    read -p "Choose an option: " choice

    #After a valid number is inputted, the corresponding function is called.
    case $choice in
        1) show_system_usage ;;
        2) show_top_processes ;;
        3) kill_process ;;
        4) check_disk_usage ;;
        5) archive_logs ;;
        6) exit_system ;;
        *) echo "Invalid option. Try again." ;; #This is said if anything other than 1-6 is entered.
    esac
done