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

def main():
    config_filename = 'config.yml'
    config = load_config(config_filename)
    ba_email = config["ba_login"]["email"]
    ba_password = config["ba_login"]["password"]
    ba_default_team =  config["ba_default_team"]
    ba_teams = config["ba_teams"]
    ba = benchappsession.BenchappSession(ba_email, ba_password, default_team=ba_default_team)
    print(ba.get_default_team())
    print(ba_default_team)
    ba.get_next_game_att(ba_default_team)
    xs_username = config["xs_login"]["username"]
    xs_password = config["xs_login"]["password"]
    #xs = xsrwsession.XSRWSession(xs_username, xs_password, headless=False, debug = True)
    #my_team_page = "https://icehq.hockeysyte.com/team/%s"%team_code
    #xs.driver.get("https://icehq.hockeysyte.com/team/818")
             
if __name__ == "__main__":
    main()