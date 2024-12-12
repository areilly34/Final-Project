import unittest
from unittest.mock import patch, MagicMock
from Ticket_Price_Tracker import fetch_event_data, fetch_ticket_price
import csv


class TestEventScraping(unittest.TestCase):

    @patch('builtins.input', return_value='nfl')  # Mocking user input
    @patch('selenium.webdriver.Chrome')  # Mocking the WebDriver
    @patch('bs4.BeautifulSoup')  # Mocking BeautifulSoup
    @patch('csv.DictWriter')  # Mocking CSV writing
    def test_fetch_event_data(self, mock_csv_writer, mock_beautifulsoup, mock_webdriver, mock_input):
        # Mock the driver and page source with changed order of date and location
        mock_driver = MagicMock()
        mock_webdriver.return_value = mock_driver
        mock_driver.page_source = '<html><body><div class="sc-1mafo1b-4 dvCFno">Event 1</div><div class="sc-ja5jff-4">Location A</div><div class="sc-1pilhev-2 dBFhOm">2024-12-12</div><a class="sc-1x2zy2i-2 cYRIRc" href="/event/123">Buy Tickets</a></body></html>'

        # Mock BeautifulSoup
        mock_parse_html = MagicMock()
        mock_beautifulsoup.return_value = mock_parse_html
        mock_parse_html.find_all.side_effect = [
            [MagicMock(get_text=MagicMock(return_value='Event 1'))],  # Event Name
            [MagicMock(get_text=MagicMock(return_value='Location A'))],  # Event Location (switched with date)
            [MagicMock(get_text=MagicMock(return_value='2024-12-12'))],  # Event Date (switched with location)
            [MagicMock(get='href', return_value='/event/123')]  # Ticket Link
        ]
        
        # Mock the CSV DictWriter
        mock_csv_instance = MagicMock()
        mock_csv_writer.return_value = mock_csv_instance
        
        # Call the function
        fetch_event_data()
        
        # Assertions
        mock_input.assert_called_once()  # Check if input was called for event type
        mock_webdriver.assert_called_once()  # Check if Chrome WebDriver was instantiated
        mock_csv_writer.assert_called_once()  # Check if DictWriter was called
        
        # Check if writeheader and writerow were called to write the correct data
        mock_csv_instance.writeheader.assert_called_once()
        
        # Updated expected values based on function's behavior
        mock_csv_instance.writerow.assert_called_with({
            'event_id': 1,
            'event name': 'Event 1',
            'event location': 'Location A',  # Location comes before Date now
            'event date': '2024-12-12',  # Date comes after Location
            'ticket ': '/event/123'
        })


class TestTicketPriceScraping(unittest.TestCase):

    @patch('selenium.webdriver.Chrome')  # Mocking the WebDriver
    @patch('bs4.BeautifulSoup')  # Mocking BeautifulSoup
    @patch('csv.DictWriter')  # Mocking CSV writing
    def test_fetch_ticket_price(self, mock_csv_writer, mock_beautifulsoup, mock_webdriver):
        # Mock the driver and page source
        mock_driver = MagicMock()
        mock_webdriver.return_value = mock_driver
        mock_driver.page_source = '<html><body><div class="sc-hlalgf-0 sc-hlalgf-6 jfjuff jXdyTR">Section 104 </div><div class="sc-hlalgf-0 sc-hlalgf-1 jfjuff tOKfM">$150</div></body></html>'

        # Mock BeautifulSoup
        mock_parse_html = MagicMock()
        mock_beautifulsoup.return_value = mock_parse_html
        mock_parse_html.find_all.side_effect = [
            [MagicMock(get_text=MagicMock(return_value='Section 104'))],  # Ticket Section
            [MagicMock(get_text=MagicMock(return_value='$150'))]  # Ticket Price
        ]
        
        # Mock the CSV DictWriter
        mock_csv_instance = MagicMock()
        mock_csv_writer.return_value = mock_csv_instance
        
        # Mock reading from the 'data.csv' file
        mock_open = patch('builtins.open', unittest.mock.mock_open(read_data="event_id,event_name,event_location,event_date,ticket\n1,Event 1,Location A,2024-12-12,/event/123\n"))
        
        with mock_open:
            # Call the function
            fetch_ticket_price()
        
        # Assertions
        mock_webdriver.assert_called_once()  # Check if Chrome WebDriver was instantiated
        mock_csv_writer.assert_called_once()  # Check if DictWriter was called
        
        # Adjusted expected values based on your function's logic
        mock_csv_instance.writeheader.assert_called_once()
        
        # Updated to reflect the correct splitting of section and row
        mock_csv_instance.writerow.assert_called_with({
            'ticket_id': 1,
            'ticket_name': 'Event 1',
            'ticket_section': 'Section 104',  # Correct ticket_section
            'ticket_row': 'N/A',  # Correct ticket_row
            'ticket_price': '$150'
        })


if __name__ == '__main__':
    unittest.main()