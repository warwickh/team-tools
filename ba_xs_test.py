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
   
def main():
    s = benchappsession.BenchappSession(maxSessionTimeSeconds=60*30)
    #s.get_all_teams()
    #s.select_default_team()
    for team in s.myTeams:
        s.get_next_game_att(team)
    xs = xsrwsession.XSRWSession()
    team_code = 0
    my_team_page = "https://icehq.hockeysyte.com/team/%s"%team_code
    xs.driver.get("https://icehq.hockeysyte.com/team/818")
    #while(True):
    #    pass  
             
if __name__ == "__main__":
    main()