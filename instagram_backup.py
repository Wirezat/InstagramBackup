from datetime import datetime
import subprocess
import requests
import random
import time
import os


#Constants                                                                                                                                          #TODO:Config file
absolute_path = os.path.dirname(__file__)

log_path = f"{absolute_path}/instagram.backup.log"
account_file = f"{absolute_path}/accounts/ActiveAccounts.txt"
inactive_account_file = f"{absolute_path}/accounts/InactiveAccounts.txt"
instaloader_params = "--latest-stamps --login=YOUR USERNAME --stories --highlights --tagged --igtv --comments --geotags --igtv"                          #TODO:unhardcode
backup_folder = f"{absolute_path}/instagram.backup"
ntfy_level = "full"

#Variables
log_filename = f"{log_path}/{datetime.now().strftime('%d-%m-%y %H:%M:%S')}.log"
processed_account = 0

def main():
    initialize()
    for acc in account_list:
        download_profile(acc)
        show_status(processed_account, account_list)
        do_sleep()
    finalize()

def initialize():
    global account_list
    global inactive_account_list
    global starting_time    
    
    os.chdir(backup_folder)
    to_log(f"{current_time()} Backup Started")
    account_list, inactive_account_list = import_account()
    starting_time = current_time()
    to_log(f"Archiving: {len(account_list)} Accounts")
    to_log(f"No longer Archiving: {len(inactive_account_list)} Accounts")
    to_log("============================================") 
    message = {
        "Title": f"[{starting_time}] Instagram Backup started.",
        "Content": f"Archiving: {len(account_list)} Accounts.No longer archiving: {len(inactive_account_list)} Accounts."
    }
    ntfy(message)
    
def import_account():
    try:
        with open(account_file, "r") as file:
            account_list = file.read().splitlines()
        with open(inactive_account_file, "r") as file:
            inactive_account_list = file.read().splitlines()
        return account_list, inactive_account_list
    except IOError:
        to_log("[ERROR]: Failed to import accounts")
        exit(1)
    
def download_profile(username):
    try:
        to_log(f"[{current_time()}]Processing Account: {username}")                                                                                     #
        command = f"{instaloader_params} {username}"                                                                                                    #
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)                                                 #TODO:Change to Python
        output, error = process.communicate()                                                                                                           #
        to_log(output.decode('utf-8'))                                                                                                                  #
        print(f"Profile '{username}' downloaded successfully.")
    except Exception as e:
        print(f"Error downloading profile '{username}': {e}")
        
def show_status(processed_account, account_list):
    progress = f"{processed_account}/{len(account_list)}"
    percentage = f"{(processed_account / len(account_list)) * 100:.2f}%"
    to_log((f"Progress: {progress} | {percentage}"))

def do_sleep():
    sleep_time = min(random.expovariate(0.6), 15.0)
    to_log(f"Sleeping {sleep_time} Seconds...")
    to_log("============================================")
    time.sleep(sleep_time)

def finalize():
    ending_time = current_time()
    if ntfy == "full":                                                                                                                                  #TODO:More notification options
        notification_data = {
            "Title": f"{ending_time} Instagram Backup beendet.",
            "Message": "Backup beendet"
        }
        ntfy(notification_data)
    to_log(f"[{ending_time}] Backup finished.")
    
def ntfy(data):
    url = "https://ntfy.sh/InstaLoader1101"
    headers = { "Title": data["Title"] }                                                                    #Unschön, aber jede Änderung macht den Code Kaputt
    requests.post(url, headers=headers, data=data["Content"])
    
def to_log(entry):
    with open(log_filename, "a") as log_file:
        log_file.write(f"{entry}\n")
        
def current_time():
    return datetime.now().strftime('%d-%m-%y %H:%M:%S')

main()