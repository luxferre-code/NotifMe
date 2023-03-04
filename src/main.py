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
    import sys
    import crontab
except ImportError as e:
    print(f"Error: {e}")
    sys.exit(1)
finally:
    init()

config_file_name = ""

if(len(sys.argv) == 1): sys.exit(1)

if(len(sys.argv) == 2):
    if(sys.argv[1] == "--setup"):
        setup()
    elif(sys.argv[1] == "--help"):
        print(f"{Fore.YELLOW}NotifMe - A simple ics notification system to your phone{Fore.RESET}")
        print(f"{Fore.YELLOW}Usage: python3 main.py [config_file_name.json]{Fore.RESET}")
        print(f"{Fore.YELLOW}Options:{Fore.RESET}")
        print(f"{Fore.YELLOW}--setup\t\tSetup NotifMe{Fore.RESET}")
        print(f"{Fore.YELLOW}--help\t\tShow this help{Fore.RESET}")
        print(f"{Fore.YELLOW}--version\tShow version{Fore.RESET}")
        print(f"{Fore.YELLOW}--reset\t\tReset NotifMe{Fore.RESET}")
        sys.exit(0)
    elif(sys.argv[1] == "--version"):
        print(f"{Fore.YELLOW}NotifMe - A simple ics notification system to your phone{Fore.RESET}")
        print(f"{Fore.YELLOW}Version: 0.1{Fore.RESET}")
        sys.exit(0)
    elif(sys.argv[1] == "--reset"):
        print(f"{Fore.YELLOW}NotifMe - A simple ics notification system to your phone{Fore.RESET}")
        print(f"{Fore.YELLOW}Resetting...{Fore.RESET}")
        os.system("rm -rf ./ressources")
        purge_all_crontab()
        print(f"{Fore.YELLOW}Done!{Fore.RESET}")
        sys.exit(0)
    else:
        config_file_name = sys.argv[1]
else:
    print(f"{Fore.RED}Error: Too many arguments!{Fore.RESET}")
    sys.exit(1)

if(not check_if_config_file_exists(config_file_name)):
    print(f"{Fore.RED}Error: Config file not found!{Fore.RESET}")
    sys.exit(1)

print(f"{Fore.YELLOW}NotifMe - A simple ics notification system to your phone{Fore.RESET}")

config = load_config_file(config_file_name)
schedule = get_schedule(str(datetime.now())[:10], config["calendar"])
schedule.sort(key=lambda x: x['dtstart'].time())
string = "Hey " + config["name"] + ",\nHere's your schedule for today:\n\n"
for event in schedule:
    string += f"{event['summary']} ({event['location']})\n {event['dtstart'].time()}- {event['dtend'].time()}\n"

if(len(schedule) == 0):
    string += "You have no events today!"
else:
    string += f"\nHave a nice day!\n\nNotifMe by Valentin Thuillier"

if(config["pushbullet"] != None):
    pb = Pushbullet(config["pushbullet"])
    push = pb.push_note("Schedule", string)
elif(config["ntfy"] != None):
    send_ntfy(string, config["ntfy"])