from flask import Flask, request, jsonify
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from flask_cors import CORS
import traceback
import threading

app = Flask(__name__)
CORS(app)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_secret_key_here')
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['csv', 'xls', 'xlsx']


@app.route('/send_emails', methods=['POST'])
def send_emails():
    if 'data_file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['data_file']
    attachments = request.files.getlist('attachments')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Please upload a valid CSV or Excel file.'}), 400

    email_column = request.form['email_column'].strip().lower()
    company_column = request.form.get('company_column', '').strip().lower()
    hr_column = request.form.get('hr_column', '').strip().lower()
    custom_columns_raw = request.form.get('custom_columns', '').strip()
    subject_template = request.form['subject']
    body_template = request.form['body']
    your_email = request.form['your_email']
    your_password = request.form['your_password']

    custom_columns = [col.strip().lower() for col in custom_columns_raw.split(',') if col.strip()] if custom_columns_raw else []

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    attachment_paths = []
    for attach_file in attachments:
        if attach_file and attach_file.filename:
            attach_path = os.path.join(UPLOAD_FOLDER, attach_file.filename)
            attach_file.save(attach_path)
            attachment_paths.append(attach_path)

    # ✅ Launch background thread
    threading.Thread(target=process_email_sending, args=(
        filepath, attachment_paths, email_column, company_column, hr_column,
        custom_columns, subject_template, body_template, your_email, your_password
    )).start()

    return jsonify({'message': 'Emails are being sent in the background! You can continue using the app.'}), 200


def process_email_sending(
    filepath, attachment_paths, email_column, company_column, hr_column,
    custom_columns, subject_template, body_template, your_email, your_password
):
    try:
        ext = filepath.rsplit('.', 1)[1].lower()
        df = pd.read_csv(filepath) if ext == 'csv' else pd.read_excel(filepath)
        df.columns = [col.lower().strip() for col in df.columns]

        required_columns = [email_column]
        for col in [company_column, hr_column] + custom_columns:
            if col:
                required_columns.append(col)
        missing = [col for col in required_columns if col and col not in df.columns]
        if missing:
            print(f"[ERROR] Missing columns: {', '.join(missing)}")
            return

        df = df.dropna(subset=[email_column])

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(your_email, your_password)

        emails_sent_count = 0
        for _, row in df.iterrows():
            email = row[email_column]
            if not email:
                continue

            variables = {}
            if company_column in df.columns:
                variables['company'] = str(row[company_column]) if pd.notna(row[company_column]) else ''
            if hr_column in df.columns:
                variables['hr_name'] = str(row[hr_column]) if pd.notna(row[hr_column]) else ''
            for col in custom_columns:
                if col in df.columns:
                    variables[col] = str(row[col]) if pd.notna(row[col]) else ''

            # Add all columns
            for col in df.columns:
                variables[col] = str(row[col]) if pd.notna(row[col]) else ''

            try:
                subject = subject_template.format(**variables)
                body = body_template.format(**variables)
            except KeyError as e:
                print(f"[ERROR] Template key error: {e}")
                continue

            msg = MIMEMultipart()
            msg['From'] = your_email
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            for path in attachment_paths:
                try:
                    with open(path, 'rb') as f:
                        part = MIMEApplication(f.read(), Name=os.path.basename(path))
                        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(path)}"'
                        msg.attach(part)
                except Exception as e:
                    print(f"[ERROR] Failed to attach file: {path}, Error: {e}")
                    continue

            try:
                server.sendmail(your_email, email, msg.as_string())
                emails_sent_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to send email to {email}, Error: {e}")
                continue

        server.quit()
        print(f"[SUCCESS] Emails sent: {emails_sent_count}")

    except Exception as e:
        print("[UNEXPECTED ERROR]", traceback.format_exc())
    finally:
        # Clean up uploaded files
        for path in [filepath] + attachment_paths:
            if os.path.exists(path):
                os.remove(path)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
