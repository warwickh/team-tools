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
#import io

class BenchappSession:
    def __init__(self,
                 email=None,
                 password=None,
                 sessionFile='ba_session.dat',
                 maxSessionTimeSeconds = 60 * 30,
                 agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
                 default_team = "",
                 debug = False):
        self.email = email
        self.password = password
        self.loginUrl = "https://www.benchapp.com/player-area/ajax/login.php"
        self.loginTestUrl = "https://www.benchapp.com/player/dashboard"
        self.baseUrl = "https://www.benchapp.com"
        self.maxSessionTime = maxSessionTimeSeconds  
        self.sessionFile = sessionFile
        self.userAgent = agent
        self.loginTestString = "Logout"
        self.debug = debug
        self.myTeams = {}
        self.default_team = default_team
        if email is None or password is None or email=="" or password=="":
            raise CredentialError('You must specify either a username/password '
                'combination or "useNetrc" must be either True or a string '
                'representing a path to a netrc file')
        self.connected = self.login()
        if self.connected:
            self.load_teams()
        if self.debug:
            print("Team count: %s"%len(self.myTeams))

    def modification_date(self, filename):
        t = os.path.getmtime(filename)
        return datetime.fromtimestamp(t)

    def login(self, forceLogin = False, **kwargs):
        wasReadFromCache = False
        if self.debug:
            print('loading or generating session...')
        if os.path.exists(self.sessionFile) and not forceLogin:
            time = self.modification_date(self.sessionFile)         
            lastModification = (datetime.now() - time).seconds
            if lastModification < self.maxSessionTime:
                with open(self.sessionFile, "rb") as f:
                    self.session = pickle.load(f)
                    wasReadFromCache = True
                    if self.debug:
                        print("loaded session from cache (last access %ds ago) "%lastModification)
        if not wasReadFromCache:
            self.session = requests.Session()
            self.session.headers.update({'user-agent' : self.userAgent})
            self.loginData = dict(email=self.email, password=self.password)
            print(self.loginData)
            res = self.session.post(self.loginUrl, data = self.loginData)
            if self.debug:
                print('created new session with login %s'%res )
            self.saveSessionToCache()

        res = self.session.get(self.loginTestUrl)
        if self.debug:print(res)
        #print(res.text)
        if res.text.lower().find(self.loginTestString.lower()) < 0:
            print("could not log into provided site %s"% self.loginUrl)
            return False
        else:
            self.saveSessionToCache()
            return True
    
    def get_teams(self):
        return self.myTeams
    
    def get_default_team(self):
        return self.default_team
        
    def set_default_team(self, team_name):
        if team_name in self.myTeams.keys():
            return True
        else:
            return False    
    
    def check_connected(self):
        return self.connected      

    def saveSessionToCache(self):
        with open(self.sessionFile, "wb") as f:
            pickle.dump(self.session, f)
            if self.debug:
                print('updated session cache-file %s' % self.sessionFile)

    def retrieveContent(self, url, method = "get", postData = None, **kwargs):
        if method == 'get':
            res = self.session.get(url , **kwargs)
        else:
            res = self.session.post(url , data = postData, **kwargs)
        self.saveSessionToCache()            
        return res

    def load_team_link(self, team):
        team.small.extract()
        team_name = team.find("a", href=True).text.strip()
        team_url = team.find("a", href=True)["href"]
        self.myTeams[team_name] = team_url.split("/")[-1]
                
    def load_teams(self):
        if self.debug:
            print("Reloading team list")
        res = self.retrieveContent(self.loginTestUrl)
        soup = BeautifulSoup(res.text, "html.parser")    
        all_other_teams = soup.find_all("li", "team")
        for team in all_other_teams:
            self.load_team_link(team)
        next_team = [elem for elem in self.myTeams.values()][0]
        res = self.retrieveContent("%s/switch/team/%s"%(self.baseUrl, next_team))
        soup = BeautifulSoup(res.text, "html.parser")    
        all_other_teams = soup.find_all("li", "team")
        for team in all_other_teams:
            self.load_team_link(team)
        
    def is_match(self, event_soup):
        game_tag = event_soup.find("div", {"class": "opponents"})
        if game_tag:
            if self.debug:
                print("This is a match %s"%game_tag)
            return True
        else:
            if self.debug:
                print("This is not a match, skipping")
            return False
            
    def process_date(self, raw_date_string):
        #Assume date is in the future. Test if current year or current year+1
        date_without_year = datetime.strptime(raw_date_string, "%A, %b %d")
        dt = date.today()
        today = datetime.combine(dt, datetime.min.time())
        current_year = today.year
        date_with_current_year = date_without_year.replace(year=int(current_year))
        clean_date_string = date_with_current_year.strftime('%Y%m%d')
        print(date_with_current_year)
        print(today)
        if date_with_current_year<today:
            if self.debug:
                print("Date occurs in the past, assume next year")
            date_with_next_year = date_without_year.replace(year=int(current_year+1))
            clean_date_string = date_with_next_year.strftime('%Y%m%d')
        if self.debug:
            print("Returning date %s"%clean_date_string)
        return clean_date_string        
        
    def process_match(self, event_soup, team):    
        rows = []
        file_headers = ["HomeTeam","AwayTeam", "Date","Name", "Number", "Position", "Check-In"]
        home_team = event_soup.find("div", {"class": "opponents"}).find("div", {"class": "home"}).find("div", {"class": "name"})
        away_team = event_soup.find("div", {"class": "opponents"}).find("div", {"class": "away"}).find("div", {"class": "name"})
        match_date = event_soup.find("div", {"class": "whenWhere"}).find("div", {"class": "date"}) 
        match_time = event_soup.find("div", {"class": "whenWhere"}).find("div", {"class": "time"})
        match_location = event_soup.find("div", {"class": "whenWhere"}).find("div", {"class": "location"})
        home_team.span.extract()
        away_team.span.extract()
        match_title = "%s V %s %s %s %s"%(home_team.text.strip(),away_team.text.strip(),match_date.text.strip(), match_time.text.strip(), match_location.text.strip())
        out_file_name = ("%s_V_%s_%s.csv"%(home_team.text.strip(),away_team.text.strip(),match_date.text.strip())).replace(" ","_")
        clean_match_date = self.process_date(match_date.text.strip())
        all_players = event_soup.find_all("li", "playerItem")
        rows.append(file_headers)
        for player in all_players:
            player.small.extract()
            check_in_status = player.find("div", "contextualWrapper")["class"][2]
            player_position = player.find("div", "contextualWrapper")["data-playerposition"]
            player_name = player.find("p").text.strip()
            try:
                player_number = player.find("span", {"class": "playerNumber"}).text
            except:
                player_number = ""
            row = [home_team.text.strip(), away_team.text.strip(), clean_match_date, player_name, player_number, player_position, check_in_status]
            print(row)
            rows.append(row)
        
        with open(out_file_name, 'w', newline='') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',')
            for row in rows:
                filewriter.writerow(row)
            csvfile.close()
        return rows
    
    def get_next_game_att(self, team):
        res = self.retrieveContent("%s/switch/team/%s"%(self.baseUrl, self.myTeams[team])) #switch to default team
        next_event_url = "https://www.benchapp.com/schedule/next-event"
        res = self.retrieveContent("https://www.benchapp.com/schedule/next-event")
        event_soup = BeautifulSoup(res.text, "html.parser") 
        with open("next_event.txt", "w") as f:
            f.write(res.text)
            f.close()
        #print(soup)
        if self.is_match(event_soup):
            return self.process_match(event_soup, team)
            
    def select_default_team(self):
        team_options = []
        for team in self.myTeams:
            team_options.append(team.strip())
        print(team_options)
        user_input = ''
        input_message = "Pick an option:\n"
        for index, item in enumerate(team_options):
            input_message += f'{index+1}) {item}\n'
        input_message += 'Your choice: '
        while user_input not in map(str, range(1, len(team_options) + 1)):
            user_input = input(input_message)
        print('You picked: ' + team_options[int(user_input) - 1])
        self.default_team = team_options[int(user_input) - 1]
        #self.update_config("ba_default_team", self.default_team)
        return self.default_team
        
    def is_valid_team(self, team_name):
        if team_name in self.myTeams:
            print("Found team")
            return True
        else:
            print("Team not found")
            return False
