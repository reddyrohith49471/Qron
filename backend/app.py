# app.py
from flask import Flask, request, jsonify
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from flask_cors import CORS
import traceback
import zipfile
from io import BytesIO
import threading
from drive_utils import upload_to_drive

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_secret_key_here')
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

MAX_DATA_FILE_SIZE_MB = 5
MAX_ATTACHMENT_SIZE_MB = 5
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "your-folder-id-here")
GOOGLE_DRIVE_CREDENTIALS = os.getenv("GOOGLE_DRIVE_CREDENTIALS", "credentials.json")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['csv', 'xls', 'xlsx']

def compress_attachments(attachments):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for attach_file in attachments:
            content = attach_file.read()
            if len(content) > MAX_ATTACHMENT_SIZE_MB * 1024 * 1024:
                return None, f"{attach_file.filename} exceeds {MAX_ATTACHMENT_SIZE_MB}MB limit."
            zipf.writestr(attach_file.filename, content)
            attach_file.seek(0)
    buffer.seek(0)
    drive_link = upload_to_drive(buffer, "attachments.zip", GOOGLE_DRIVE_FOLDER_ID, GOOGLE_DRIVE_CREDENTIALS)
    buffer.seek(0)
    return buffer, drive_link

def process_and_send_emails(params):
    filepath, attachments, form = params

    try:
        ext = filepath.rsplit('.', 1)[1].lower()
        df = pd.read_csv(filepath) if ext == 'csv' else pd.read_excel(filepath)
        df.columns = [col.lower().strip() for col in df.columns]

        email_column = form['email_column']
        required_columns = [email_column] + [c for c in [form['company_column'], form['hr_column']] + form['custom_columns'] if c]
        missing = [col for col in required_columns if col not in df.columns]

        if missing:
            raise ValueError(f"Missing columns: {', '.join(missing)}")

        df = df.dropna(subset=[email_column])

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(form['your_email'], form['your_password'])

        zip_buffer, drive_link = compress_attachments(attachments)
        if isinstance(drive_link, str) and drive_link.startswith("Google Drive upload failed"):
            raise ValueError(drive_link)

        emails_sent_count = 0
        for _, row in df.iterrows():
            variables = {col: str(row[col]) if pd.notna(row[col]) else '' for col in df.columns}
            try:
                subject = form['subject'].format(**variables)
                body = form['body'].format(**variables)
                body += f"\n\nDownload attachments from Google Drive: {drive_link}"
            except KeyError as e:
                raise ValueError(f"Template variable missing: {e}")

            msg = MIMEMultipart()
            msg['From'] = form['your_email']
            msg['To'] = row[email_column]
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            try:
                server.sendmail(form['your_email'], row[email_column], msg.as_string())
                emails_sent_count += 1
            except Exception:
                continue

        server.quit()
        os.remove(filepath)
        return f"Emails sent successfully to {emails_sent_count} recipients!"

    except Exception as e:
        traceback.print_exc()
        return f"Error: {e}"

@app.route('/send_emails', methods=['POST'])
def send_emails():
    try:
        if 'data_file' not in request.files:
            return jsonify({'error': 'No data file provided'}), 400

        data_file = request.files['data_file']
        attachments = request.files.getlist('attachments')

        if not allowed_file(data_file.filename):
            return jsonify({'error': 'Invalid file format'}), 400

        data_file.seek(0, os.SEEK_END)
        if data_file.tell() > MAX_DATA_FILE_SIZE_MB * 1024 * 1024:
            return jsonify({'error': 'Data file too large'}), 400
        data_file.seek(0)

        filepath = os.path.join(UPLOAD_FOLDER, data_file.filename)
        data_file.save(filepath)

        form = {
            'email_column': request.form['email_column'].strip().lower(),
            'company_column': request.form.get('company_column', '').strip().lower(),
            'hr_column': request.form.get('hr_column', '').strip().lower(),
            'custom_columns': [c.strip().lower() for c in request.form.get('custom_columns', '').split(',') if c],
            'subject': request.form['subject'],
            'body': request.form['body'],
            'your_email': request.form['your_email'],
            'your_password': request.form['your_password']
        }

        thread = threading.Thread(target=process_and_send_emails, args=((filepath, attachments, form),))
        thread.start()

        return jsonify({'message': 'Emails are being processed in the background.'}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Unexpected error: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
