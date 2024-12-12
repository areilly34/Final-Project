from bs4 import BeautifulSoup 
import re
import csv 
import smtplib
import tabulate
import pandas as pd
import time 
from selenium import webdriver
import sys

def fetch_event_data():
    """ web scraps through the url to get event name, date, and location then store that to a csv file """
    
    # Gets the event the user is looking for and ensures it is a valid event type
    while True:
        event = input("What event are you looking for? (nfl, nba, nhl, golf, mlb): ")
        if event == 'nfl' or event == 'nba' or event == 'nhl' or event == 'golf' or event == 'mlb':
            break
        else:
            print("Invalid event. Please enter a valid event.\n")
            
   # Set up Chrome WebDriver
    driver = webdriver.Chrome()

    # Navigate to stubhub website 
    driver.get(f"https://www.stubhub.com/{event}-tickets")

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
    driver = webdriver.Chrome() # set up Chrome WebDriver 
    
    url = [] # empty url list to store all the links thats being read 
    ticket_name = [] # empty list to store all the ticket names 
    with open('data.csv') as file_conn:  # creating a connection to the data of tickets to get the link 
        heading = next(file_conn) # skipping the headers of the csv file 
        reader_obj = csv.reader(file_conn) # reading through the document and storing it as objects 
        for row in reader_obj: #reading through each object row by row 
            url.append(row[4]) # storing each link to the url list 
            ticket_name.append(row[1])
    

    ticket_count = []
    ticket_data = {"ticket_id":[],
                   "ticket_name":[],
            "ticket_section": [],
            "ticket_row": [],
            "ticket_price": [],
            } # ticket data dict th at stores all the ticket information
    ticket_id = 0 # id counter for the tickets 
    section_row = [] # data of section and rows joint data from the pages 
    t_section = [] # ticket section
    t_row = [] # ticket row 
    for i in range(len(ticket_name)): # for loop to loop through each ticket name and url onces 
        ticket = ticket_name[i] # each time through the loop it gets the ticket name 
        link = url[i] # each time through the loop it gets the url of that ticket name 
        
        
        driver.get(link+'?quantity=1') # searches for the link but the +'?quantity=1' is saying we looking for 1 ticket each time. normally when  you open it you need to pick how many tickets you want. this just by pass it 
        time.sleep(1) # this will help us not get block on the website since we are looking thorugh a lot of links. its also the internet rule 
        page = driver.page_source
        parse_html = BeautifulSoup(page,"html.parser") # parse HTML content 

        ticket_section_row = parse_html.find_all('div', class_='sc-hlalgf-0 sc-hlalgf-6 jfjuff jXdyTR') # gets all the ticket section and rows in the page
        for i_section in ticket_section_row: # loops through the parsed list of section and row list 
            ticket_id +=1 # adds a id to each ticket that has the row and section
            ticket_count.append(ticket) # adds the name to the list of names ticket so that each section and rows corresponds with the ticket name 
            ticket_data["ticket_id"].append(ticket_id) # creates the same id for the same ticket that is being looked at 
            section_row.append(i_section.get_text('span')if i_section else 'N/AspanN/A') # addds the section and rows to the section rows list that is connected by span in the html
            
        ticket_price = parse_html.find_all('div', class_="sc-hlalgf-0 sc-hlalgf-1 jfjuff tOKfM") # gets all the html prices on the page 
        for i_price in ticket_price: # loops through  the parsed html list of all prices on the page
            ticket_data["ticket_price"].append(i_price.get_text() if i_price else 'N/A') # gets each price from the ticket_price parse html then add it to ticket data['ticket price]
    
    for section in section_row: # loops through the section and rows string to get each elemement at a time 
        split =section.split('span') # splits the sections and rows string at 'span' ex:Section 104spanRow J turns to Section[0] Row J[1]
        t_section.append(split[0].strip()) # gets the sections then add it to section list 
        t_row.append(split[1].strip() if len(split) > 1 else 'N/A') # gets the rows then adds it to rows list. also adds 'N/A' if there is no rows in that section
    ticket_data["ticket_section"].extend(t_section) # adds the list of sections to the ticket section key in the ticket data 
    ticket_data["ticket_row"].extend(t_row) # adds the list of rows to the ticket row key in the ticket data 
    ticket_data["ticket_name"].extend(ticket_count) # appends the list of ticket out for each time thro
    
    driver.quit() # stops the driver 
    
    with open("Ticket_info.csv", "w", newline="") as csvfile:

        writer = csv.DictWriter(csvfile, fieldnames=ticket_data.keys())  # create writer with header based on keys

        writer.writeheader()  # write header row

        for row in zip(ticket_data["ticket_id"],ticket_data["ticket_name"],ticket_data["ticket_section"], ticket_data["ticket_row"],ticket_data["ticket_price"]):  # Iterate through values in each column

            writer.writerow(dict(zip(ticket_data.keys(), row)))  # write each row as a dictionary


