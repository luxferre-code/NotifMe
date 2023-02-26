try:
    import os
    import sys
    import icalendar
    import requests
    import datetime as dt
    import json
    from pushbullet import Pushbullet
    from colorama import Fore, init
    from crontab import CronTab
except ModuleNotFoundError as e:
    print(f"Error: {e}")
    sys.exit(1)
finally:
    init()

def ask(text: str) -> str:
    return input(f"{Fore.YELLOW}{text}{Fore.RESET}")

def test_calendar(link: str) -> bool:
    r = requests.get(link)
    try:
        icalendar.Calendar.from_ical(r.text)
        return True
    except:
        return False
    
def ask_number(text: str, min=0, max=31) -> int:
    while True:
        try:
            number = int(ask(text))
            if(number >= min and number <= max):
                return number
            else:
                print(f"{Fore.RED}Error: Number must be between {min} and {max}{Fore.RESET}")
        except:
            print(f"{Fore.RED}Error: Invalid number!{Fore.RESET}")
    
def genere_random_code() -> str:
    return str(os.urandom(16).hex())[:8]

def setup():
    print(f"{Fore.YELLOW}Welcome to the setup!{Fore.RESET}")
    print(f"{Fore.YELLOW}Please enter the following information:{Fore.RESET}")
    config = {}
    config["name"] = ask("Name: ")
    
    while True:
        calendar_link = ask("Calendar link: ")
        if(test_calendar(calendar_link)):
            config["calendar"] = calendar_link
            break
        else:
            print(f"{Fore.RED}Error: Invalid calendar link!{Fore.RESET}")

    while True:
        pushbullet_token = ask("Pushbullet token: ")
        try:
            pb = Pushbullet(pushbullet_token)
            
            # Send a code to confirm the token
            code = genere_random_code()
            pb.push_note("NotifMe setup", f"Your code is: {code}")
            if(ask("Please enter the code you received: ") == code):
                config["pushbullet_token"] = pushbullet_token
                break
            else:
                print(f"{Fore.RED}Error: Invalid code!{Fore.RESET}")
        except:
            print(f"{Fore.RED}Error: Invalid Pushbullet token!{Fore.RESET}")

    with open("../ressources/config.json", "w") as f:
        json.dump(config, f, indent=4)

    add_crontab = None
    while add_crontab not in ["y", "n"]:
        add_crontab = ask("Do you want to add a crontab to run the program every day? (y/n): ")
    if(add_crontab == "y"):
        crontab = CronTab(user=True)
        job = crontab.new(command=f"python3 {os.path.dirname(os.path.realpath(__file__))}/main.py")
        job.hour.on(ask_number("Hour: ", 0, 23))
        job.minute.on(ask_number("Minute: ", 0, 59))
        crontab.write()

    print(f"{Fore.GREEN}Setup complete!{Fore.RESET}")
    sys.exit(0)

def load_config_file() -> dict:
    try:
        with open("../ressources/config.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{Fore.RED}Error: config.json not found!{Fore.RESET}\nPlease use python3 main.py --setup to create a config file")
        sys.exit(1)

def download_calendar(link: str) -> icalendar.Calendar:
    r = requests.get(link)
    return icalendar.Calendar.from_ical(r.text)

def get_schedule(date: str, link: str) -> list:
    cal = download_calendar(link)
    schedule = []
    for event in cal.walk():
        if(event.name == "VEVENT"):
            event_date = str(event.get('dtstart').dt)[:10]
            if dt.datetime.strptime(event_date, '%Y-%m-%d') == dt.datetime.strptime(date, '%Y-%m-%d'):
                event_dict = {}
                event_dict['summary'] = event.get('summary')
                event_dict['location'] = event.get('location')
                event_dict['dtstart'] = event.get('dtstart').dt + dt.timedelta(hours=1)
                event_dict['dtend'] = event.get('dtend').dt + dt.timedelta(hours=1)
                schedule.append(event_dict)
    return schedule

def string_schedule(date: str, link: str) -> str:
    schedule = get_schedule(date, link)
    schedule.sort(key=lambda x: x['dtstart'].time())
    string = ""
    for event in schedule:
        start_time = event['dtstart'].strftime("%H:%M")
        end_time = event['dtend'].strftime("%H:%M")
        text = event['summary'].split(" - ")
        string += f"{text[1]} | {event['location']}\n=> {start_time} - {end_time}\n\n"
    return string