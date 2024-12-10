from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
from email import message_from_bytes, message_from_string
from datetime import datetime, timedelta
import os
from bs4 import BeautifulSoup
import requests
import zipfile
import os
import pandas as pd
from io import BytesIO
from simpledbf import Dbf5
import pyzipper 
from setup import log


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    log.info("Authenticating with google ... ")
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=50810)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def search_emails(service, sender_email, start_date, end_date):
    log.info(f"Searching for emails with sender = {sender_email}, between {start_date} and {end_date}")
    start_date = start_date.isoformat() + "Z"
    end_date = end_date.isoformat() + "Z"
    
    query = f'from:{sender_email} after:{start_date[:10]} before:{end_date[:10]}'

    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    return messages

def get_email_content(service, message_id):
    message = service.users().messages().get(userId='me', id=message_id, format='raw').execute()
    msg_str = base64.urlsafe_b64decode(message['raw']).decode('utf-8')
    mime_msg = message_from_string(msg_str)

    subject = mime_msg['Subject']
    from_email = mime_msg['From']
    body = None

    if mime_msg.is_multipart():
        for part in mime_msg.walk():
            if part.get_content_type() == 'text/html':
                body = part.get_payload(decode=True).decode('utf-8')
    else:
        body = mime_msg.get_payload(decode=True).decode('utf-8')

    return {
        "subject": subject,
        "from": from_email,
        "body": body,
    }

def process_zip_file(url, password):
    try:
        log.info(f"Downloading Zip file. URL = {url}")
        response = requests.get(url)
        response.raise_for_status()
        zip_file = BytesIO(response.content)
        with pyzipper.AESZipFile(zip_file, 'r') as z:
            log.info(f"Extracting file from zip ...")
            password_bytes = password.encode('utf-8')
            z.extractall("extracted_files", pwd=password_bytes)
            extracted_files = z.namelist()
        dbf_file = next((file for file in extracted_files if file.endswith('.dbf')), None)
        if not dbf_file:
            raise FileNotFoundError("No DBF file found in the zip archive.")
        
        dbf_path = os.path.join("extracted_files", dbf_file)
        dbf = Dbf5(dbf_path)
        df = dbf.to_dataframe()
        df = df.astype(str).where(df.notnull(), None)
        log.info("Successfully parsed the DBF file.")
        return df

    except requests.exceptions.RequestException as e:
        log.error(f"Error downloading the zip file: {e}")
    except zipfile.BadZipFile as e:
        log.error(f"Error extracting the zip file: {e}")
    except Exception as e:
        log.error(f"An unexpected error occurred: {e}")

def process_cams_data(soup: BeautifulSoup):
    url = soup.find_all('td')[3].a['href']
    report_no = soup.find_all('td')[8].find_all('td')[1].get_text(strip=True)
    if report_no == "WBR2":
        df = process_zip_file(url, password='123456')
        # df.to_sql('transactions', con=engine, if_exists='append', index=False)
    elif report_no == "WBR9":
        df = process_zip_file(url, password='123456')
        # df.to_sql('transactions', con=engine, if_exists='append', index=False)
    return df

def process_karvy_data(soup: BeautifulSoup):
    url = soup.find('a', string=lambda text: text and "Click Here" in text).get('href')
    df = process_zip_file(url, password='kfin123456')
    return df

def task():
    service = authenticate_gmail()
    end_date = (datetime.now() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = end_date - timedelta(days=1)
    sender_emails = ['donotreply@camsonline.com', 'distributorcare@kfintech.com']
    for i, sender_email in enumerate(sender_emails):
        messages = search_emails(service, sender_email, start_date, end_date)
        for msg in messages:
            email_content = get_email_content(service, msg['id'])
            log.info(f"Found: {email_content['subject']}")
            body = email_content['body']
            soup = BeautifulSoup(body, 'html.parser')
            if i == 0:
                process_cams_data(soup)
            elif i == 1:
                process_karvy_data(soup)

task()