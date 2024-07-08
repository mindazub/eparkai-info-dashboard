import requests
from bs4 import BeautifulSoup
import json

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

        project_list.append({
            'title': title,
            'image_url': image_url,
            'small_image_url': small_image_url,
            'purchase_price_info': purchase_price_info,
            'old_price': old_price,
            'maintenance_price_info': maintenance_price_info,
            'status': status
        })

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

print("Starting to fetch all projects...")
projects = fetch_all_projects()
print("Finished fetching all projects.")

# Saving the data to a JSON file
output_file = 'eparkai_projects.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(projects, f, ensure_ascii=False, indent=4)

print(f"Data saved to {output_file}")
print("Script finished successfully.")
