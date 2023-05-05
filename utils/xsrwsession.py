#!/usr/bin/env python3
"""

"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from datetime import datetime, date

class XSRWSession:
    def __init__(self,
                 username=None,
                 password=None,
                 headless=False,
                 debug = False):
        self.username = username
        self.password = password         
        self.loginUrl = "https://icehq.hockeysyte.com/#"
        self.baseUrl = "https://icehq.hockeysyte.com/"
        self.debug = debug
        self.headless = headless
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)
        #self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.login()
        
    def login(self):
        self.driver.get(self.loginUrl)
        self.driver.implicitly_wait(1)
        login_button = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/div[2]/ul/li/a")
        login_button.click();
        self.driver.implicitly_wait(1)
        login_username = self.driver.find_element(By.ID, "login_username")
        self.driver.execute_script("document.getElementById('login_username').value='%s'"%self.username)
        self.driver.execute_script("document.getElementById('login_password').value='%s'"%self.password)
        login_submit = self.driver.find_element(By.XPATH, '//*[@id="login_form"]/div[2]/div[1]/button')
        login_submit.click()
    
    def get_team_code(self):
        self.driver.get(self.loginUrl)
        self.driver.implicitly_wait(1)
        team_urls = self.driver.find_elements(By.XPATH, "/html/body/div[1]/div/div[2]/div[4]/div/div/div/div[2]/div[1]/div/a")
        team_url = team_urls[0].get_attribute("href") #Assumes first team - only tested with one team
        #print(team_url)
        team_code = team_url.split("/")[-1]
        #print(team_code)
        return team_code
        
    def process_date(self, raw_date_string):
        #Assume date is in the future. Test if current year or current year+1
        date_without_year = datetime.strptime(raw_date_string, "%a %b %d %I:%M %p")
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
        
    def get_scheduled_matches(self):
        rows = []
        self.driver.get(self.loginUrl)
        self.driver.implicitly_wait(1)
        team_urls = self.driver.find_elements(By.XPATH, "/html/body/div[1]/div/div[2]/div[4]/div/div/div/div[2]/div[1]/div/a")
        scheduled_matches = self.driver.find_elements(By.XPATH, '/html/body/div[1]/div/div[2]/div[3]/div/div/div/div/div')
        for scheduled_match in scheduled_matches:
            try:
                game_code = scheduled_match.find_element(By.TAG_NAME, 'a').get_attribute("href").split("/")[-1]
                if game_code=="4795":
                    home_team = scheduled_match.find_elements(By.CLASS_NAME, "scroller__team")[0].text
                    away_team = scheduled_match.find_elements(By.CLASS_NAME, "scroller__team")[1].text
                    season_name = scheduled_match.find_elements(By.TAG_NAME, 'h4')[0].text.split("-")[0].strip()
                    match_date =  self.process_date(scheduled_match.find_elements(By.TAG_NAME, 'h4')[1].text.strip())
                    row = [game_code, home_team, away_team, season_name, match_date]
                    rows.append(row)
            except:
                pass
        return rows