# Define the filtering function
def filter_events_by_activity(events, activity):
    """
    Filters a list of events by the specified activity and sorts them by type.

    Args:
        events (list): List of event dictionaries.
        activity (str): Desired activity to filter by.

    Returns:
        list: A filtered and sorted list of events.
    """
    # Filter events by the specified activity
    filtered_events = [event for event in events if event["activity"] == activity]
    
    # Sort filtered events by type
    sorted_events = sorted(filtered_events, key=lambda event: event["type"])
    
    return sorted_events

# Define the sorting function
def sort_tickets_by_price(tickets, order="asc"):
    """
    Sorts a list of tickets by price in ascending or descending order.

    Args:
        tickets (list): List of ticket dictionaries.
        order (str): Sort order ('asc' for ascending, 'desc' for descending).

    Returns:
        list: A list of tickets sorted by price.
    """
    # Determine if sorting is in ascending or descending order
    reverse = order == "desc"
    
    # Sort the tickets by price
    sorted_tickets = sorted(tickets, key=lambda ticket: ticket["price"], reverse=reverse)
    
    return sorted_tickets

# Example usage of filter_events_by_activity
desired_activity = "music"
filtered_events = filter_events_by_activity(events, desired_activity)

print("Filtered events by activity (music):")
for event in filtered_events:
    print(f"{event['name']} ({event['type']}) - ${event['price']}")

# Example usage of sort_tickets_by_price
sorted_tickets_asc = sort_tickets_by_price(events, order="asc")
sorted_tickets_desc = sort_tickets_by_price(events, order="desc")

print("\nTickets sorted by price in ascending order:")
for ticket in sorted_tickets_asc:
    print(f"{ticket['name']} ({ticket['type']}) - ${ticket['price']}")

print("\nTickets sorted by price in descending order:")
for ticket in sorted_tickets_desc:
    print(f"{ticket['name']} ({ticket['type']}) - ${ticket['price']}")

def get_user_selection():
    """
    Allows users to choose an event from a list and returns the details of chosen event

    Parameters: 
    events (list): A list of dictionaries, where each dictionary contains event details

    Returns: The select event dictionary
    """
    with open("data.csv", 'r') as event_data:
        reader = csv.DictReader(event_data)
        events = list(reader)
        
    with open("Ticket_info.csv", "r") as ticket_info:
        ticket_reader = csv.DictReader(ticket_info)
        tickets = list(ticket_reader)
    
    for index, event in enumerate(events, start=1):
        print(f"{index}. {event.get('event name', 'Unknown Event')} on {event.get('event location', 'Unknown Date')} at {event.get('event date', 'Unknown Venue')}")

    if not events:
        print("No events available to select")
        sys.exit()
    while True:
        try:
            selection = int(input("\nPlease select an event by number: "))
            if 1 <= selection <= len(events):
                user_event = events[selection - 1]
                available_tickets = []
                for ticket in tickets:
                    if ticket["ticket_name"] == user_event["event name"]:
                        available_tickets.append(ticket)
                return (user_event, available_tickets, selection)
            else:
                print(f"Invalid selection. Please enter a number between 1 and {len(events)}")
    
        except ValueError:
            print("Invalid input. Please enter a valid number.")
class TicketDisplay:
    """This will display the ticket information the user selected """
    
    def __init__(self, event, available_tickets):
        """ Initialization of the events and available tickets 
            Args: 
            event(str): it gets the event that is chosen by the user 
            available_tickets(str): it gets the avaiable ticket based on the user selection
            """
        
        self.event = event
        self.available_tickets = available_tickets
        
    def display_event_details(self):
        """Displays information for the specific event chosen
        Parameters: event (dict): A dictionary containiing information of the event such as name, date, venue, website
        Returns: None
        """
        # Prints event details for user to see
        try:
            print("\nEvent Details")
            print(f"Name: {self.event.get('event name', 'N/A')}")
            print(f"Date: {self.event.get('event location', 'N/A')}")
            print(f"Venue: {self.event.get('event date', 'N/A')}")
            print(f"Source: {self.event.get('ticket ', 'N/A')}")
            print("\nAvailable Tickets:")

            #  If there are tickets for the event ticket information gets printed out
            if self.available_tickets:
                for ticket in self.available_tickets:
                    print(f" - Section: {ticket.get('ticket_section', 'Unknown')}, Seat: {ticket.get('ticket_row', 'Unknown')}, Price: {ticket.get('ticket_price', 'Unknown')}")
            else:
                print("No ticket information available")
        except:
            pass
    
