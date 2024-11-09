import requests 
from bs4 import BeautifulSoup 
import re
import csv 


def fetch_event_data():
    url = "https://www.ticketmaster.com/" 
    response = requests.get(url) 

    parse_html = BeautifulSoup(response.content,"html.parser") 
    events = parse_html.find_all('div',class_=re.compile('[a-z])'))

    data = []


    with open('Ticket_data.csv','w', newline = '') as csv_conn: 
        write = csv.DictWriter(csv_conn,fieldnames= data[0].key())
        write.writeheader()
        write.writerows(data)
    

    pass 





if __name__ == "__main__":
    pass  