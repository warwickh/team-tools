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
from utils import benchappsession, xsrwsession

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
    ba = benchappsession.BenchappSession(ba_email, ba_password, default_team=ba_default_team)
    print(ba.get_default_team())
    print(ba_default_team)
    ba.get_next_game_att(ba_default_team)

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
    print(xs_team_code)
    print(xs_season_code)
    game_date = "20230505"
    #xs.driver.get(my_team_page)
    scheduled_matches = xs.get_scheduled_matches()
    for scheduled_match in scheduled_matches:
        pool_name = scheduled_match[3].split(" ")[-1]
        ba_home_team_name = "%s %s"%(scheduled_match[1],pool_name)
        ba_away_team_name = "%s %s"%(scheduled_match[2],pool_name)
        print("%s V %s"%(ba_home_team_name, ba_away_team_name))
        

def main():
    config_filename = 'config.yml'
    config = load_config(config_filename)
    process_ba(config)
    process_xs(config)
    #while(True):
    #    pass  

    
             
if __name__ == "__main__":
    main()