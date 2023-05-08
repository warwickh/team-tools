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
                 team_code=None,
                 season_code=None,
                 debug = False):
        self.username = username
        self.password = password         
        self.loginUrl = "https://icehq.hockeysyte.com/#"
        self.baseUrl = "https://icehq.hockeysyte.com/"
        self.team_code = team_code
        self.season_code = season_code
        self.debug = debug
        self.headless = headless
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.login()
        
    def login(self):
        self.driver.get(self.loginUrl)
        self.driver.implicitly_wait(1)
        login_button = self.driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div[2]/div[2]/ul/li/a")
        login_button.click();
        self.driver.implicitly_wait(2)
        login_username = self.driver.find_element(By.ID, "login_username")
        self.driver.execute_script("document.getElementById('login_username').value='%s'"%self.username)
        self.driver.execute_script("document.getElementById('login_password').value='%s'"%self.password)
        login_submit = self.driver.find_element(By.XPATH, '//*[@id="login_form"]/div[2]/div[1]/button')
        print(login_submit.get_attribute("id"))
        login_submit.click()
        self.driver.implicitly_wait(2)
        
    
    def team_loaded(self):
        return_val = True
        if int(self.team_code) not in range(1, 10000):
            print("Invalid team code: %s"%self.team_code)
            return_val = False
        if int(self.season_code) not in range(1, 10000):
            print("Invalid season code: %s"%self.season_code)
            return_val = False
        self.driver.get(self.baseUrl)
        self.driver.implicitly_wait(1)
        logout_buttons = self.driver.find_elements(By.XPATH, '//a[@href="/login/logout/go"]')
        if len(logout_buttons)<1:
            print("Logged out, giving up")
            return_val = False
        return return_val
    
    def get_team_code(self):
        return self.team_code
        
    def get_season_code(self):
        return self.season_code
        
    def set_team_code(self, team_code):
        self.team_code = team_code
        
    def set_season_code(self, season_code):
        self.season_code = season_code    
        
    def load_team(self, season_code, team_code):
        self.season_code = season_code
        self.team_code = team_code
        
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

    def check_invites_sent(self, match_code):
        if not self.team_loaded():
            return
        matchup_url = "%smatchup/%s"%(self.baseUrl, match_code)
        self.driver.get(matchup_url)
        self.driver.implicitly_wait(2)
        invite_buttons = self.driver.find_elements(By.XPATH, '//a[contains(@href, "/pickup/send_invite/")]')
        print(len(invite_buttons))
        if len(invite_buttons)>1:
            return False
        else:
            return True
    
    def send_invites_for_match(self, match_code):
        if not self.team_loaded():
            return
        matchup_url = "%smatchup/%s"%(self.baseUrl, match_code)
        self.driver.get(matchup_url)
        self.driver.implicitly_wait(1)
        invite_url = "/pickup/send_invites/%d/%d"%(match_code, self.team_code)
        print(invite_url)
        send_invites_button = self.driver.find_element(By.XPATH, '//a[@href="%s"]'%invite_url)
        #print(send_invites_button.text) #.click()
        send_invites_button.click()

    def check_in_player(self, player_name, match_code, status):
        if not self.team_loaded():
            return
        matchup_url = "%smatchup/%s"%(self.baseUrl, match_code)
        self.driver.get(matchup_url)
        self.driver.implicitly_wait(2)
        player_boxes = self.driver.find_elements(By.XPATH,  '//div[contains(@class, "player-box player-box")]')
        for player_box in player_boxes:
            found_player_name = player_box.find_element(By.XPATH, './/div[2]/h4/a[contains(@data-open, "player_info_")]').text
            if player_name == found_player_name:
                print("Found player %s"%player_name)
                per_ind_button = player_box.find_element(By.XPATH, './/div[contains(@class, "indication_button")]')
                current_status = per_ind_button.get_attribute("class").split(" ")[0]
                print("Current status: %s"%current_status)
                if status == 'in' and current_status !='yes' :
                    per_ind_button.click()
                    self.driver.implicitly_wait(2)
                    yes_button = self.driver.find_element(By.XPATH, '//*[@id="indication_dialog_button_yes"]')
                    print(yes_button.get_attribute("id"))
                    yes_button.click()
                elif status == 'out' and current_status != 'no':
                    per_ind_button.click()
                    self.driver.implicitly_wait(2)
                    no_button = self.driver.find_element(By.XPATH, '//*[@id="indication_dialog_button_no"]')
                    no_button.click()
                else:
                    print("No action as requested %s and current status is %s"%(status, current_status))
                    pass
                break
                    