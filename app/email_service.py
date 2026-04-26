"""
LGU MUN 2026 — Email Notification Service
Uses Gmail SMTP for sending emails
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

# Email configuration from environment
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")  # Your Gmail address
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # App password (not regular password)
FROM_NAME = os.getenv("FROM_NAME", "LGU MUN Society")

# Event details from settings
EVENT_VENUE = "Lahore Garrison University"
EVENT_DATES = "May 15-17, 2026"


class EmailService:
    def __init__(self):
        self.smtp_host = SMTP_HOST
        self.smtp_port = SMTP_PORT
        self.smtp_user = SMTP_USER
        self.smtp_password = SMTP_PASSWORD
        self.from_name = FROM_NAME

    def is_configured(self) -> bool:
        """Check if SMTP is properly configured"""
        return bool(self.smtp_user and self.smtp_password)

    def send_email(self, to_email: str, subject: str, html_body: str, plain_body: str = "") -> bool:
        """
        Send an email via Gmail SMTP

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML content
            plain_body: Plain text fallback

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.is_configured():
            logger.warning(f"Email not sent: SMTP not configured. To: {to_email}, Subject: {subject}")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.from_name} <{self.smtp_user}>"
            msg["To"] = to_email

            # Add plain text version
            if plain_body:
                msg.attach(MIMEText(plain_body, "plain"))

            # Add HTML version
            msg.attach(MIMEText(html_body, "html"))

            # Connect and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()  # Secure connection
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def send_registration_confirmation(
        self,
        to_email: str,
        delegate_name: str,
        roll_number: str,
        committee_name: str,
        committee_short: str
    ) -> bool:
        """
        Send registration confirmation email (Email 1)
        Fires immediately on successful registration
        """
        subject = f"LGU MUN 2026 — Registration Confirmed ✓"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 30px; text-align: center; color: #fff; }}
                .header h1 {{ margin: 0; font-size: 28px; color: #d4a843; }}
                .header p {{ margin: 10px 0 0; opacity: 0.8; }}
                .content {{ padding: 30px; }}
                .roll-box {{ background: #f8f9fa; border: 2px dashed #d4a843; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0; }}
                .roll-number {{ font-size: 32px; font-weight: bold; color: #1a1a2e; margin: 0; letter-spacing: 2px; }}
                .details {{ background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 20px 0; }}
                .detail-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #eee; }}
                .detail-row:last-child {{ border-bottom: none; }}
                .detail-label {{ color: #666; }}
                .detail-value {{ font-weight: 600; color: #1a1a2e; }}
                .checklist {{ background: #fffbeb; border-radius: 8px; padding: 20px; margin: 20px 0; }}
                .checklist h3 {{ margin-top: 0; color: #92400e; }}
                .checklist li {{ margin: 8px 0; color: #78350f; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 14px; }}
                .footer a {{ color: #d4a843; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>LGU MUN Society</h1>
                    <p>Intra-University Model United Nations 2026</p>
                </div>
                <div class="content">
                    <p>Dear <strong>{delegate_name}</strong>,</p>
                    <p>Your registration has been successfully confirmed! 🎉</p>

                    <div class="roll-box">
                        <p style="margin: 0 0 10px; color: #666;">Your Roll Number</p>
                        <p class="roll-number">{roll_number}</p>
                    </div>

                    <div class="details">
                        <div class="detail-row">
                            <span class="detail-label">Committee</span>
                            <span class="detail-value">{committee_name}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Event Dates</span>
                            <span class="detail-value">{EVENT_DATES}</span>
                        </div>
                        <div class="detail-row">
                            <span class="detail-label">Venue</span>
                            <span class="detail-value">{EVENT_VENUE}</span>
                        </div>
                    </div>

                    <div class="checklist">
                        <h3>📋 What to Bring</h3>
                        <ul>
                            <li>Valid CNIC / Student ID</li>
                            <li>Formal attire (Western or South Asian formal)</li>
                            <li>Position paper (3 copies) — Check with your committee chair</li>
                            <li>Notepad and pen</li>
                            <li>Research materials on your country/position</li>
                        </ul>
                    </div>

                    <p><strong>Next Steps:</strong></p>
                    <p>You will receive another email when your <strong>country/personality assignment</strong> is finalized by the MUN Society. Stay tuned!</p>

                    <p>If you have any questions, use the query portal on our website.</p>

                    <p>Best regards,<br><strong>LGU MUN Society</strong></p>
                </div>
                <div class="footer">
                    <p>LGU MUN 2026 • {EVENT_VENUE}</p>
                    <p>Questions? Contact us through the <a href="http://localhost:8000/success.html">Query Portal</a></p>
                </div>
            </div>
        </body>
        </html>
        """

        plain_body = f"""
LGU MUN 2026 — Registration Confirmed

Dear {delegate_name},

Your registration has been successfully confirmed!

ROLL NUMBER: {roll_number}
Committee: {committee_name}
Event Dates: {EVENT_DATES}
Venue: {EVENT_VENUE}

What to Bring:
- Valid CNIC / Student ID
- Formal attire
- Position paper (3 copies)
- Notepad and pen
- Research materials

You will receive another email when your country/personality assignment is finalized.

Best regards,
LGU MUN Society
        """

        return self.send_email(to_email, subject, html_body, plain_body)

    def send_country_assignment(
        self,
        to_email: str,
        delegate_name: str,
        roll_number: str,
        committee_name: str,
        allocation_type: str,  # "country" or "personality"
        assigned_value: str,   # Country name or Personality name
        prep_note: str = "",
        study_link: str = ""
    ) -> bool:
        """
        Send country/personality assignment email (Email 2)
        Fires ONLY when admin clicks Publish
        """
        type_label = "Country" if allocation_type == "country" else "Personality"
        emoji = "🌍" if allocation_type == "country" else "🎭"

        subject = f"LGU MUN 2026 — Your {type_label} Assignment {emoji}"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f4f4; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding: 30px; text-align: center; color: #fff; }}
                .header h1 {{ margin: 0; font-size: 28px; color: #d4a843; }}
                .header p {{ margin: 10px 0 0; opacity: 0.8; }}
                .content {{ padding: 30px; }}
                .assignment-box {{ background: linear-gradient(135deg, #d4a843 0%, #f5cf58 100%); border-radius: 12px; padding: 25px; text-align: center; margin: 20px 0; }}
                .assignment-type {{ font-size: 14px; text-transform: uppercase; letter-spacing: 2px; color: #7a5a1a; margin: 0; }}
                .assignment-value {{ font-size: 36px; font-weight: bold; color: #1a1a2e; margin: 10px 0 0; }}
                .committee-badge {{ display: inline-block; background: #1a1a2e; color: #d4a843; padding: 8px 20px; border-radius: 20px; font-size: 14px; margin-top: 15px; }}
                .prep-section {{ background: #f0fdf4; border-left: 4px solid #22c55e; border-radius: 0 8px 8px 0; padding: 20px; margin: 20px 0; }}
                .prep-section h3 {{ margin-top: 0; color: #166534; }}
                .prep-section p {{ color: #15803d; line-height: 1.6; }}
                .study-link {{ display: inline-block; background: #22c55e; color: #fff; padding: 12px 24px; border-radius: 8px; text-decoration: none; margin-top: 15px; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 14px; }}
                .footer a {{ color: #d4a843; text-decoration: none; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>LGU MUN Society</h1>
                    <p>Intra-University Model United Nations 2026</p>
                </div>
                <div class="content">
                    <p>Dear <strong>{delegate_name}</strong>,</p>
                    <p>Your {type_label.lower()} has been assigned! 🎭</p>

                    <div class="assignment-box">
                        <p class="assignment-type">{type_label}</p>
                        <p class="assignment-value">{assigned_value}</p>
                        <span class="committee-badge">{committee_name}</span>
                    </div>
        """

        if prep_note:
            html_body += f"""
                    <div class="prep-section">
                        <h3>📚 Preparation Notes</h3>
                        <p>{prep_note}</p>
                    </div>
            """

        if study_link:
            html_body += f"""
                    <div style="text-align: center; margin: 20px 0;">
                        <a href="{study_link}" class="study-link">📖 Access Study Materials</a>
                    </div>
            """

        html_body += f"""
                    <p><strong>Next Steps:</strong></p>
                    <ul>
                        <li>Research your {type_label.lower()}'s position on key agenda topics</li>
                        <li>Prepare opening remarks and policy statements</li>
                        <li>Review the committee's rules of procedure</li>
                        <li>Draft position papers if required by your committee</li>
                    </ul>

                    <p>We look forward to an exceptional MUN experience with you!</p>

                    <p>Best regards,<br><strong>LGU MUN Society</strong></p>
                </div>
                <div class="footer">
                    <p>LGU MUN 2026 • {EVENT_VENUE}</p>
                    <p>Questions? Contact us through the <a href="http://localhost:8000/success.html">Query Portal</a></p>
                </div>
            </div>
        </body>
        </html>
        """

        plain_body = f"""
LGU MUN 2026 — Your {type_label} Assignment

Dear {delegate_name},

Your {type_label} has been assigned!

{type_label.upper()}: {assigned_value}
Committee: {committee_name}

{prep_note if prep_note else ''}

Study Materials: {study_link if study_link else 'Check with your committee chair'}

Next Steps:
1. Research your {type_label.lower()}'s position on key agenda topics
2. Prepare opening remarks and policy statements
3. Review the committee's rules of procedure
4. Draft position papers if required

Best regards,
LGU MUN Society
        """

        return self.send_email(to_email, subject, html_body, plain_body)


# Singleton instance
email_service = EmailService()


def send_registration_confirmation(
    to_email: str,
    delegate_name: str,
    roll_number: str,
    committee_name: str,
    committee_short: str
) -> bool:
    """Convenience function"""
    return email_service.send_registration_confirmation(
        to_email, delegate_name, roll_number, committee_name, committee_short
    )


def send_country_assignment(
    to_email: str,
    delegate_name: str,
    roll_number: str,
    committee_name: str,
    allocation_type: str,
    assigned_value: str,
    prep_note: str = "",
    study_link: str = ""
) -> bool:
    """Convenience function"""
    return email_service.send_country_assignment(
        to_email, delegate_name, roll_number, committee_name,
        allocation_type, assigned_value, prep_note, study_link
    )