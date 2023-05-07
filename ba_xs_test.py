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

def process_ba(config):
    ba_email = config["ba_login"]["email"]
    ba_password = config["ba_login"]["password"]
    ba_default_team =  config["ba_default_team"]
    ba_teams = config["ba_teams"]
    ba = basession.BenchappSession(ba_email, ba_password, default_team=ba_default_team)
    print(ba.get_default_team())
    print(ba_default_team)
    ba.get_next_game_att(ba_default_team)
    return ba

def process_xs(config):
    xs_username = config["xs_login"]["username"]
    xs_password = config["xs_login"]["password"]
    xs_default_team = config["xs_default_team"]
    xs_teams = config["xs_teams"]
    xs_team_code = xs_teams[xs_default_team]
    xs_seasons =  config["xs_seasons"]
    xs_default_season = config["xs_default_season"]
    xs_season_code = xs_seasons[xs_default_season]
    xs = xsrwsession.XSRWSession(xs_username, xs_password, headless=False, debug = True)
    #team_code = xs.get_team_code()
    #print(xs_team_code)
    #print(xs_season_code)
    #game_date = "20230505"
    #xs.driver.get(my_team_page)
    #scheduled_matches = xs.get_scheduled_matches()
    #for scheduled_match in scheduled_matches:
    #    pool_name = scheduled_match[3].split(" ")[-1]
    #    ba_home_team_name = "%s %s"%(scheduled_match[1],pool_name)
    #    ba_away_team_name = "%s %s"%(scheduled_match[2],pool_name)
    #    print("%s V %s"%(ba_home_team_name, ba_away_team_name))
    return xs
        
def process_xsro(config):
    xs_username = config["xs_login"]["username"]
    xs_password = config["xs_login"]["password"]
    xs_default_team = config["xs_default_team"]
    xs_teams = config["xs_teams"]
    xs_team_code = xs_teams[xs_default_team]
    xs_seasons =  config["xs_seasons"]
    xs_default_season = config["xs_default_season"]
    xs_season_code = xs_seasons[xs_default_season]
    print(xs_season_code, xs_team_code)
    xs = xsrosession.XSROSession(xs_username, xs_password, login=False, debug=True)
    print("From name: %s"%xs.get_season_code("POOL B3"))
    print("From name: %s"%xs.get_team_code("POOL B3", "Hat Trick Swayzes"))
    print("Codes from name: %s"%xs.get_codes("POOL B3", "Hat Trick Swayzes"))
    
    schedule = xs.load_season_schedule(113, 818)
    print(schedule)
    return xs

def get_match_schedule(config, season_name, team_name):
    xs_username = config["xs_login"]["username"]
    xs_password = config["xs_login"]["password"]
    xs = xsrosession.XSROSession(xs_username, xs_password, login=False, debug=True)
    codes = xs.get_codes(season_name, team_name)
    print(codes)
    schedule = xs.load_season_schedule(codes[0][season_name],codes[1][team_name])
    print(schedule)
    return schedule
    
    
def main():
    config_filename = 'config.yml'
    config = load_config(config_filename)
    match_schedule = get_match_schedule(config, "B3", "Hat Trick Swayzes")
    for row in match_schedule:
        print(row[4])
    #ba = process_ba(config)
    #xsrw = process_xs(config)
    #xsro = process_xsro(config)
    #match_code = 4821
    #xsrw.load_team(113,818)
    #xsrw.send_invites_for_match(match_code)
    #xsrw.check_in_for_match(match_code)
             
if __name__ == "__main__":
    main()
    while(True):
        pass  