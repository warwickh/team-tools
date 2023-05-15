#!/usr/bin/env python3
"""
Extract game schedule from hockeysyte for loading into BenchApp
season code is unique for season and division 
e.g. 125 is B3 winter 2023
https://icehq.hockeysyte.com/games/125

"""
import requests 
from bs4 import BeautifulSoup 
import re
from datetime import datetime
import csv

class XSROSession:
    def __init__(self,
                 username=None,
                 password=None,
                 login=False,
                 debug = False):
        self.username = username
        self.password = password         
        self.loginUrl = "https://icehq.hockeysyte.com/#"
        self.baseUrl = "https://icehq.hockeysyte.com/"
        self.login = login
        self.debug = debug
        #if self.login:
        #    self.login()

    def get_page(self, url):
        with requests.session() as s: 
            s.get(url).raise_for_status()
            data = s.post(url).content
        return data

    def get_page_soup(self, url):
        data = self.get_page(url)
        soup = BeautifulSoup(data, "html.parser")
        return soup

    def get_small_matches(self, soup):
        #my_mid_matches = soup.find_all("div", {"class": "flex__horizontally-centered show-for-medium"})
        my_small_matches = soup.find_all("div", {"class": "callout show-for-small-only text-center"})
        return my_small_matches

    def get_seasons(self, soup):
        #my_mid_matches = soup.find_all("div", {"class": "flex__horizontally-centered show-for-medium"})
        all_seasons = soup.find_all("ul", {"class": "vertical menu submenu"})[2]
        active_seasons = all_seasons.find_all("a", href=True)
        return active_seasons

    def get_teams(self, soup):
        standings = soup.find_all("div", {"class": "season__standings"})[0]
        all_teams = standings.find_all("a", {"class": "black_links"}, href=True)
        return all_teams

    def process_date(self, raw_date_string, year):
        clean_date_string = datetime.strptime(raw_date_string, "%a . %b %d")
        #clean_date_string = clean_date_string.replace(year=int(year)).strftime('%d/%m/%Y')
        clean_date_string = clean_date_string.replace(year=int(year)).strftime('%Y%m%d')
        return clean_date_string

    def process_time(self, raw_time_string):
        clean_time_string = raw_time_string.split("-")[0].strip()
        return clean_time_string
        
    def get_season_name(self, season_code):
        sched_url = "%sgames/%s"%(self.baseUrl,season_code)
        page_soup = self.get_page_soup(sched_url)
        #search_string = '<a href="/season/%s">'%season_code
        season_name = page_soup.find('a', {'href': "/season/%s"%season_code}).text.strip()
        return season_name
        
    def get_team_name(self, season_code, team_code):
        season_url = "%sseason/%s"%(self.baseUrl, season_code)
        page_soup = self.get_page_soup(season_url)
        # = '<a href="/team/%s">'%team_code
        team_name = page_soup.find('a', {'href': "/team/%s"%team_code}, text=True).text.strip()
        return team_name

    def get_year_from_season(self, season_string):
        return season_string.split(" ")[-1]

    def get_team_code(self, season_name, team_name):
        team_code = None
        page_soup = self.get_page_soup(self.baseUrl)
        seasons = self.get_seasons(page_soup)
        for season in seasons:
            #print("%s %s"%(season.text.strip(), season_name))
            if season_name.lower() in season.text.strip().lower():
                season_code = season['href'].split("/")[-1]
        return season_code

    def get_season_code(self, season_name):
        season_code = None
        page_soup = self.get_page_soup(self.baseUrl)
        seasons = self.get_seasons(page_soup)
        for season in seasons:
            #print("%s %s"%(season.text.strip(), season_name))
            if season_name.lower() in season.text.strip().lower():
                season_code = season['href'].split("/")[-1]
        return season_code

    def get_codes(self, season_name, team_name):
        team_code = {}
        season_code = {}
        season_code[season_name] = self.get_season_code(season_name)
        season_url = "%sseason/%s"%(self.baseUrl, season_code[season_name])
        page_soup = self.get_page_soup(season_url)
        teams = self.get_teams(page_soup)
        for team in teams:
            #print("%s %s"%(team.text.strip(), team_name))
            if team_name.lower() in team.text.strip().lower():
                team_code[team_name] = team['href'].split("/")[-1]
        return [season_code, team_code]
                
    def select_season(self):
        season_options = []
        season_paths = []
        page_soup = self.get_page_soup(self.baseUrl)
        seasons = self.get_seasons(page_soup)
        for season in seasons:
            season_options.append(season.text.strip())
            season_paths.append(season['href'])
        #print(season_options)
        user_input = ''
        input_message = "Pick an option:\n"
        for index, item in enumerate(season_options):
            input_message += f'{index+1}) {item}\n'
        input_message += 'Your choice: '
        while user_input not in map(str, range(1, len(season_options) + 1)):
            user_input = input(input_message)
        print('You picked: ' + season_options[int(user_input) - 1])
        #return season_paths[int(user_input) - 1].split("/")[-1]
        return season_options[int(user_input) - 1].split("-")[0].split("Pool ")[-1].strip()

    def select_team(self, season_code):
        team_options = []
        season_url = "%sseason/%s"%(self.baseUrl, season_code)
        #print(season_url)
        page_soup = self.get_page_soup(season_url)
        teams = self.get_teams(page_soup)
        for team in teams:
            team_options.append(team.text.strip())
        #print(team_options)
        user_input = ''
        input_message = "Pick an option:\n"
        for index, item in enumerate(team_options):
            input_message += f'{index+1}) {item}\n'
        input_message += 'Your choice: '
        while user_input not in map(str, range(1, len(team_options) + 1)):
            user_input = input(input_message)
        print('You picked: ' + team_options[int(user_input) - 1])
        #print(team_options[int(user_input) - 1])
        return team_options[int(user_input) - 1]

    def get_row_small_match(self, match, year):
        def_type = "GAME"
        def_game_type = "REGULAR"
        def_duration = "1:00"
        def_location = "ICEHQ"
        date = self.process_date(match.find("h4").text, year)
        time = self.process_time(match.find("p").text)
        home_team = match.find_all("div", {"class": "text-center"})[0].find("div").text
        away_team = match.find_all("div", {"class": "text-center"})[2].find("div").text
        game_code = match.find_all("a", href=True)[0]['href'].split("/")[-1]
        return [def_type, def_game_type, home_team, away_team, date, time, def_duration, def_location, game_code]

    def check_invites_sent(self, match_code): #todo login required
        matchup_url = "%smatchup/%s"%(self.baseUrl, match_code)
        page_soup = self.get_page_soup(matchup_url)
        #invite_buttons = self.driver.find_elements(By.XPATH, '//a[contains(@href, "/pickup/send_invite/")]')
        print(soup)
        invite_buttons = page_soup.find_all("a", href=re.compile("/pickup/send_invite/"))
        print(invite_buttons)
        print(len(invite_buttons))
        if len(invite_buttons)>1:
            return False
        else:
            return True        

    def load_season_schedule(self, season_code, team_code):
        sched_headers = ["Type", "Game Type", "Home", "Away", "Date", "Time", "Duration", "Location", "Season Code", "Team Code", "Game Code"]
        rows = []
        sched_url = "%sgames/%s"%(self.baseUrl,season_code)
        page_soup = self.get_page_soup(sched_url)
        current_season_name = self.get_season_name(season_code)
        #print(current_season_name)
        my_team_name = self.get_team_name(season_code, team_code)
        #print(my_team_name)
        current_year = self.get_year_from_season(current_season_name)
        my_small_matches = self.get_small_matches(page_soup)
        rows.append(sched_headers)
        for match in my_small_matches:
            current_row = self.get_row_small_match(match, current_year)
            if(current_row[2] == my_team_name or current_row[3] == my_team_name):
                rows.append(current_row + [season_code, team_code])
        return rows
        
    def create_ba_schedule_upload(self, season_code, team_code):
        #ba_sched_headers = ["Type", "Game Type", "Home", "Away", "Date", "Time", "Duration", "Location"]
        current_season_name = self.get_season_name(season_code)
        my_team_name = self.get_team_name(season_code, team_code)
        schedule = self.load_season_schedule(season_code, team_code)
        out_file_name = "%s_%s.csv"%(my_team_name.replace(" ","_"),current_season_name.replace(" ","_"))
        with open(out_file_name, 'w', newline='') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',')
            #filewriter.writerow(ba_sched_headers)
            for row in schedule:
                filewriter.writerow(row[0:8])
