import requests 
from bs4 import BeautifulSoup 
import re
import csv 


def fetch_event_data():

    url = "https://www.ticketmaster.com/" 
    response = requests.get(url) # sending a request to the website 

    parse_html = BeautifulSoup(response.content,"html.parser") # parse HTML content 

    events = parse_html.find_all('div',class_=re.compile('[a-z])')) # using regex to scape the ticket information 

    data = []

    #not used yet but will be the end goal to store all the scaped information. 
    with open('Ticket_data.csv','w', newline = '') as csv_conn:  
        write = csv.DictWriter(csv_conn,fieldnames= data[0].key())
        write.writeheader()
        write.writerows(data)
    

    pass 





if __name__ == "__main__":
    pass  