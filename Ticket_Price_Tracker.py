import requests 
from bs4 import BeautifulSoup 
import re
import csv 
import smtplib
import tabulate
import pandas as pd

def fetch_event_data():

    url = "https://www.ticketmaster.com/" 
    response = requests.get(url) # sending a request to the website 

    parse_html = BeautifulSoup(response.content,"html.parser") # parse HTML content 

    data = []
    for ticket in parse_html: 

        data = {"event_id": ticket.find('div',class_= "event-id").content.strip(),
        "event": ticket.find('h1',class_= "event-title").content.strip(),
        "location": ticket.find('div',class_= "event-venue").content.strip(),
        "ticket availability": ticket.find('button',class_= "buy-tickets").content.strip()}
    
    with open('Ticket_data.csv','w', newline = '') as csv_conn:  
        write = csv.DictWriter(csv_conn,fieldnames= data[0].key())
        write.writeheader()
        write.writerows(data)
    



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