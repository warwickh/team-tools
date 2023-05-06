#!/usr/bin/env python3
"""
Extract game schedule from hockeysyte for loading into BenchApp
season code is unique for season and division 
e.g. 113 is B3 winter 2023
https://icehq.hockeysyte.com/games/113

"""
import requests 
from bs4 import BeautifulSoup 
import re
from datetime import datetime
import csv

sched_headers = ["Type", "Game Type", "Home", "Away", "Date", "Time", "Duration", "Location"]

def_type = "GAME"
def_game_type = "REGULAR"
def_duration = "1:00"
def_location = "ICEHQ"

def get_page(url):
    with requests.session() as s: 
        s.get(url).raise_for_status()
        data = s.post(url).content
    return data

def get_page_soup(url):
    data = get_page(url)
    soup = BeautifulSoup(data, "html.parser")
    return soup

def get_small_matches(soup):
    #my_mid_matches = soup.find_all("div", {"class": "flex__horizontally-centered show-for-medium"})
    my_small_matches = soup.find_all("div", {"class": "callout show-for-small-only text-center"})
    return my_small_matches

def get_seasons(soup):
    #my_mid_matches = soup.find_all("div", {"class": "flex__horizontally-centered show-for-medium"})
    all_seasons = soup.find_all("ul", {"class": "vertical menu submenu"})[2]
    active_seasons = all_seasons.find_all("a", href=True)
    return active_seasons

def get_teams(soup):
    standings = soup.find_all("div", {"class": "season__standings"})[0]
    all_teams = standings.find_all("a", {"class": "black_links"}, href=True)
    return all_teams

def process_date(raw_date_string, year):
    clean_date_string = datetime.strptime(raw_date_string, "%a . %b %d")
    clean_date_string = clean_date_string.replace(year=int(year)).strftime('%d/%m/%Y')
    return clean_date_string

def process_time(raw_time_string):
    clean_time_string = raw_time_string.split("-")[0].strip()
    return clean_time_string
    
def get_row_small_match(match, year):
    date = process_date(match.find("h4").text, year)
    time = process_time(match.find("p").text)
    home_team = match.find_all("div", {"class": "text-center"})[0].find("div").text
    away_team = match.find_all("div", {"class": "text-center"})[2].find("div").text
    return [def_type, def_game_type, home_team, away_team, date, time, def_duration, def_location]

def get_season_name(soup, season_code):
    search_string = '<a href="/season/%s">'%season_code
    season_name = soup.find('a', {'href': "/season/%s"%season_code}).text.strip()
    return season_name

def get_year_from_season(season_string):
    return season_string.split(" ")[-1]

def get_my_season(url):
    season_options = []
    season_paths = []
    page_soup = get_page_soup(url)
    seasons = get_seasons(page_soup)
    for season in seasons:
        season_options.append(season.text.strip())
        season_paths.append(season['href'])
    print(season_options)
    user_input = ''
    input_message = "Pick an option:\n"
    for index, item in enumerate(season_options):
        input_message += f'{index+1}) {item}\n'
    input_message += 'Your choice: '
    while user_input not in map(str, range(1, len(season_options) + 1)):
        user_input = input(input_message)
    print('You picked: ' + season_options[int(user_input) - 1])
    #print(season_paths[int(user_input) - 1].split("/")[-1])
    return season_paths[int(user_input) - 1].split("/")[-1]

def get_my_team(url):
    team_options = []
    page_soup = get_page_soup(url)
    teams = get_teams(page_soup)
    for team in teams:
        team_options.append(team.text.strip())
    print(team_options)
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
    
def main():
    base_url = "https://icehq.hockeysyte.com/"   
    season_code = get_my_season(base_url)
    season_url = "%sseason/%s"%(base_url,season_code)
    my_team_name = get_my_team(season_url)
    sched_url = "%sgames/%s"%(base_url,season_code)
    page_soup = get_page_soup(sched_url)
    current_season_name = get_season_name(page_soup, season_code)
    out_file_name = "%s_%s.csv"%(my_team_name.replace(" ","_"),current_season_name.replace(" ","_"))
    current_year = get_year_from_season(current_season_name)
    my_small_matches = get_small_matches(page_soup)
    with open(out_file_name, 'w', newline='') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        filewriter.writerow(sched_headers)
        for match in my_small_matches:
            current_row = get_row_small_match(match, current_year)
            if(current_row[2] == my_team_name or current_row[3] == my_team_name):
                filewriter.writerow(current_row)

if __name__ == "__main__":
    main()