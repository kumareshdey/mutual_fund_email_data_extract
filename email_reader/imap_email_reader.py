import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
import requests
import pandas as pd
from io import BytesIO
from simpledbf import Dbf5
import os
import pyzipper
from datetime import datetime, timedelta
from setup import log
from db_connection import engine
from credentials import IMAP_SERVER, EMAIL, PASSWORD, PORT
from models import CamsWBR2, CamsWBR9
from repository import GenericRepository

def authenticate_imap():
    log.info("Authenticating with Gmail IMAP...")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, PORT)
    mail.login(EMAIL, PASSWORD)
    return mail

def search_emails_imap(mail, sender_emails, start_date, end_date):
    log.info(f"Searching emails from {sender_emails} between {start_date} and {end_date}...")
    mail.select("inbox")
    
    # Format date for IMAP
    start_date = start_date.strftime('%d-%b-%Y')
    end_date = end_date.strftime('%d-%b-%Y')
    
    # Search emails by date range
    status, messages = mail.search(
        None,
        f'(SINCE "{start_date}" BEFORE "{end_date}")'
    )
    if status != "OK":
        log.error("Failed to fetch emails.")
        return []
    
    # Filter messages containing any of the sender emails
    message_ids = messages[0].split()
    matching_emails = []
    if not message_ids:
        log.info("No emails found.")
    for msg_id in message_ids:
        status, msg_data = mail.fetch(msg_id, '(RFC822)')
        if status != "OK":
            log.warning(f"Failed to fetch message {msg_id}.")
            continue
        
        # Extract the email content
        raw_email = msg_data[0][1]
        email_content = raw_email.decode(errors='ignore').lower()
        
        # Check if any sender email is in the content
        if any(sender_email.lower() in email_content for sender_email in sender_emails):
            matching_emails.append(msg_id)
    
    return matching_emails

def get_email_content_imap(mail, msg_id):
    status, data = mail.fetch(msg_id, "(RFC822)")
    if status != "OK":
        log.error(f"Failed to fetch email with ID {msg_id}.")
        return None

    raw_email = data[0][1]
    msg = email.message_from_bytes(raw_email)
    subject = decode_header(msg["Subject"])[0][0]
    if isinstance(subject, bytes):
        subject = subject.decode()
    from_email = msg.get("From")
    body = None

    # Get email content
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                body = part.get_payload(decode=True).decode('utf-8')
    else:
        body = msg.get_payload(decode=True).decode('utf-8')

    return {
        "subject": subject,
        "from": from_email,
        "body": body,
    }

def process_zip_file(url, password) -> pd.DataFrame:
    try:
        log.info(f"Downloading ZIP file. URL = {url}")
        response = requests.get(url, verify=False)
        response.raise_for_status()
        zip_file = BytesIO(response.content)
        
        with pyzipper.AESZipFile(zip_file, 'r') as z:
            log.info("Extracting files from ZIP...")
            password_bytes = password.encode('utf-8')
            z.extractall("extracted_files", pwd=password_bytes)
            extracted_files = z.namelist()
        
        dbf_file = next((file for file in extracted_files if file.endswith('.dbf')), None)
        if not dbf_file:
            raise FileNotFoundError("No DBF file found in the ZIP archive.")
        
        dbf_path = os.path.join("extracted_files", dbf_file)
        dbf = Dbf5(dbf_path)
        df = dbf.to_dataframe()
        df = df.astype(str).where(df.notnull(), None)
        log.info("Successfully parsed the DBF file.")
        return df

    except requests.exceptions.RequestException as e:
        log.error(f"Error downloading ZIP file: {e}")
    except pyzipper.BadZipFile as e:
        log.error(f"Error extracting ZIP file: {e}")
    except Exception as e:
        log.error(f"An unexpected error occurred: {e}")


def save_dataframe_to_db(df, model_class):
    """
    Save a DataFrame to a database table using the GenericRepository.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        model_class: The SQLAlchemy model class corresponding to the table.
        repository (GenericRepository): An instance of the GenericRepository.
    """
    
    repository = GenericRepository()
    if df.empty:
        log.warning("The DataFrame is empty. Nothing to save.")
        return

    try:
        # Convert DataFrame rows to a list of model instances
        records = [
            model_class(**row) for row in df.to_dict(orient="records")
        ]

        for record in records:
            repository.add_or_update(record)
        
        log.info(f"Successfully saved {len(records)} records to the {model_class.__tablename__} table.")

    except Exception as e:
        log.error(f"Error saving DataFrame to {model_class.__tablename__}: {e}")



def process_cams_data(soup: BeautifulSoup):
    url = soup.find_all('td')[3].a['href']
    report_no = soup.find_all('tr')[9].find_all('td')[1].get_text(strip=True)
    if report_no == "WBR2":
        df = process_zip_file(url, password='123456')
        column_names = [column.name for column in CamsWBR2.__table__.columns]
        df = df[column_names]
        log.info("Saving Cams WBR2 entries ...")
        save_dataframe_to_db(df = df, model_class=CamsWBR2)
        log.info("Saved Cams WBR2 entries ...")
    elif report_no == "WBR9":
        df = process_zip_file(url, password='123456')
        column_names = [column.name for column in CamsWBR9.__table__.columns]
        df = df[column_names]
        log.info("Saving Cams WBR9 entries ...")
        save_dataframe_to_db(df = df, model_class=CamsWBR9)
        log.info("Saved Cams WBR9 entries ...")
    return df

def process_karvy_data(soup: BeautifulSoup):
    url = soup.find('a', string=lambda text: text and "Click Here" in text).get('href')
    df = process_zip_file(url, password='kfin123456')
    return df


def task():
    mail = authenticate_imap()
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=74)
    sender_emails = ["donotreply@camsonline.com", "distributorcare@kfintech.com"]
    for i, sender_email in enumerate(sender_emails):
        messages = search_emails_imap(mail, sender_email, start_date, end_date)
        for msg_id in messages:
            email_content = get_email_content_imap(mail, msg_id)
            if not email_content:
                continue
            log.info(f"Processing email: {email_content['subject']}. Sent: {email_content['from']}.")
            body = email_content['body']
            soup = BeautifulSoup(body, 'html.parser')
            if i == 0:
                process_cams_data(soup)
            elif i == 1:
                process_karvy_data(soup)
    
    mail.logout()

if __name__ == "__main__":
    task()
