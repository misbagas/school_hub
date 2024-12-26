import requests
from bs4 import BeautifulSoup

# URL where the CSRF token can be found
url = 'http://127.0.0.1:5000/save_class_code'

# Start a session to persist cookies (CSRF token might be in cookies)
session = requests.Session()

# Send a GET request to fetch the page
response = session.get(url)

# Use BeautifulSoup to parse the HTML and extract the CSRF token (if it's in a hidden form field)
soup = BeautifulSoup(response.text, 'html.parser')
csrf_token = soup.find('input', {'name': 'csrf_token'})['value']

print("CSRF Token:", csrf_token)
