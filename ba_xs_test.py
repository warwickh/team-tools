#!/usr/bin/env python3
"""

"""
import requests 
from bs4 import BeautifulSoup 
import pickle
from datetime import datetime, date
import os
from urllib.parse import urlparse  
import csv
import yaml
import io
from utils import basession, xsrwsession, xsrosession

def load_config(config_filename):
    config = None
    with open(config_filename, "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return config

def update_config(config_filename, key, value):
    temp_config = load_config()
    temp_config[key] = value
    with open(config_filename,'w') as yamlfile:
         yaml.safe_dump(temp_config, yamlfile)

def get_match_schedule(config, season_name, team_name):
    xs_username = config["xs_login"]["username"]
    xs_password = config["xs_login"]["password"]
    xs = xsrosession.XSROSession(xs_username, xs_password, login=False, debug=True)
    codes = xs.get_codes(season_name, team_name)
    print(codes)
    schedule = xs.load_season_schedule(codes[0][season_name],codes[1][team_name])
    print(schedule)
    return schedule

def process_match(config, team_div, team_name, next_match_schedule):
    print(next_match_schedule)
    ba_team_name = "%s %s"%(team_name, team_div)
    ba_email = config["ba_login"]["email"]
    ba_password = config["ba_login"]["password"]
    ba = basession.BenchappSession(ba_email, ba_password)
    checkins = ba.get_next_game_att(ba_team_name)
    print(checkins)
    match_code = next_match_schedule[8]
    season_code = next_match_schedule[9]
    team_code = next_match_schedule[10]
    xs_match_date = next_match_schedule[4]
    print("Processing check-ins for %s %s %s"%(match_code, season_code, team_code))
    xs_username = config["xs_login"]["username"]
    xs_password = config["xs_login"]["password"]
    xsrw = xsrwsession.XSRWSession(xs_username, xs_password, headless=False, debug = True)
    xsrw.load_team(season_code, team_code)
    if xsrw.check_invites_sent(team_code) is True:
        for player in checkins[1:]:
            print(player)
            player_name = player[3]
            player_status = player[6]
            ba_match_date = player[2]
            print("Check if dates match %s %s"%(xs_match_date, ba_match_date))
            if xs_match_date == ba_match_date:
                print("Processing check-ins for %s %s %s %s"%(player_name, xs_match_date, match_code, player_status))
                xsrw.check_in_player(player_name, match_code, player_status) 
            else:
                print("Dates don't match %s %s"%(xs_match_date, ba_match_date))
    else:
        print("Invites not sent for match %s on %s. Please send before checking in"%(match_code, xs_match_date))
        #xsrw.send_invites_for_match(match_code)

    
def main():
    team_div = "B3"
    team_name = "Hat Trick Swayzes"
    config_filename = 'config.yml'
    config = load_config(config_filename)
    match_schedule = get_match_schedule(config, team_div, team_name)  #Get schedule from xs
    input_date = datetime.today().strftime('%Y%m%d')
    dates = []
    for row in match_schedule:
        dates.append(row[4])
    results = [d for d in sorted(dates) if d > input_date]
    next_match_date = results[0] if results else None 
    answer = input("Next match for %s %s: %s Continue? "%(team_name,team_div, datetime.strptime(next_match_date,'%Y%m%d').strftime("%a %b %d")))
    if answer.lower() in ["y","yes"]:
        for row in match_schedule:
            if row[4] == next_match_date:
                next_match_schedule = row
                break
        process_match(config, team_div, team_name, next_match_schedule)# Do stuff
    elif answer.lower() in ["n","no"]:
        print("Cancelling")
    else:
        print("Invalid response...Cancelling")
             
if __name__ == "__main__":
    main()
     while(True):
        pass 