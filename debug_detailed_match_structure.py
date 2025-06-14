from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

# Configure Selenium options
options = Options()
options.add_argument("--headless")  # Run in headless mode
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

# Create driver (make sure chromedriver is in your PATH or provide path)
driver = webdriver.Chrome(options=options)

try:
    # Load the VLR match page
    url = "https://www.vlr.gg/371266/kr-esports-vs-cloud9-champions-tour-2024-americas-stage-2-ko"
    driver.get(url)

    # Wait for JavaScript to load content
    time.sleep(5)  # you can adjust the sleep time if needed

    # Get full page source
    full_html = driver.page_source

    # Save to file (optional)
    with open("vlr_match_detailed_page.html", "w", encoding="utf-8") as file:
        file.write(full_html)

    print("✅ Page structure saved successfully!")

finally:
    driver.quit()