def generate_ticket_comparison_report(tickets):
    """
    Displays a table of tickets to user 
    Args: 
        tickets: List of dictionaries with ticket info
    Returns:
        table: table with ticket info 
    """
    
    # Changes ticket_price values from str to int for proper sorting, also drops '$' sign
    for ticket in tickets:
            ticket["ticket_price"] = int(ticket['ticket_price'].replace('$', ''))
    
    # Creates a DataFrame from tickets
    df = pd.DataFrame(tickets)
    
    run_loop = True
    
    # Returns a sorted DataFrame depending on users choice, renames ticket_price column for more user clarity 
    while run_loop:
        try:
            order = str(input("\nDisplay tickets priced low to high or high to low? (type 'low to high' or 'high to low') "))
            if order == 'high to low':    
                df = df.sort_values(by = 'ticket_price', ascending = False)
                df.rename(columns={'ticket_price': 'ticket_price (in dollars $)'}, inplace=True)
                print(tabulate.tabulate(df, headers = 'keys', tablefmt = 'fancy_grid'))
                run_loop = False    
                    
            elif order == 'low to high':
                df = df.sort_values(by = 'ticket_price', ascending = True)
                df.rename(columns={'ticket_price': 'ticket_price (in dollars $)'}, inplace=True)
                print(tabulate.tabulate(df, headers = 'keys', tablefmt = 'fancy_grid'))
                run_loop = False
            
            # Catches invaild commands user may enter
            else:
                print("Invalid command. Please enter a valid command.")
            
        except ValueError:
            print("Invalid command. Please enter valid command.")
            
    
    while True:
        # User picks a ticket, ticket is returned if it is valid
        try:
            user_ticket = int(input("Please choose a ticket by the number in the first column and enter number: "))
            
            if 0 <= user_ticket <= len(tickets):
                return int(user_ticket)
            # Catches invaild commans user may enter
            else:
                print("Invalid number. Please enter a valid number.\n")
        except ValueError:
            print("Invalid number. Please enter a valid number.\n")


def send_price_alert(available_tickets, user_ticket):
    """
    Sends email to user with ticket information
    Agrs:
        ticket: Dictionary with ticket info
        user_email: Email of the user
    Returns:
    
    """
    # Gets ticket from a list of tickets
    ticket = available_tickets[user_ticket]
    
    # Checks that user_email is a valid email
    while True:
        user_email = input("Please enter email to receive ticket information: ")
        email_style = (r"(^[a-zA-Z0-9_.±]+@[a-zA-Z0-9-]+.[a-zA-Z0-9-.]+$)")
        if re.match(email_style, user_email):
            break
        else:
            print("Invalid email. Please enter a valid email.\n")
    
    # Format body of email so the information is more readable for user
    subject = 'Ticket Information'
    body = (f"Name: {ticket['ticket_name']}\nSection: {ticket['ticket_section']}\nRow: {ticket['ticket_row']}\nPrice: {ticket['ticket_price']}")
    msg = f"Subject: {subject}\n\n{body}"

    # Login credentials for account sending email
    user = 'finalproject326@gmail.com'
    password = 'jrmuzbocwbhwiipm'
    send_to = user_email

    # Creates smtp object and sends email to user
    with smtplib.SMTP('smtp.gmail.com', 587) as smtpObj:
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.ehlo()
    
        # Logs into account using credentials above
        smtpObj.login(user, password)
        smtpObj.sendmail(user, send_to, msg)
        print("Email sent.")   


if __name__ == "__main__":
    fetch_event_data()
    fetch_ticket_price()
    user_event, available_tickets, selection = get_user_selection()
    display = TicketDisplay(user_event, available_tickets)
    display.display_event_details()
    user_ticket = generate_ticket_comparison_report(available_tickets)
    send_price_alert(available_tickets, user_ticket)
    print("\nThank you for using the ticket price tracker!")
