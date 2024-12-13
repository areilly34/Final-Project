import unittest
from unittest.mock import patch, MagicMock
from Ticket_Price_Tracker import fetch_event_data, fetch_ticket_price, send_price_alert, generate_ticket_comparison_report
import csv


class TestEventScraping(unittest.TestCase):
    """ This will test the fetch_event_data scraping function from Ticket_Price_Tracker"""

    @patch('builtins.input', return_value='nfl')  # Mocking user input which in this case its nfl 
    @patch('selenium.webdriver.Chrome')  # Mocking the WebDriver
    @patch('bs4.BeautifulSoup')  # Mocking BeautifulSoup
    @patch('csv.DictWriter')  # Mocking CSV writing
    def test_fetch_event_data(self, mock_csv_writer, mock_beautifulsoup, mock_webdriver, mock_input):
        """ Test method for fetching event data from a webpage. It will test the details of the webscape such as name, location, date, and ticket source. 
            It will mock selenium webDriver and BeautifulSoup 
        """
        # Mock the driver 
        mock_driver = MagicMock() # mocking the driver using MagicMock object
        mock_webdriver.return_value = mock_driver # Return the mock driver when webdriver is activated
         # The following a page source that you would expect when the webdriver scraps the website
        mock_driver.page_source = '<html><body><div class="sc-1mafo1b-4 dvCFno">Event 1</div><div class="sc-ja5jff-4">Location A</div><div class="sc-1pilhev-2 dBFhOm">2024-12-12</div><a class="sc-1x2zy2i-2 cYRIRc" href="/event/123">Buy Tickets</a></body></html>'

        # Mock BeautifulSoup
        mock_parse_html = MagicMock() # Mocking beautifulSoup by creating a object 
        mock_beautifulsoup.return_value = mock_parse_html # This will use the beautifulsoup mocked results when its being activated 
        mock_parse_html.find_all.side_effect = [
            [MagicMock(get_text=MagicMock(return_value='Event 1'))],  # Event Name
            [MagicMock(get_text=MagicMock(return_value='Location A'))],  # Event Location (switched with date)
            [MagicMock(get_text=MagicMock(return_value='2024-12-12'))],  # Event Date (switched with location)
            [MagicMock(get='href', return_value='/event/123')]  # Ticket Link
        ]
         
        # Mock the CSV DictWriter
        mock_csv_instance = MagicMock() #create csv writer object 
        mock_csv_writer.return_value = mock_csv_instance # Return the mock instance when DictWriter is activated 
        
        # Call the function
        fetch_event_data()
        
        # Assertions
        mock_input.assert_called_once()  # Check if input was called for event type
        mock_webdriver.assert_called_once()  # Check if Chrome WebDriver was instantiated
        mock_csv_writer.assert_called_once()  # Check if DictWriter was called
        
        # Check if writeheader and writerow were called to write the correct data
        mock_csv_instance.writeheader.assert_called_once()
        
        # Ensure the correct data was written to the CSV (ticket id,name, location, date, and ticket)
        mock_csv_instance.writerow.assert_called_with({
            'event_id': 1, # Mock id 
            'event name': 'Event 1', # Mock name 
            'event location': 'Location A',  #Mock location 
            'event date': '2024-12-12',  #Mock date 
            'ticket ': '/event/123' # Mock ticket link 
        })


class TestTicketPriceScraping(unittest.TestCase):
    """ This will test the fetch_ticket_price function from Ticket_Price_Tracker """

    @patch('selenium.webdriver.Chrome')  # Mocking the WebDriver
    @patch('bs4.BeautifulSoup')  # Mocking BeautifulSoup
    @patch('csv.DictWriter')  # Mocking CSV writing
    def test_fetch_ticket_price(self, mock_csv_writer, mock_beautifulsoup, mock_webdriver):
        """ Test method for fetching ticket price from a webpage. It will test the details of the webscape such as id,name,section,row and price. 
            It will mock selenium webDriver and BeautifulSoup 
        """
        # Mock the driver and page source
        mock_driver = MagicMock() # Mocking the driver using MagicMock object
        mock_webdriver.return_value = mock_driver # Return the mock driver when webdriver is activated
        # The following a page source that you would expect when the webdriver scraps the website 
        mock_driver.page_source = '<html><body><div class="sc-hlalgf-0 sc-hlalgf-6 jfjuff jXdyTR">Section 104 </div><div class="sc-hlalgf-0 sc-hlalgf-1 jfjuff tOKfM">$150</div></body></html>'

        # Mock BeautifulSoup
        mock_parse_html = MagicMock() # mocking beautifulSoup by creating a object 
        mock_beautifulsoup.return_value = mock_parse_html # This will use the beautifulsoup mocked results when its being activated 
        mock_parse_html.find_all.side_effect = [
            [MagicMock(get_text=MagicMock(return_value='Section 104'))],  # Ticket Section it needs to get 
            [MagicMock(get_text=MagicMock(return_value='$150'))]  # Ticket Price it needs to get 
        ] # These are the expected find all return value of the test web page source 
        
        # Mock the CSV DictWriter
        mock_csv_instance = MagicMock()  #Create csv writer object 
        mock_csv_writer.return_value = mock_csv_instance # Return the mock instance when DictWriter is activated 
        
        # Mock reading from the 'data.csv' file
        mock_open = patch('builtins.open', unittest.mock.mock_open(read_data="event_id,event_name,event_location,event_date,ticket\n1,Event 1,Location A,2024-12-12,/event/123\n"))
        
        with mock_open:
            # Call the function to scrape ticket price 
            fetch_ticket_price()
        
        # Assertions
        mock_webdriver.assert_called_once()  # Check if Chrome WebDriver was instantiated
        mock_csv_writer.assert_called_once()  # Check if DictWriter was instantiated
        
       # Check if writeheader and writerow were called to write the correct data
        mock_csv_instance.writeheader.assert_called_once()
        
        # Ensure the correct data was written to the CSV (ticket id,name, section, row, and price)
        mock_csv_instance.writerow.assert_called_with({
            'ticket_id': 1, # Mock ticket id 
            'ticket_name': 'Event 1', # Mock ticket name 
            'ticket_section': 'Section 104',  # Mock ticket section
            'ticket_row': 'N/A',  # Mock ticket row 
            'ticket_price': '$150' # Mock ticket price 
        })

