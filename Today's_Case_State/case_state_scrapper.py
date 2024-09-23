import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import json
import schedule
import time

class WebScraper:
    def __init__(self, url, json_file):
        self.url = url
        self.json_file = json_file
        self.user_agent = UserAgent()

    def scrape_data(self):
        headers = {'User-Agent': self.user_agent.random}
        data = {}
        try:
            response = requests.get(self.url, headers=headers, verify=False)
            if response.status_code == 200:
                rows = BeautifulSoup(response.text, 'html.parser').find('table').find_all('tr')
                for row in rows:
                    cols = row.find_all(['th', 'td'])
                    if cols:
                        key = cols[0].get_text(strip=True).encode('latin1').decode('utf-8')
                        value = cols[1].get_text(strip=True).encode('latin1').decode('utf-8')
                        data[key] = value
                self.save_data(data)
        except requests.exceptions.RequestException as e:
            print(f'Error: {e}')

    def save_data(self, data):
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {self.json_file}")

    def schedule_scraping(self):
        schedule.every().day.at("10:35").do(self.scrape_data)
        schedule.every().day.at("17:35").do(self.scrape_data)

    def run(self):
        self.schedule_scraping()
        while True:
            print("...Waiting Until Scheduled Time...")
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    scraper = WebScraper('https://supremecourt.gov.np/web/', 'case_state_today.json')
    scraper.run()