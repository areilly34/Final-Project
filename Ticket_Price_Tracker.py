
from bs4 import BeautifulSoup 
import re
import csv 
import smtplib
import tabulate
import pandas as pd
import time 
from selenium import webdriver

def fetch_event_data():
    """ web scraps through the url to get event name, date, and location then store that to a csv file """
   # Set up Chrome WebDriver
    driver = webdriver.Chrome()

    # Navigate to stubhub website 
    driver.get("https://www.stubhub.com/nba-tickets")

    time.sleep(1)
    # Retrieve the page source
    page = driver.page_source

    # Close the driver
    driver.quit()

    parse_html = BeautifulSoup(page,"html.parser") # parse HTML content 

    data_link = []
    data ={"event_id":[],
            "event name": [],
            "event date": [],
            "event location": [],
            "ticket ":[]
           } # data dict to keep track of all the information 
    event_id = 0
    event_name = parse_html.find_all('div', class_='sc-1mafo1b-4 dvCFno') # finds all the evnet names on the url 
    for i_name in event_name: # looping through each event name
        event_id+=1 # creating id for each event 
        data["event name"].append(i_name.get_text()) # adding all the evnet names to the event name key 
        data['event_id'].append(event_id) # creating event id and adding it to event id key 

    
    event_date = parse_html.find_all('div', class_='sc-ja5jff-4') # finds all event dates  on the url 
    data["event date"].extend([i_date.get_text()for i_date in event_date]) # using list comprehension to add each event date to event date key 
    event_location = parse_html.find_all('div', class_='sc-1pilhev-2 dBFhOm') # finds all event location on the url 
    data["event location"].extend([i_location.get_text()for i_location in event_location]) #using list comprehension to add each event location to event location key
    ticket_link = parse_html.find_all('a', class_='sc-1x2zy2i-2 cYRIRc') # finds all links on the url  
    for i_link in ticket_link:
        link = i_link.get("href") # getting each link from the find all link 
        if 'event' in link: # checks to make sure each link is a event
            data_link.append(link) # adds it to link data 
    
    data['ticket '].extend(data_link) # adding it to ticket key in the data dict 


    # open file in write mode

    with open("data.csv", "w", newline="") as csvfile: # creating the connection

        writer = csv.DictWriter(csvfile, fieldnames=data.keys())  # create writer with header based on keys

        writer.writeheader()  # write header row

        for row in zip(data["event_id"], data["event name"], data["event location"],data["event date"],data["ticket "]):  # iterate through values in each column

            writer.writerow(dict(zip(data.keys(), row)))  # write each row as a dictionary

def fetch_ticket_prices(event_id): 
    """ using the event id to get ticket prices of the event based on row and section. Then return a list of that information"""
    pass
    
def display_event_details(event):
    """Displays information for the specific event chosen
    Parameters: event (dict): A dictionary containiing information of the event such as name, date, venue, website
    Returns: None
    """
    try:
        print("Event Details")
        print(f"Name: {event.get('name', 'N/A')}")
        print(f"Date: {event.get('date', 'N/A')}")
        print(f"Venue: {event.get('venue', 'N/A')}")
        print(f"Source: {event.get('source', 'N/A')}")
        print("Available Tickets:")

        if "tickets" in event and event["tickets"]:
            for ticket in event["tickets"]:
                print(f" - Section: {ticket.get('section', 'Unknown')}, Seat: {ticket.get('seat', 'Unknown')}, "
                      f"Price: ${ticket.get('price', 'Unknown')}")
        else:
            print("No ticket information available")
            
def get_user_selection(events):
    """
    Allows users to choose an event from a list and returns the details of chosen event

    Parameters: 
    events (list): A list of dictionaries, where each dictionary contains event details

    Returns: The select event dictionary
    """
    if not events:
        print("No events available to select")
        return None
    for index, event in enumerate(events, start=1):
        print(f"{index}. {event.get('name', 'Unknown Event')} on {event.get('date', 'Unknown Date')} at {event.get('venue', 'Unknown Venue')}")

    while True:
        try:
            selection = int(input("Please select an event by number: "))
            if 1 <= selection <= len(events):
                return events[selection - 1]
            else:
                print(f"Invalid selection. Please enter a number between 1 and {len(events)}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            

def generate_ticket_comparison_report(tickets):
    """
    Displays a table of tickets to user 
    Args: 
        tickets: List of dictionaries with ticket info
    Returns:
        table: table with ticket info 
    """
    # Asks user how they want table to be sorted
    order = input("Display tickets price low to high or high to low? (type 'low to high' or 'high to low) ")
    
    # Creates a DataFrame from tickets
    df = pd.DataFrame(tickets)
    
    # Returns a sorted DataFrame
    if order == 'high to low':    
        df = df.sort_values(by = 'price', ascending = False)
        return(tabulate.tabulate(df, headers = 'keys', tablefmt = 'fancy_grid'))
    
    elif order == 'low to high':
        df = df.sort_values(by = 'price', ascending = True)
        return(tabulate.tabulate(df, headers = 'keys', tablefmt = 'fancy_grid'))
    
    else:
        return ("Invalid command")
    
    
def send_price_alert(ticket, user_email):
    """
    Sends email to user with ticekt information
    Agrs:
        ticket: Dictionary with ticket info
        user_email: Email of the user
    Returns:
    
    """
    # Checks that user_email is a valid email
    email_style = (r"(^[a-zA-Z0-9_.±]+@[a-zA-Z0-9-]+.[a-zA-Z0-9-.]+$)")
    assert re.match(email_style, user_email), "Invalid email"
    
    # Format body so the information is more usable for user
    subject = 'Ticket Information'
    body = ticket
    msg = f"Subject: {subject}\n\n{body}"

    # Login credentials
    user = 'finalproject326@gmail.com'
    password = 'jrmuzbocwbhwiipm'
    send_to = user_email

    # Creates smtp object and sends email to user
    with smtplib.SMTP('smtp.gmail.com', 587) as smtpObj:
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.ehlo()
    
        smtpObj.login(user, password)
        smtpObj.sendmail(user, send_to, msg)
        print("Email sent.")

if __name__ == "__main__":
    pass  