class TestDisplayEventDetails(unittest.TestCase):
    def test_display_event_details(self):
        # Mock data for event and tickets
        mock_event = {
            "event name": "Concert A",
            "event location": "City Arena",
            "event date": "2024-12-15",
            "ticket ": "https://example.com/concert-a-tickets"
        }
        mock_tickets = [
            {"ticket_section": "101", "ticket_row": "A", "ticket_price": "$100"},
            {"ticket_section": "102", "ticket_row": "B", "ticket_price": "$80"}
        ]
        
        # Instantiate TicketDisplay and call the method
        display = TicketDisplay(mock_event, mock_tickets)
        with patch('builtins.print') as mock_print:
            display.display_event_details()
        
        # Verify expected print statements
        mock_print.assert_any_call("\nEvent Details")
        mock_print.assert_any_call("Name: Concert A")
        mock_print.assert_any_call("Date: City Arena")
        mock_print.assert_any_call("Venue: 2024-12-15")
        mock_print.assert_any_call("Source: https://example.com/concert-a-tickets")
        mock_print.assert_any_call(" - Section: 101, Seat: A, Price: $100")
        mock_print.assert_any_call(" - Section: 102, Seat: B, Price: $80")


class TestGetUserSelection(unittest.TestCase):
    @patch('builtins.input', side_effect=["1"])
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data="event_id,event_name,event_location,event_date,ticket\n1,Concert A,City Arena,2024-12-15,https://example.com/concert-a-tickets\n")
    def test_get_user_selection(self, mock_open, mock_input):
        # Mock ticket info
        ticket_data = "ticket_id,ticket_name,ticket_section,ticket_row,ticket_price\n1,Concert A,101,A,$100\n2,Concert A,102,B,$80\n"
        with patch('builtins.open', unittest.mock.mock_open(read_data=ticket_data), create=True):
            user_event, available_tickets, selection = get_user_selection()
        
        # Validate output
        self.assertEqual(user_event["event name"], "Concert A")
        self.assertEqual(len(available_tickets), 2)
        self.assertEqual(selection, 1)


class SendPriceAlert(unittest.TestCase):
    available_tickets = [
        {
        "ticket_name": "NFL game",
        "ticket_section": "100",
        "ticket_row": "10",
        "ticket_price": "$56"
        } 
    ]
    user_ticket = 0

    # Tests what happens if a valid email is never entered
    @patch('builtins.input', return_value = 'nonsense_email')
    def test_invalid_email(self, mock_input):
        result = send_price_alert(SendPriceAlert.available_tickets, SendPriceAlert.user_ticket)
        self.assertEqual(result, 'Too many invalid emails entered.')

    # Tests if a few inputs are invalid, but then a valid email is entered
    @patch('builtins.input', side_effect = ['not_an_email', 'also_not_an_email', 'finalproject326@gmail.com'])
    def test_invaild_then_valid(self, mock_input):
        result = send_price_alert(SendPriceAlert.available_tickets, SendPriceAlert.user_ticket)
        self.assertEqual(result, 'Email sent.')
        
    # Tests if a valid email is entered from the start
    @patch('builtins.input', return_value = 'finalproject326@gmail.com')
    def test_valid(self, mock_input):
        result = send_price_alert(SendPriceAlert.available_tickets, SendPriceAlert.user_ticket)
        self.assertEqual(result, 'Email sent.')
        
class TestGenerateTicketComparisonReport(unittest.TestCase):
    @patch('builtins.input', side_effect = ['low to high', 1])
    def test_valid_inputs_low_to_high(self, mock_input):
        tickets = [
            {"ticket_id": 1, "ticket_price": "$50", "event": "Concert A"},
            {"ticket_id": 2, "ticket_price": "$30", "event": "Concert B"},
            {"ticket_id": 3, "ticket_price": "$70", "event": "Concert C"},
        ]
        result = generate_ticket_comparison_report(tickets)
        self.assertEqual(result, 1)
       
    # test intended to fail because of invalid input 
    @patch('builtins.input', side_effect = ['low to high', 50])
    def test_invalid_inputs_low_to_high(self, mock_input):
        tickets = [
            {"ticket_id": 1, "ticket_price": "$50", "event": "Concert A"},
            {"ticket_id": 2, "ticket_price": "$30", "event": "Concert B"},
            {"ticket_id": 3, "ticket_price": "$70", "event": "Concert C"},
        ]
        result = generate_ticket_comparison_report(tickets)
        self.assertEqual(result, "Invalid number. Please enter a valid number.\n")

if __name__ == '__main__':
    unittest.main()
