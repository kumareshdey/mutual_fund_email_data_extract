# Mutual Fund Data Extractor

This project provides an automated solution for extracting, processing, and serving mutual fund transaction data from two of India's largest registrars and transfer agents: CAMS and Karvy (KFintech). The system is designed to streamline the workflow for financial advisors, analysts, or back-office teams who need to aggregate and analyze mutual fund transaction data for their clients.

**How it works:**

1. **Automated Email Retrieval:**  
   The system connects to a Gmail account using either IMAP (username/password) or the Gmail API (OAuth). It searches for transaction report emails sent by CAMS and Karvy within a configurable date range.

2. **Attachment Extraction:**  
   These emails typically contain password-protected ZIP files as attachments. The system automatically downloads these ZIP files and extracts their contents using the appropriate password for each provider.

3. **DBF File Parsing:**  
   Inside the ZIP files are DBF (dBase) files containing detailed transaction or holding data. The system parses these DBF files and converts them into pandas DataFrames for further processing.

4. **Database Ingestion:**  
   The parsed data is mapped to SQLAlchemy ORM models and inserted into a PostgreSQL database. The schema supports both CAMS (WBR2, WBR9) and Karvy data formats, ensuring compatibility and referential integrity.

5. **REST API for Data Access:**  
   A FastAPI server exposes an endpoint that allows users to query mutual fund data by PAN number. This enables easy integration with dashboards, reporting tools, or other applications.

6. **Logging and Error Handling:**  
   All major operations are logged for traceability. The system is designed to handle errors gracefully, ensuring that issues with one email or file do not halt the entire process.

This end-to-end pipeline eliminates manual intervention in downloading, extracting, and loading mutual fund data, making it easier to keep your database up-to-date and accessible for analytics or compliance purposes.

## Features

- Reads emails from Gmail (IMAP or Gmail API supported)
- Downloads and extracts password-protected ZIP attachments
- Parses DBF files and loads data into PostgreSQL using SQLAlchemy ORM
- Supports CAMS (WBR2, WBR9) and Karvy reports
- FastAPI endpoint for querying user data by PAN number
- Logging for all major operations

## Folder Structure

- `api.py` - FastAPI server for user data queries
- `email_reader_task.py` - Gmail API-based email reader (OAuth)
- `imap_email_reader.py` - IMAP-based email reader (username/password)
- `models.py` - SQLAlchemy ORM models
- `repository.py` - Generic repository for DB operations
- `mapper.py` - Column mapping for DBF to user-friendly names
- `setup.py` - Logging configuration
- `migrations.py` - Database and schema management
- `requirements.txt` - Python dependencies

## Setup

1. **Clone the repository** and navigate to this folder.

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure credentials:**
   - Create a `credentials.py` file with your database and email credentials (see `.gitignore` for excluded files).
   - For Gmail API, download `credentials.json` from Google Cloud Console and place it in this folder.

4. **Database setup:**
   - Edit `DB_PORT` and other DB settings in `credentials.py`.
   - Run migrations to create the database and tables:
     ```bash
     python migrations.py
     ```

5. **Run the email reader:**
   - For IMAP (username/password):
     ```bash
     python imap_email_reader.py
     ```
   - For Gmail API (OAuth):
     ```bash
     python email_reader_task.py
     ```

6. **Start the API server:**
   ```bash
   python api.py
   ```
   - Access the endpoint at: `http://127.0.0.1:8000/user_data?pan_no=YOUR_PAN_NO`

## Notes

- Ensure your database is running and accessible.
- The `.dbf` files and extracted files are ignored by `.gitignore`.
- Logging output is written to `logs.log`.

## License

This project is for demonstration and internal use only.
