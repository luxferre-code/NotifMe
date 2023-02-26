"""
    NotifMe - A simple ics notification system to your phone
    Credits:
        - LuxFerre
    Started on: 26-02-2023
"""
try:
    import sys
    import os
    from colorama import Fore, init
    from datetime import datetime
    from functions import *
    from pushbullet import Pushbullet
except ImportError as e:
    print(f"Error: {e}")
    sys.exit(1)
finally:
    init()

if(len(sys.argv) > 1):
    if(sys.argv[1] == "--setup"):
        setup()
    else:
        print(f"{Fore.RED}Error: Unknown argument: {sys.argv[1]}{Fore.RESET}")
        sys.exit(1)

config = load_config_file()
schedule = get_schedule(str(datetime.now())[:10], config["calendar"])
schedule.sort(key=lambda x: x['dtstart'].time())
string = "Hey " + config["name"] + ", here's your schedule for today:\n\n"
for event in schedule:
    string += f"{event['summary']} ({event['location']})\n {event['dtstart'].time()}- {event['dtend'].time()}\n"

if(len(schedule) == 0):
    string += "You have no events today!"

pb = Pushbullet(config["pushbullet_token"])
pb.push_note("Schedule today", string + "\n\nHave a nice day!")