import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth import default
import requests
from datetime import datetime, timezone
import schedule
import time
from os import getenv
from dotenv import load_dotenv


load_dotenv('src/.env')
print("Quota project from ENV:", getenv("GOOGLE_CLOUD_QUOTA_PROJECT"))

"""Authentication with Google Sheets"""
# Define scope & authorize
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds, _ = default(scopes=scope)

# Refresh creds if expired
if creds.expired and creds.refresh_token:
    creds.refresh(Request())

print("Effective scopes:", creds.scopes)

client = gspread.authorize(creds)

# Open your sheet
sheet = client.open("FiverrDemo").sheet1

# Header row
if sheet.row_count == 0 or not sheet.row_values(1):
    sheet.insert_row(["Timestamp", "BTC", "ETH", "SOL", "DOGE", "ADA"], index=1)




"""Prices from CoinGecko"""
def get_prices():
    ids = "bitcoin,ethereum,solana,dogecoin,cardano"
    url = (
        f"https://api.coingecko.com/api/v3/simple/price"
        f"?ids={ids}&vs_currencies=usd"
    )
    resp = requests.get(url)
    data = resp.json()
    return {
        "BTC": data["bitcoin"]["usd"],
        "ETH": data["ethereum"]["usd"],
        "SOL": data["solana"]["usd"],
        "DOGE": data["dogecoin"]["usd"],
        "ADA": data["cardano"]["usd"],
    }


"""Append to Sheet with Timestamp"""
def log_to_sheet(sheet, prices):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    row = [
        timestamp,
        f'${prices["BTC"]}',
        f'${prices["ETH"]}',
        f'${prices["SOL"]}',
        f'${prices["DOGE"]}',
        f'${prices["ADA"]}',
    ]
    sheet.append_row(row)
    print(f"Logged at {timestamp}:", row)



"""Orchestrate & Schedule"""
def job():
    prices = get_prices()
    log_to_sheet(sheet, prices)

# Schedule the job every hour
schedule.every().hour.at(":00").do(job)

if __name__ == "__main__":
    print("---\nStarting Crypto Price Tracker…\n")
    job()  # run once at start
    while True:
        schedule.run_pending()
        time.sleep(1)