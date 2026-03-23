#These are the imports that the script needs to run.
import time
import os
from datetime import datetime

#This makes sure the text files are created in the same directory as the root file.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JOB_QUEUE_FILE = os.path.join(SCRIPT_DIR, "job_queue.txt")
COMPLETED_FILE = os.path.join(SCRIPT_DIR, "completed_jobs.txt")
LOG_FILE = os.path.join(SCRIPT_DIR, "scheduler_log.txt")

#Round Robin quantum value.
TIME_QUANTUM = 5

#This adds timestamped events to the scheduler_log.txt file.
def log_event(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as log:
        log.write(f"{timestamp} - {message}\n")


#This loads pending jobs from the job_queue.txt document.
def load_jobs():
    if not os.path.exists(JOB_QUEUE_FILE):
        return []

    jobs = []
    with open(JOB_QUEUE_FILE, "r") as f:
        for line in f:
            student_id, name, exec_time, priority = line.strip().split(",")
            jobs.append({
                "student_id": student_id,
                "name": name,
                "exec_time": int(exec_time),
                "priority": int(priority)
            })
    return jobs

#This saves any pending jobs back to the job_queue.txt file.
def save_jobs(jobs):
    with open(JOB_QUEUE_FILE, "w") as f:
        for job in jobs:
            f.write(f"{job['student_id']},{job['name']},{job['exec_time']},{job['priority']}\n")

#This stores completed jobs back into the completed_jobs.txt file.
def save_completed(job, scheduling_type):
    with open(COMPLETED_FILE, "a") as f:
        f.write(f"{job['student_id']},{job['name']},{scheduling_type},{datetime.now()}\n")

#This allows the user to view any pending jobs before they are completed.
def view_pending_jobs():
    jobs = load_jobs()
    if not jobs:
        print("No pending jobs.")
        return

    print("\nPENDING JOBS:")
    for j in jobs:
        print(f"Student: {j['student_id']} | Job: {j['name']} | "
              f"Time: {j['exec_time']}s | Priority: {j['priority']}")

#This asks the user the student ID, job name, time and priority which then creates a pending job.
def submit_job():
    student_id = input("Enter student ID: ")
    job_name = input("Enter job name: ")
    exec_time = int(input("Enter estimated execution time (secs): "))
    priority = int(input("Enter priority (1–10): "))

    job = f"{student_id},{job_name},{exec_time},{priority}\n"

    with open(JOB_QUEUE_FILE, "a") as f:
        f.write(job)

    log_event(f"Job submitted: {student_id}, {job_name}, priority {priority}")
    print("Job submitted successfully.")

#This reads the completed_jobs.txt file and outputs all the previously completed jobs to the user.
def view_completed_jobs():
    if not os.path.exists(COMPLETED_FILE):
        print("No completed jobs.")
        return

    print("\nCOMPLETED JOBS:")
    with open(COMPLETED_FILE, "r") as f:
        for line in f:
            print(line.strip())

#This is the Round Robin algorithm.
#Unfortuantly it doesn't work, it is something to do with the loops I suppose as it outputs 'Running [job] for 5 seconds' every 5 seconds continuously. :(
def round_robin():
    jobs = load_jobs()
    #It finds jobs, it no jobs are found, then it returns back to the main menu.
    if not jobs:
        print("No jobs to process.")
        return

    print("\nProcessing with ROUND ROBIN (5s quantum)...")

    while jobs:
        job = jobs.pop(0)

        log_event(f"Executing job (RR): {job['student_id']} - {job['name']}")

        if job["exec_time"] > TIME_QUANTUM:
            print(f"Running {job['name']} for {TIME_QUANTUM}s...")
            time.sleep(TIME_QUANTUM)  #Simulated execution for dramatic effect....
            job["exec_time"] -= TIME_QUANTUM
            jobs.append(job)
        else:
            print(f"Completing {job['name']} ({job['exec_time']}s remaining)...")
            time.sleep(TIME_QUANTUM)
            save_completed(job, "Round Robin")

        save_jobs(jobs)
    print("Round Robin scheduling complete.")

#This is the priority scheduling algorithm.
def priority_scheduling():
    jobs = load_jobs()
    if not jobs:
        print("No jobs to process.")
        return

    print("\nProcessing with PRIORITY SCHEDULING...")

    #This sorts all the jobs with the highest priority being first (10 being the highest).
    jobs.sort(key=lambda x: x["priority"], reverse=True)

    for job in jobs:
        log_event(f"Executing job (PRIORITY): {job['student_id']} - {job['name']}")
        #print(f"Running {job['name']} (priority {job['priority']}) for {job['exec_time']}s...")
        time.sleep(1) #Simulated execution for dramatic effect.
        save_completed(job, f"Priority: {job['priority']}")

    save_jobs([]) #Clears the the pending queue once completed.
    print("Priority scheduling complete.")


def main_menu():
    while True:
        print("\nUNIVERSITY HPC JOB SCHEDULER")
        print("1. View Pending Jobs")
        print("2. Submit Job Request")
        print("3. Process Queue (Round Robin)")
        print("4. Process Queue (Priority Scheduling)")
        print("5. View Completed Jobs")
        print("6. Exit")
        choice = input("Choose an option: ")

        #This calls the functions relevant to the task asked by the user.
        if choice == "1":
            view_pending_jobs()
        elif choice == "2":
            submit_job()
        elif choice == "3":
            round_robin()
        elif choice == "4":
            priority_scheduling()
        elif choice == "5":
            view_completed_jobs()
        elif choice == "6":
            confirm = input("Are you sure you want to exit? (y/n): ")
            if confirm.lower() == "y":
                log_event("Scheduler exited.")
                print("Goodbye.")
                break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main_menu()