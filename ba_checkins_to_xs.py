#!/usr/bin/env python3
"""
This script will query the hockeysyte page for your team and retrieve the season schedule.
The next upcoming match will be determined and you will have the option to confirm this date.
Once confirmed, the check in details will be extracted from the Benchapp page for your team and loaded into hockeysyte for the upcoming match. 
In order to process check ins, the invitations must have been sent previously. There is a function for sending invitations for the match also.

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

def get_match_schedule(xsro_session, season_name, team_name):
    codes = xsro_session.get_codes(season_name, team_name)
    print(codes)
    schedule = xsro_session.load_season_schedule(codes[0][season_name],codes[1][team_name])
    xsro_session.create_ba_schedule_upload(codes[0][season_name],codes[1][team_name]) #Create BA Upload file
    #print(schedule)
    return schedule

def process_match(config, team_div, team_name, next_match_schedule):
    print(next_match_schedule)
    ba_email = config["ba_login"]["email"]
    ba_password = config["ba_login"]["password"]
    ba_session = basession.BenchappSession(ba_email, ba_password)
    xs_username = config["xs_login"]["username"]
    xs_password = config["xs_login"]["password"]
    ba_team_name = "%s %s"%(team_name, team_div)
    checkins = ba_session.get_next_game_att(ba_team_name)
    print(checkins)
    match_code = next_match_schedule[8]
    season_code = next_match_schedule[9]
    team_code = next_match_schedule[10]
    xs_match_date = next_match_schedule[4]
    xsrw_session = xsrwsession.XSRWSession(xs_username, xs_password, headless=False, team_code=team_code, season_code=season_code,debug = True)
    if xsrw_session.check_invites_sent(match_code) is False:
        print("Invites not sent...")
        answer = input("Send invites now for match %s on %s? "%(match_code, xs_match_date))
        if answer.lower() in ["y","yes"]:
            print("Sending invites for match %s"%match_code)
            xsrw.send_invites_for_match(match_code) 
        elif answer.lower() in ["n","no"]:
            print("Cannot continue without invites")
            return
    else:
        print("Invites have already been sent...")
    print("Processing check-ins for %s %s %s"%(match_code, season_code, team_code))
    for player in checkins[1:]:
        print(player)
        player_name = player[3]
        player_status = player[6]
        ba_match_date = player[2]
        print("Check if dates match %s %s"%(xs_match_date, ba_match_date))
        if xs_match_date == ba_match_date:
            print("Processing check-ins for %s %s %s %s"%(player_name, xs_match_date, match_code, player_status))
            xsrw_session.check_in_player(player_name, match_code, player_status) 
        else:
            print("Dates don't match %s %s"%(xs_match_date, ba_match_date))
    return True
    
def main():
    team_div = ""
    team_name = ""
    config_filename = 'config.yml'
    config = load_config(config_filename)
    xs_username = config["xs_login"]["username"]
    xs_password = config["xs_login"]["password"]
    xsro_session = xsrosession.XSROSession(xs_username, xs_password, login=False, debug=False)
    team_div = xsro_session.select_season()
    team_name = xsro_session.select_team(xsro_session.get_season_code(team_div))
    #Get schedule from xs
    match_schedule = get_match_schedule(xsro_session, team_div, team_name)  
    input_date = datetime.today().strftime('%Y%m%d')
    dates = []
    #Find next match in schedule
    for row in match_schedule:
        print("%s %s %s %s"%(row[2],row[3],row[4],row[5]))
        dates.append(row[4])
    results = [d for d in sorted(dates) if d > input_date]
    next_match_date = results[0] if results else None 

    answer = input("Next match for %s %s: %s Continue? "%(team_name,team_div, datetime.strptime(next_match_date,'%Y%m%d').strftime("%a %b %d")))
    #If confirmed process match from schedule
    if answer.lower() in ["y","yes"]:
        for row in match_schedule:
            if row[4] == next_match_date:
                next_match_schedule = row
                break
        process_match(config, team_div, team_name, next_match_schedule)
    elif answer.lower() in ["n","no"]:
        print("Cancelling")
    else:
        print("Invalid response...Cancelling")
             
if __name__ == "__main__":
    main()
    #while(True):
    #    pass 