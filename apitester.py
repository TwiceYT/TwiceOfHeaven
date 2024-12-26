import requests
from dotenv import load_dotenv
import os

#Load env file
load_dotenv(dotenv_path='config\config.env')

#Load custom Prefix
genius = os.getenv("GENIUSTOKEN")
token = genius
headers = {
    "Authorization": f"Bearer {token}"
}
query = "Vampire"
response = requests.get(f"https://api.genius.com/search?q={query}", headers=headers)

print(response.status_code)  # Should return 200
print(response.json())  # Check the response
