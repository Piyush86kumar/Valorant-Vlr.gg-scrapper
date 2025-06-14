from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

# Setup Selenium
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(), options=options)

# Load the match URL
url = "https://www.vlr.gg/371266/kr-esports-vs-cloud9-champions-tour-2024-americas-stage-2-ko/?game=all&tab=overview"
driver.get(url)
time.sleep(5)  # Allow JS to load completely

soup = BeautifulSoup(driver.page_source, 'html.parser')
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

# Setup Selenium
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(), options=options)

# Load the match URL
url = "https://www.vlr.gg/371266/kr-esports-vs-cloud9-champions-tour-2024-americas-stage-2-ko/?game=all&tab=overview"
driver.get(url)
time.sleep(5)  # Allow JS to load completely

soup = BeautifulSoup(driver.page_source, 'html.parser')

# Team names and scores
teams = soup.select('.team')
if len(teams) >= 2:
    print(f"Team 1: {teams[0].text.strip()}")
    print(f"Team 2: {teams[1].text.strip()}")
score = soup.select_one('.match-header-vs-score').text.strip() if soup.select_one('.match-header-vs-score') else 'N/A'
print(f"Score: {score}\n")

# Map picks/bans
print("Map Picks/Bans:\n")
map_bans = soup.select_one('.map-list')
if map_bans:
    for map_item in map_bans.select('.map'):        
        map_name = map_item.select_one('.map-name')
        if map_name:
            print(f"- {map_name.text.strip()}")
else:
    print("No map picks/bans found.")

# Parse map statistics
print("\nMap Statistics Tables:\n")

maps = soup.select('.vm-stats-game')
for game in maps:
    map_name = game.select_one('.map-header .map').text.strip() if game.select_one('.map-header .map') else "Unknown Map"
    print(f"\nMap: {map_name}")

    rows = game.select('tr')
    for row in rows:
        cols = row.find_all(['td', 'th'])
        text = [col.get_text(strip=True) for col in cols]
        if any(text):
            print("\t" + " | ".join(text))

# Cleanup
driver.quit()

# Team names and scores
teams = soup.select('.team')
if len(teams) >= 2:
    print(f"Team 1: {teams[0].text.strip()}")
    print(f"Team 2: {teams[1].text.strip()}")
score = soup.select_one('.match-header-vs-score').text.strip() if soup.select_one('.match-header-vs-score') else 'N/A'
print(f"Score: {score}\n")

# Map picks/bans
print("Map Picks/Bans:\n")
map_bans = soup.select_one('.map-list')
if map_bans:
    for map_item in map_bans.select('.map'):        
        map_name = map_item.select_one('.map-name')
        if map_name:
            print(f"- {map_name.text.strip()}")
else:
    print("No map picks/bans found.")

# Parse map statistics
print("\nMap Statistics Tables:\n")

maps = soup.select('.vm-stats-game')
for game in maps:
    map_name = game.select_one('.map-header .map').text.strip() if game.select_one('.map-header .map') else "Unknown Map"
    print(f"\nMap: {map_name}")

    rows = game.select('tr')
    for row in rows:
        cols = row.find_all(['td', 'th'])
        text = [col.get_text(strip=True) for col in cols]
        if any(text):
            print("\t" + " | ".join(text))

# Cleanup
driver.quit()
