import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from requests.exceptions import RequestException
from flask import Flask, render_template

# Initialize Flask app
app = Flask(__name__)

# List of URLs to scrape
URLS = [
    'https://store.steampowered.com/app/2769570/Fable/',
    'https://www.xbox.com/en-US/xbox-game-studios',
    'https://playground-games.com/about/'
]

# Configure headers to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def scrape_url(url):
    try:
        time.sleep(1)
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        data = {'url': url, 'timestamp': pd.Timestamp.now()}

        # Steam Store Page
        if 'steampowered.com' in url:
            data['title'] = soup.find('div', class_='apphub_AppName').get_text(strip=True) if soup.find('div', class_='apphub_AppName') else 'N/A'
            data['release date'] = soup.find('div', class_='date').get_text(strip=True) if soup.find('div', class_='date') else 'N/A'
            data['description'] = soup.find('div', class_='game_area_description').get_text(strip=True) if soup.find('div', class_='game_area_description') else 'N/A'
            data['min_req'] = soup.find('div', class_='game_area_sys_req_leftCol').get_text(strip=True) if soup.find('div', class_='game_area_sys_req_leftCol') else 'N/A'
            data['rec_req'] = soup.find('div', class_='game_area_sys_req_rightCol').get_text(strip=True) if soup.find('div', class_='game_area_sys_req_rightCol') else 'N/A'

        # Playground Games About Page
        elif 'playground-games.com' in url:
            data['about'] = soup.find('div', class_='wow fadeIn').get_text(strip=True, separator=' ') if soup.find('div', class_='wow fadeIn') else 'N/A'

        # Xbox Game Studios Page
        elif 'xbox.com' in url:
            data['about'] = soup.find('div', class_='m-banner jumpgcontainer').get_text(strip=True) if soup.find('div', class_='m-banner jumpgcontainer') else 'N/A'

        return data

    except RequestException as e:
        print(f"Request failed for {url}: {str(e)}")
        return None
    except Exception as e:
        print(f"Error processing {url}: {str(e)}")
        return None

def get_scraped_data():
    scraped_data = []
    
    # Process each URL
    for url in URLS:
        print(f"Scraping {url}...")
        result = scrape_url(url)
        if result:
            scraped_data.append(result)
    
    return scraped_data

@app.route('/')
def index():
    scraped_data = get_scraped_data()

    if scraped_data:
        return render_template('index.html', scraped_data=scraped_data)
    else:
        return "No data was scraped"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
