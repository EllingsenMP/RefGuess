import requests
import numpy as np
import pandas as pd
import random
from bs4 import BeautifulSoup
import pybaseball
import time
import warnings

def pullDatabase():
    # %%
    #Pull player information into df
    initialPull = pybaseball.chadwick_register()

    # %%
    #Initial Data Cleaning
    cols = ['name_first', 'name_last', 'key_bbref', 'mlb_played_first', 'mlb_played_last']
    initialPull = initialPull[cols]
    initialPull['numSeasons'] = initialPull['mlb_played_last'] - initialPull['mlb_played_first']
    cleanRows = initialPull.dropna(subset = ['key_bbref'])
    return cleanRows

# %%
#Function to scrape all time team lists from bref
def pullAlltimePlayers(team):
    #Request all time team list
    url = f'https://www.baseball-reference.com/teams/{team}/bat.shtml'
    r = requests.get(url)
    data = r.text
    teamQuery = BeautifulSoup(data, 'html.parser')

    #Find table element
    table = teamQuery.find('tbody')

    teamPlayers = []

    #Iterate through all rows and retrieve the player id value to insert into our list
    for i in table.find_all('td', class_ = 'left', attrs= {'data-stat': 'player'}):
        teamPlayers.append(i['data-append-csv'])

    return teamPlayers

# %%
#Function that accepts filter values from user and generates random player accordingly
#Function that accepts filter values from user and generates random player accordingly
def generateNewPlayer(cleanRows, seasonValue=None, debutValue=None,retirementValue=None, teamValue = None):
    #Check if None vals
    if seasonValue is None:
        seasonValue = 0

    if debutValue is None:
        debutValue = 0

    if retirementValue is None:
        retirementValue = 10000

    #Input filters
    filteredDF = cleanRows[(cleanRows['numSeasons'] >= seasonValue) & (cleanRows['mlb_played_first'] >= debutValue) & (cleanRows['mlb_played_last'] <= retirementValue)]

    #Prototype of filtering by team
    if teamValue is not None:
        teamList = pullAlltimePlayers(teamValue)
        filteredDF = filteredDF[filteredDF['key_bbref'].isin(teamList)]

    #Get new random ID and get bref url
    chosenPlayerID = filteredDF['key_bbref'].sample(n=1).iloc[0]
    baseLink = f'https://www.baseball-reference.com/players/{chosenPlayerID[0]}/{chosenPlayerID}.shtml'
    
    return baseLink, chosenPlayerID


#Function that processes bref page and returns final df
#Function that processes bref page and returns final df
def getNewPlayer(baseLink):
    #Scrape chosen player
    url = baseLink
    r = requests.get(url)
    data = r.text
    baseball = BeautifulSoup(data, 'html.parser')
    
    #Find player stats table
    table = baseball.find('table', class_ = 'stats_table sortable row_summable suppress_headers soc')
 
    #Cycle through table and find correct elements
    entriesTR = []

    for i in table.find_all('tr'):
        entriesTR.append(i.text)

    #Create list of lists for future data frame compilation
    playerList = []

    for i in range(len(entriesTR)):
        inList = []
        rows = entriesTR[i].split(' ')
        for j in rows:
            inList.append(j)

        playerList.append(inList)

    #Split lists into individual elements
    for i in range(len(entriesTR)):
        playerList[i] = entriesTR[i].split(' ')

    #Convert to DF and remove unnecessary cols/rows
    data = pd.DataFrame(playerList)
    data.columns = data.iloc[0].values
    cutoffRow = data.index[(data['Age'] == 'Yrs') | (data['Age'] == 'Yr') | (data['Age'] == 'WAR')]
    data = data.iloc[1:cutoffRow[0]]
    data = data.fillna(' ')
    data = data.drop(data[''], axis = 1)

    return data


def retrieveMysteryPlayer(data, chosenPlayerID):
    answer = data[data['key_bbref'] == chosenPlayerID].values
    
    if len(answer) == 0:
        print(f"No player found with ID: {chosenPlayerID}")
        return None
        
    return f'{answer[0][0]} {answer[0][1]}'

# %%
#Function that processes bref page and returns final df
def getNewPlayer(baseLink):
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.baseball-reference.com/'
    }
    
    r = requests.get(baseLink, headers=headers, timeout=15)
    r.raise_for_status()
    
    data = r.text
    baseball = BeautifulSoup(data, 'html.parser')
    
    #Find player stats table
    table = baseball.find('table', class_='stats_table sortable row_summable suppress_headers soc')
    
    #Cycle through table and find correct elements
    entriesTR = []

    for i in table.find_all('tr'):
        entriesTR.append(i.text)

    #Create list of lists for future data frame compilation
    playerList = []

    for i in range(len(entriesTR)):
        inList = []
        rows = entriesTR[i].split(' ')
        for j in rows:
            inList.append(j)

        playerList.append(inList)

    #Split lists into individual elements
    for i in range(len(entriesTR)):
        playerList[i] = entriesTR[i].split(' ')

    #Convert to DF and remove unnecessary cols/rows
    data = pd.DataFrame(playerList)
    data.columns = data.iloc[0].values
    cutoffRow = data.index[(data['Age'] == 'Yrs') | (data['Age'] == 'Yr') | (data['Age'] == 'WAR')]
    data = data.iloc[1:cutoffRow[0]]
    data = data.fillna(' ')
    data = data.drop(data[''], axis=1)

    return data

def retrieveMysteryPlayer(data, chosenPlayerID):
    answer = data[data['key_bbref'] == chosenPlayerID].values
    return f'{answer[0][0]} {answer[0][1]}'

