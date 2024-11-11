import requests 
from bs4 import BeautifulSoup 
import re
import csv 


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
    







if __name__ == "__main__":
    pass  