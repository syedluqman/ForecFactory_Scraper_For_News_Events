import cloudscraper
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
import os
import csv

def get_date_time(event_time):
    match = re.search(r'(\d+)(:\d{2})([ap]m)', event_time)
    if match:
        hour, minutes, am_pm = match.groups()
        hour = int(hour) + 12 if am_pm == 'pm' else int(hour)
        return f"{hour:02}:{minutes}"
    return None

def scrape_forex_factory_between_dates(start_date, end_date, file_path):
    scraper = cloudscraper.create_scraper()
    
    current_date = start_date
    
    # Create column names
    columns = ['Date', 'Time', 'Currency', 'Impact', 'Event', 'Previous', 'Forecast', 'Actual']
    
    # Check if the CSV file exists, and generate if not
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(columns)
    
    while current_date <= end_date:
        url_date_format = current_date.strftime("%b%d.%Y")  # Format for URL
        url = f'https://www.forexfactory.com/calendar?day={url_date_format}'
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
                    
                    with open(file_path, 'a', newline='') as file:
                        csv_writer = csv.writer(file)
                        # Write the extracted data to the file
                        csv_writer.writerow([url_date_format, event_time, currency, impact, event, previous, forecast, actual])
        
        # Move to the next date
        current_date += timedelta(days=1)

if __name__ == "__main__":
    output_file_path = "ffc_news_events.csv"
    
    start_date_input = input("Enter the start date (Format: MMMDD.YYYY): ")
    end_date_input = input("Enter the end date (Format: MMMDD.YYYY): ")
    start_date = datetime.strptime(start_date_input, "%b%d.%Y")
    end_date = datetime.strptime(end_date_input, "%b%d.%Y")
    
    # Call the scraping function between the specified dates
    scrape_forex_factory_between_dates(start_date, end_date, output_file_path)
