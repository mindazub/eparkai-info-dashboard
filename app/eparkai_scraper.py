import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import re

db_name = 'eparkai_projects.db'
base_url = 'https://www.eparkai.lt'

def create_table():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''DROP TABLE IF EXISTS projects''')  # Drop the table if it exists
    c.execute('''CREATE TABLE projects (
                 title TEXT,
                 image_url TEXT,
                 small_image_url TEXT,
                 purchase_price REAL,
                 old_price REAL,
                 maintenance_price REAL,
                 status TEXT,
                 total_kw REAL,
                 progress_percentage REAL,
                 reserved_percentage REAL,
                 reserved_kw REAL,
                 remaining_percentage REAL,
                 remaining_kw REAL
                 )''')
    conn.commit()
    conn.close()

def insert_data(data):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.executemany('''INSERT INTO projects (
                     title, image_url, small_image_url, purchase_price, old_price, maintenance_price,
                     status, total_kw, progress_percentage, reserved_percentage, reserved_kw, remaining_percentage, remaining_kw
                     ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
    conn.commit()
    conn.close()

def parse_numeric(value, default=0):
    # Replace ',' with '.' and then handle multiple dots
    value = value.replace(',', '.')
    parts = value.split('.')
    if len(parts) > 2:
        value = '.'.join(parts[:2])  # Keep only the first part and one dot
    return float(re.sub(r'[^\d.]', '', value)) if value else default

def fetch_project_data(page_number):
    print(f"Fetching data from page {page_number}...")
    url = f"https://www.eparkai.lt/projektai?page={page_number}"
    response = requests.get(url)
    if response.status_code == 404:
        print(f"Page {page_number} not found (404). Stopping.")
        return None
    if response.status_code != 200:
        print(f"Failed to fetch page {page_number} (status code: {response.status_code}). Skipping.")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    projects = soup.find_all('a', class_=['project-widget info-button', 'project-widget info-button project-status-sold'])

    project_list = []
    for project in projects:
        title = project.find('h3', class_='project-title').text.strip() if project.find('h3', class_='project-title') else ''
        image_tag = project.find('div', class_='project-image').find('img') if project.find('div', class_='project-image') else None
        image_url = base_url + image_tag['src'] if image_tag else ''
        
        contractor_image_tag = project.find('div', class_='contractor-wrapper').find('img') if project.find('div', class_='contractor-wrapper') else None
        small_image_url = base_url + contractor_image_tag['src'] if contractor_image_tag else ''

        status = 'YRAGALIOS' if 'project-status-sold' not in project['class'] else 'ISPARDUOTA'
        
        project_info_wrapper = project.find('div', class_='project-info-wrapper tree-colums')
        
        # Get "Pirkimo kaina"
        price_info_div = project_info_wrapper.find('div', class_='project-summary-col summary-with-discount') if project_info_wrapper else None
        if not price_info_div:
            price_info_div = project_info_wrapper.find('div', class_='project-summary-col') if project_info_wrapper else None
        purchase_price_info = parse_numeric(price_info_div.find('div', class_='project-info').text.strip()) if price_info_div else 0

        # Get old price line
        old_price_div = project_info_wrapper.find('div', class_='old-price-line') if project_info_wrapper else None
        old_price = parse_numeric(old_price_div.find('div', class_='project-info').text.strip(), default=0) if old_price_div else 0

        # Get "Metine prieziuros kaina"
        maintenance_price_div = project_info_wrapper.find('div', class_='project-summary-col') if project_info_wrapper else None
        maintenance_price_info = parse_numeric(maintenance_price_div.find('div', class_='project-info').text.strip()) if maintenance_price_div else 0
        
        # Get progress bar info
        progress_bar = project.find('div', class_='progress-bar')
        total_text = parse_numeric(progress_bar.find('div', class_='total-text').text.strip()) if progress_bar else 0
        progress_percentage = parse_numeric(progress_bar.find('div', class_='project-progress')['style'].split(':')[1].strip()) if progress_bar else 0

        project_info_wrapper_stats = progress_bar.find('div', class_='project-info-wrapper-stats') if progress_bar else None
        reserved_info = parse_numeric(project_info_wrapper_stats.find('p', class_='left').text.strip()) if project_info_wrapper_stats else 0
        reserved_kw = parse_numeric(project_info_wrapper_stats.find('p', class_='left').find('span', class_='desc').text.strip()) if project_info_wrapper_stats else 0
        remaining_info = parse_numeric(project_info_wrapper_stats.find('p', class_='right').text.strip()) if project_info_wrapper_stats else 0
        remaining_kw = parse_numeric(project_info_wrapper_stats.find('p', class_='right').find('span', class_='desc').text.strip()) if project_info_wrapper_stats else 0

        project_list.append((
            title, image_url, small_image_url, purchase_price_info, old_price, maintenance_price_info,
            status, total_text, progress_percentage, reserved_info, reserved_kw, remaining_info, remaining_kw
        ))

    print(f"Found {len(project_list)} projects on page {page_number}.")
    return project_list

async def fetch_all_projects():
    all_projects = []
    for page_number in range(4):  # Limiting to pages 0, 1, 2, 3
        projects = fetch_project_data(page_number)
        if projects is None:
            break
        all_projects.extend(projects)

    return all_projects

def save_projects_to_db(projects):
    create_table()
    insert_data(projects)
