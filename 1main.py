import requests
from bs4 import BeautifulSoup
import sqlite3

# Define the SQLite database and table
db_name = 'eparkai_projects.db'

def create_table():
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
                 title TEXT,
                 image_url TEXT,
                 small_image_url TEXT,
                 purchase_price_info TEXT,
                 old_price TEXT,
                 maintenance_price_info TEXT,
                 status TEXT,
                 total_text TEXT,
                 progress_percentage TEXT,
                 reserved_info TEXT,
                 reserved_kw TEXT,
                 remaining_info TEXT,
                 remaining_kw TEXT
                 )''')
    conn.commit()
    conn.close()

def insert_data(data):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.executemany('''INSERT INTO projects (
                     title, image_url, small_image_url, purchase_price_info, old_price, maintenance_price_info,
                     status, total_text, progress_percentage, reserved_info, reserved_kw, remaining_info, remaining_kw
                     ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
    conn.commit()
    conn.close()

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
        title = project.find('h3', class_='project-title').text.strip()
        image_tag = project.find('div', class_='project-image').find('img')
        image_url = image_tag['src'] if image_tag else ''
        
        contractor_image_tag = project.find('div', class_='contractor-wrapper').find('img')
        small_image_url = contractor_image_tag['src'] if contractor_image_tag else ''

        status = 'YRAGALIOS' if 'project-status-sold' not in project['class'] else 'ISPARDUOTA'
        
        project_info_wrapper = project.find('div', class_='project-info-wrapper tree-colums')
        
        # Get "Pirkimo kaina"
        price_info_div = project_info_wrapper.find('div', class_='project-summary-col summary-with-discount')
        if not price_info_div:
            price_info_div = project_info_wrapper.find('div', class_='project-summary-col')
        purchase_price_info = price_info_div.find('div', class_='project-info').text.strip() if price_info_div else 'N/A'

        # Get old price line
        old_price_div = project_info_wrapper.find('div', class_='old-price-line')
        old_price = old_price_div.find('div', class_='project-info').text.strip() if old_price_div else 'N/A'

        # Get "Metine prieziuros kaina"
        maintenance_price_div = project_info_wrapper.find('div', class_='project-summary-col')
        maintenance_price_info = maintenance_price_div.find('div', class_='project-info').text.strip() if maintenance_price_div else 'N/A'
        
        # Get progress bar info
        progress_bar = project.find('div', class_='progress-bar')
        total_text = progress_bar.find('div', class_='total-text').text.strip()
        progress_percentage = progress_bar.find('div', class_='project-progress')['style'].split(':')[1].strip()
        
        project_info_wrapper_stats = progress_bar.find('div', class_='project-info-wrapper-stats')
        reserved_info = project_info_wrapper_stats.find('p', class_='left').text.strip().replace('\n', ' ')
        reserved_kw = project_info_wrapper_stats.find('p', class_='left').find('span', class_='desc').text.strip()
        remaining_info = project_info_wrapper_stats.find('p', class_='right').text.strip().replace('\n', ' ')
        remaining_kw = project_info_wrapper_stats.find('p', class_='right').find('span', class_='desc').text.strip()

        project_list.append((
            title, image_url, small_image_url, purchase_price_info, old_price, maintenance_price_info,
            status, total_text, progress_percentage, reserved_info, reserved_kw, remaining_info, remaining_kw
        ))

    print(f"Found {len(project_list)} projects on page {page_number}.")
    return project_list

def fetch_all_projects():
    all_projects = []
    for page_number in range(4):  # Limiting to pages 0, 1, 2, 3
        projects = fetch_project_data(page_number)
        if projects is None:
            break
        all_projects.extend(projects)

    return all_projects

# Create database table
create_table()

print("Starting to fetch all projects...")
projects = fetch_all_projects()
print("Finished fetching all projects.")

# Insert data into SQLite database
insert_data(projects)
print("Data inserted into SQLite database successfully.")
