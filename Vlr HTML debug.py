from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# Setup headless browser
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)

url = "https://www.vlr.gg/event/matches/2095/champions-tour-2024-americas-stage-2"
driver.get(url)
time.sleep(5)
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

match_days = soup.select("div.vm-date")
print(f"Found {len(match_days)} day sections")

all_matches = []

for day in match_days:
    date_label = day.find('div', class_='vm-date-label')
    match_rows = day.find_all('a', class_='vm-match')
    match_date = date_label.get_text(strip=True) if date_label else 'N/A'

    for row in match_rows:
        time_elem = row.find('div', class_='vm-time')
        time_str = time_elem.get_text(strip=True) if time_elem else 'N/A'

        team_elems = row.select('div.vm-t')
        team1 = team_elems[0].find('div', class_='vm-t-name').get_text(strip=True) if len(team_elems) > 0 else 'N/A'
        team2 = team_elems[1].find('div', class_='vm-t-name').get_text(strip=True) if len(team_elems) > 1 else 'N/A'

        score_elem = row.find('div', class_='vm-score')
        score_text = score_elem.get_text(strip=True) if score_elem else 'N/A'
        try:
            score1, score2 = [int(s) for s in score_text.split('-')]
        except:
            score1 = score2 = None

        status = row.find('div', class_='vm-status')
        status_text = status.get_text(strip=True) if status else 'N/A'

        week = row.find('div', class_='vm-stats-container')
        week_text = week.get_text(strip=True).split("Week")[-1].strip() if week and "Week" in week.get_text() else "N/A"

        stage_text = "Regular Season" if "Regular Season" in week.get_text() else ("Playoffs" if "Playoffs" in week.get_text() else "N/A") if week else "N/A"

        match_url = f"https://www.vlr.gg{row['href']}"

        winner = team1 if score1 is not None and score2 is not None and score1 > score2 else team2 if score1 < score2 else "Draw/N/A"

        all_matches.append({
            'date': match_date,
            'time': time_str,
            'team1': team1,
            'team2': team2,
            'score': score_text,
            'status': status_text,
            'week': f"Week {week_text}" if week_text != "N/A" else "N/A",
            'stage': stage_text,
            'winner': winner,
            'match_url': match_url
        })

for match in all_matches:
    print("\n--- MATCH ---")
    for k, v in match.items():
        print(f"{k.capitalize()}: {v}")
