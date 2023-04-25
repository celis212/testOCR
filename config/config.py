# Description: This file contains the configuration variables for the veryfi API
import os
from dotenv import load_dotenv

load_dotenv()  

# Get the variables
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
CLIENT_ID = os.getenv("CLIENT_ID")
API_KEY = os.getenv("API_KEY")