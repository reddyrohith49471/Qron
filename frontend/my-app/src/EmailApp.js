import React, { useState } from 'react';
import './App.css';
import logo from "./Screenshot_2025-07-12_at_6.33.52_PM-removebg-preview.png";

function EmailApp() {
  const [dataFile, setDataFile] = useState(null);
  const [attachments, setAttachments] = useState([]);
  const [emailColumn, setEmailColumn] = useState('');
  const [companyColumn, setCompanyColumn] = useState('');
  const [hrColumn, setHrColumn] = useState('');
  const [customColumns, setCustomColumns] = useState('');
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [yourEmail, setYourEmail] = useState('');
  const [yourPassword, setYourPassword] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleDataFileChange = (e) => {
    if (e.target.files.length > 0) {
      setDataFile(e.target.files[0]);
    }
  };

  const removeDataFile = () => {
    setDataFile(null);
  };

  const handleAttachmentsChange = (e) => {
    if (e.target.files.length > 0) {
      setAttachments(prev => [...prev, ...Array.from(e.target.files)]);
    }
  };

  const removeAttachment = (index) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!dataFile) {
      setMessage('Please upload a data file.');
      return;
    }
    setLoading(true);
    setMessage('');

    const formData = new FormData();
    formData.append('data_file', dataFile);
    attachments.forEach(file => formData.append('attachments', file));
    formData.append('email_column', emailColumn);
    formData.append('company_column', companyColumn);
    formData.append('hr_column', hrColumn);
    formData.append('custom_columns', customColumns);
    formData.append('subject', subject);
    formData.append('body', body);
    formData.append('your_email', yourEmail);
    formData.append('your_password', yourPassword);

    try {
      const response = await fetch('https://qron.onrender.com/send_emails', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      setMessage(data.message || data.error);
    } catch (err) {
      setMessage('An error occurred while sending emails.');
    }
    setLoading(false);
  };

  return (
    <div>
      <div className="logo-area1">
        <img src={logo} alt="Qron Logo" className="logo-img1" />
        <span className="logo-title1">Qron</span>
      </div>
      <div className="container">
        <form className="email-form" onSubmit={handleSubmit}>
          <label>Upload File (CSV or Excel) *</label>
          {!dataFile ? (
            <input
              type="file"
              accept=".csv,.xls,.xlsx"
              onChange={handleDataFileChange}
              required
            />
          ) : (
            <div className="file-selected">
              <span>{dataFile.name}</span>
              <button type="button" className="remove-btn" onClick={removeDataFile}>Remove</button>
            </div>
          )}

          <label>Enter Emails Column Name *</label>
          <input type="text" value={emailColumn} onChange={e => setEmailColumn(e.target.value)} required />

          <label>Company Column Name (optional)</label>
          <input type="text" value={companyColumn} onChange={e => setCompanyColumn(e.target.value)} />

          <label>HR Column Name (optional)</label>
          <input type="text" value={hrColumn} onChange={e => setHrColumn(e.target.value)} />

          <label>
            Any other columns? (comma separated, optional)
            <span className="hint"> (Reference in subject/body as {'{column_name}'})</span>
          </label>
          <input
            type="text"
            value={customColumns}
            onChange={e => setCustomColumns(e.target.value)}
            placeholder="e.g. location, date, manager"
          />

          <label>Enter Subject for your emails *</label>
          <input
            type="text"
            value={subject}
            onChange={e => setSubject(e.target.value)}
            required
            className="subject-input"
          />

          <label>Enter body for your emails *</label>
          <textarea
            value={body}
            onChange={e => setBody(e.target.value)}
            required
            className="body-textarea"
            rows={8}
            placeholder="Write your email body here. Use {company}, {hr_name}, or any column name in curly braces."
          />

          <label>Attach files (optional)</label>
          <input
            type="file"
            multiple
            onChange={handleAttachmentsChange}
            accept="*"
          />
          {attachments.length > 0 && (
            <div className="attachments-list">
              {attachments.map((file, index) => (
                <div key={index} className="file-selected">
                  <span>{file.name}</span>
                  <button type="button" className="remove-btn" onClick={() => removeAttachment(index)}>Remove</button>
                </div>
              ))}
            </div>
          )}

          <label>Enter Your Email *</label>
          <input type="email" value={yourEmail} onChange={e => setYourEmail(e.target.value)} required />

          <label>Enter Your Password *</label>
          <input type="password" value={yourPassword} onChange={e => setYourPassword(e.target.value)} required />

          <button type="submit" disabled={loading}>{loading ? 'Sending...' : 'Submit'}</button>
          {message && <div className="message">{message}</div>}
        </form>
      </div>
    </div>
  );
}

export default EmailApp;
