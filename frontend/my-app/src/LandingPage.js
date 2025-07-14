import React, { useRef } from "react";
import { useNavigate } from "react-router-dom";
import "./landing.css";
import logo from "./Screenshot_2025-07-12_at_6.33.52_PM-removebg-preview.png";

export default function LandingPage() {
  const navigate = useNavigate();
  const howToRef = useRef(null);

  return (
    <div className="landing-root">
      <header className="landing-header">
        <div className="logo-area">
          <img src={logo} alt="Qron Logo" className="logo-img" />
          <span className="logo-title">Qron</span>
        </div>
        <div className="landing-subtitle">
          Send Emails to 1000+ Recruiters with just one click
        </div>
        <div className="landing-btn-row">
          <button
            className="landing-btn primary"
            onClick={() => navigate("/app")}
          >
            Start an Email
          </button>
          <button
            className="landing-btn secondary"
            onClick={() => howToRef.current.scrollIntoView({ behavior: "smooth" })}
          >
            How it Works?
          </button>
        </div>
      </header>

      <main className="landing-main">
        <section className="about-section">
          <div className="about-content">
            <div className="about-text">
              <h2>About QRON</h2>
              <p>
                Qron was created to solve a real challenge faced by placement and internship coordinators: sending personalized emails to large lists of recruiters or contacts, quickly and efficiently.
              </p>
              <p>
                Instead of spending hours manually composing and sending messages, Qron empowers coordinators with a streamlined, intuitive platform. Simply upload your recruiter or contact list—whether in CSV or Excel format—add optional attachments, specify columns for personalization, and craft your message using dynamic placeholders.
              </p>
              <p>
                With just one click, Qron automatically generates and sends individualized emails to every recipient, merging in company names, HR names, or any custom details you need. Attachments, flexible templates, and error-free delivery ensure your communication is professional and consistent every time.
              </p>
              <p>
                No more tedious manual work or repetitive tasks—Qron makes bulk emailing fast, smart, and secure, so you can focus on building relationships and driving results, not on operations.
              </p>
            </div>
          </div>
        </section>

        <section className="howto-section" ref={howToRef}>
          <h2>How to Send Emails to Recruiters with Qron?</h2>
          <ol>
            <li>
              <span className="howto-highlight">Prepare Your Contact File:</span>
              Upload a CSV or Excel file with columns like email, company, hr_name, or any custom fields you want to use.
            </li>
            <li>
              <span className="howto-highlight">Use Correct Column Names:</span>
              Enter the exact column names for email presented in the file and any personalization fields you plan to use.
            </li>
            <li>
              <span className="howto-highlight">Write Your Message:</span>
              Compose your subject and message body. Use curly braces like <code>{'{hr_name}'}</code> and <code>{'{company}'}</code> to personalize each email.
            </li>
            <li>
              <span className="howto-highlight">Attach Any Files (Optional):</span>
              You can include any PDF, image, or document you want to send along with the email.
            </li>
            <li>
              <span className="howto-highlight">Enter Sender Email &amp; Password:</span>
              Provide the sender Gmail address. Generate an <a href="https://myaccount.google.com/apppasswords" target="_blank" rel="noopener noreferrer">App Password</a> from Google and paste it—both must belong to the same Gmail account.
            </li>
            <li>
              <span className="howto-highlight">Review &amp; Submit:</span>
              Double-check your inputs, remove any incorrect files if needed, and click Submit. Qron sends all emails individually within seconds.
            </li>
          </ol>
          <button
            className="landing-btn primary"
            style={{ marginTop: 24 }}
            onClick={() => navigate("/app")}
          >
            Start an Email
          </button>
        </section>
      </main>
    </div>
  );
}
