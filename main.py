import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import os

def get_date_time(event_time):
    match = re.search(r'(\d+)(:\d{2})([ap]m)', event_time)
    if match:
        hour, minutes, am_pm = match.groups()
        hour = int(hour) + 12 if am_pm == 'pm' else int(hour)
        return f"{hour:02}:{minutes}"
    return None

def scrape_forex_factory_last_month(file_path):
    scraper = cloudscraper.create_scraper()
    
    # Calculate start and end dates for the last month
    today = datetime.today()
    last_month_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
    last_month_end = today.replace(day=1) - timedelta(days=1)
    
    current_date = last_month_start.strftime("%b%d.%Y")
    end_date = last_month_end.strftime("%b%d.%Y")
    
    while current_date <= end_date:
        url = f'https://www.forexfactory.com/calendar?day={current_date}'
        page = scraper.get(url).text
        soup = BeautifulSoup(page, 'html.parser')
        table = soup.find('table', class_='calendar__table')
        
        for row in table.find_all('tr', class_='calendar__row'):
            event_time = row.find('td', class_='calendar__time')
            if event_time:
                event_time = get_date_time(event_time.text.strip())
            
                if event_time:
                    currency = row.find('td', class_='currency').text.strip()
                    impact = row.find('td', class_='impact').find('span')['class'][0]
                    event = row.find('td', class_='event').find('span').text.strip()
                    previous = row.find('td', class_='previous').text.strip()
                    forecast = row.find('td', class_='forecast').text.strip()
                    actual = row.find('td', class_='actual').text.strip()
                    
                    with open(file_path, 'a') as file:
                        # Write the extracted data to the file
                        file.write(f"{current_date}, {event_time}, {currency}, {impact}, {event}, {previous}, {forecast}, {actual}\n")
        
        # Move to the next date
        current_date = (datetime.strptime(current_date, "%b%d.%Y") + timedelta(days=1)).strftime("%b%d.%Y")

if __name__ == "__main__":
    output_file_path = "ffc_news_events_last_month.csv"
    
    # Call the scraping function for the last month
    scrape_forex_factory_last_month(output_file_path)
