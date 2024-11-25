import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

def scrape_academic_calendar(url):
    """
    Scrape the academic calendar from the given URL.
    
    Args:
        url (str): The URL of the academic calendar page.
        
    Returns:
        dict: A dictionary containing academic dates categorized by term.
    """
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch the webpage. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Initialize a dictionary to hold the academic dates
    academic_dates = {}

    # Find all term sections (e.g., Fall 2024, Spring 2025)
    term_sections = soup.find_all('h3')
    for term in term_sections:
        term_name = term.get_text(strip=True)
        # Initialize a list to hold dates for the current term
        dates_list = []
        # Find the next sibling which contains the dates
        dates_table = term.find_next_sibling('table')
        if dates_table:
            rows = dates_table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) == 2:
                    date = cols[0].get_text(strip=True)
                    description = cols[1].get_text(strip=True)
                    dates_list.append({'date': date, 'description': description})
        # Add the term and its dates to the dictionary
        academic_dates[term_name] = dates_list

    return academic_dates

def save_calendar_to_file(data, file_path):
    """
    Save the academic calendar to a JSON file.
    
    Args:
        data (dict): The academic calendar data.
        file_path (str): The path to the JSON file.
    """
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def load_calendar_from_file(file_path):
    """
    Load the academic calendar from a JSON file.
    
    Args:
        file_path (str): The path to the JSON file.
        
    Returns:
        dict: The academic calendar data, or None if the file does not exist.
    """
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return None

def main():
    url = "https://registrar.nd.edu/calendars/"
    json_file = "academic_calendar.json"

    # Load existing data from the file if it exists
    existing_calendar = load_calendar_from_file(json_file)

    if existing_calendar:
        # Check the latest term in the data to determine if an update is needed
        latest_term = max(existing_calendar.keys(), key=lambda term: datetime.strptime(term.split()[-1], "%Y"))
        current_year = datetime.now().year
        if str(current_year) in latest_term:
            print("The academic calendar is up to date.")
            return existing_calendar

    # If the data is missing or outdated, scrape the website
    print("Scraping the academic calendar...")
    academic_calendar = scrape_academic_calendar(url)
    if academic_calendar:
        save_calendar_to_file(academic_calendar, json_file)
        print("Saved the updated academic calendar.")
    else:
        print("Failed to update the academic calendar.")
    
    return academic_calendar

if __name__ == "__main__":
    calendar = main()
    if calendar:
        for term, dates in calendar.items():
            print(f"\n{term}:")
            for entry in dates:
                print(f"  {entry['date']}: {entry['description']}")