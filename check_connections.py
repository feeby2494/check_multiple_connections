#!./venv/bin/python
import subprocess
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

###
# 
#           In order to ensure that a particular web server or servers is/are
#           always connected to the network, I have made this simple script to 
#           ping all IP address listed inside the local environmental var: ADDRESSESS 15 times 
#           and email the return code and output text of the 
#           ping command to email. This could be ran by cronjob.
#
#           Furthermore, a local log is maintained, so 
#           the local admin can know when the disconnection happened. This is meant to be done on a client 
#           of the server and not on the server itself.
#
#           Please configure the .env file.
#               ADDRESSES="<your list of ip addresses delimited by ",">"
#               EMAIL_PASSWORD=""
#               EMAIL_SENDER=""
#               EMAIL_RECEIVER=""
#
#           Email password may have to be setup with your email host like Gmail or Hotmail
#           Also, port might have to change depending on email host.
#
#           Make sure python-dotenv is installed to the local virtual environment.
#               python3 -m venv venv
#               source venv/bin/activate
#               pip install python-dotenv 
#
# ###

def ping_server(server_ip):
    ping = subprocess.Popen(['ping', server_ip, "-c", "15"], stdout=subprocess.PIPE)
    return ping

# Doing the pings for all addresses in .env

pings_list = []
error_list = []
addresses = os.getenv("IP_ADDRESSES").split(",")

for address in addresses:
    ping_object = {}
    ping_command = ping_server(address)
    ping_object["ip_address"] = address
    ping_object["output"] = ping_command.communicate()[0]
    ping_object["success"] = True
    ping_object["return_code"] = ping_command.returncode
    if ping_object["return_code"] != 0:
        ping_object["success"] = False
        error_list.append(ping_object)
    pings_list.append(ping_object)

# ### 
# # 
# # Local Logging Portion 
# # 
# # ###

log_path = os.path.join(os.getcwd(), "logs", "ping_errors.txt")

if not os.path.exists(log_path):
    with open(log_path, "w") as f:
        f.write("Error Log for Failed Pings with date")

if len(error_list) > 0:
    with open(log_path, "a") as f:
        for line in error_list:
            f.write(f"\n{datetime.datetime.now()} - Failed for ip address:{line['ip_address']} with return code: {line['return_code']}")

# ### 
# # 
# # Email Portion
# # 
# # ###

import smtplib

port = 465
email_password = os.getenv("EMAIL_PASSWORD")

sender_mail = os.getenv("EMAIL_SENDER")
receiver_email = os.getenv("EMAIL_RECEIVER")
smtp_server_host = "smtp.gmail.com"
message = f"""\
    Subject: Ping results {datetime.datetime.now()}


    """

for ping in pings_list:
    message += f"""\
    
    ******************************

    IP Address: {ping["ip_address"]}

    Successfull ping: {ping["success"]}
    Returncode was: {ping["return_code"]}

    Command Output: {ping["output"]}
    
    *******************************
    
    """

with smtplib.SMTP_SSL(smtp_server_host, port) as server:
    # server.starttls()
    server.login(sender_mail, email_password)
    server.sendmail(sender_mail, receiver_email, message)

###
#
#       That's it. Please, any feedback or improvments are appricated.
#       - Jamie Lynn
#
###


