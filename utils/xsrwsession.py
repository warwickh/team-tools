#!/usr/bin/env python3
"""

"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class XSRWSession:
    def __init__(self,
                 username=None,
                 password=None,
                 headless=False,
                 debug = False):
        self.username = username
        self.password = password         
        self.loginUrl = "https://icehq.hockeysyte.com/#"
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
    
