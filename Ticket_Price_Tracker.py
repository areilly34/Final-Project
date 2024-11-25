
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

def fetch_ticket_price():
    """ This methond will read in a csv file of ticket data that includes link to prices. 
        Then using that link extract the section,row, and ticket price for that url.
        The ticket id matchs the event id 
        """
    driver = webdriver.Chrome()
    
    url = [] # empty url list to store all the links thats being read 

    with open('data.csv') as file_conn:  # creating a connection to the data of tickets to get the link 
        heading = next(file_conn) # skipping the headers of the csv file 
        reader_obj = csv.reader(file_conn) # reading through the document and storing it as objects 
        for row in reader_obj: #reading through each object row by row 
            url.append(row[4]) # storing each link to the url list 
            
    
    ticket_data = {"ticket_id":[],
            "ticket_section": [],
            "ticket_row": [],
            "ticket_price": [],
            } # ticket data dict that stores all the ticket information
    ticket_id = 0 # id counter for the tickets 
    section_row = [] # data of section and rows joint data from the pages 
    t_section = [] # ticket section
    t_row = [] # ticket row 
    for link in url:
        
        driver.get(link+'?quantity=1') # searches for the link but the +'?quantity=1' is saying we looking for 1 ticket each time. normally when  you open it you need to pick how many tickets you want. this just by pass it 
        time.sleep(1) # this will help us not get block on the website since we are looking thorugh a lot of links. its also the internet rule 
        page = driver.page_source
        ticket_id +=1 # icrements through the links. so each time a new ticket is taking a look at it will have the same id as the data.csv 
        parse_html = BeautifulSoup(page,"html.parser") # parse HTML content 

        ticket_section_row = parse_html.find_all('div', class_='sc-hlalgf-0 sc-hlalgf-6 jfjuff jXdyTR')
        for i_section in ticket_section_row: # loops through the parsed list of section and row list 
            ticket_data["ticket_id"].append(ticket_id) # creates the same id for the same ticket that is being looked at 
            section_row.append(i_section.get_text('span')) # addds the section and rows to the section rows list that is connected by span in the html
            
        ticket_price = parse_html.find_all('div', class_="sc-hlalgf-0 sc-hlalgf-1 jfjuff tOKfM") # gets all the html prices on the page 
        for i_price in ticket_price: # loops through  the parsed html list of all prices on the page
            ticket_data["ticket_id"].append(ticket_id) # creates a id for the ticket but the code breaks when this line gets taken out but does not effect the data all. 
            ticket_data["ticket_price"].append(i_price.get_text()) # gets each price from the ticket_price parse html then add it to ticket data['ticket price]
    
    for section in section_row: # loops through the section and rows string to get each elemement at a time 
        split =section.split('span') # splits the sections and rows string at 'span' ex:Section 104spanRow J turns to Section[0] Row J[1]
        t_section.append(split[0].strip()) # gets the sections then add it to section list 
        t_row.append(split[1].strip() if len(split) > 1 else 'N/A') # gets the rows then adds it to rows list. also adds 'N/A' if there is no rows in that section
    ticket_data["ticket_section"].extend(t_section) # adds the list of sections to the ticket section key in the ticket data 
    ticket_data["ticket_row"].extend(t_row) # adds the list of rows to the ticket row key in the ticket data 
    

    driver.quit() # stops the driver 
    
    with open("Ticket_info.csv", "w", newline="") as csvfile: # creating a connection to the file 

        writer = csv.DictWriter(csvfile, fieldnames=ticket_data.keys())  # create writer with header based on keys

        writer.writeheader()  # write header row

        for row in zip(ticket_data["ticket_id"], ticket_data["ticket_section"], ticket_data["ticket_row"],ticket_data["ticket_price"]):  # iterate through values in each column

            writer.writerow(dict(zip(ticket_data.keys(), row)))  # write each row as a dictionary

    
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
