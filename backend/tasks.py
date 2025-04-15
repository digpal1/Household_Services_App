from datetime import datetime
from io import StringIO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import csv
import os
from celery_config import celery
from household.model import db, Bookings, Services, User, SubmitFeedback
from app import create_app


def send_email(to_email, subject, html_content):
    """Send an email using a local SMTP server."""
    from_email = 'admin@household.com'
    msg = MIMEMultipart('alternative')
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(html_content, 'html'))

    smtp_server = 'localhost'
    smtp_port = 1025

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.sendmail(from_email, to_email, msg.as_string())

@celery.task
@celery.task
def send_daily_reminders():
    from app import create_app

    app = create_app()
    with app.app_context():
        pending_bookings = Bookings.query.filter_by(status=False).all()
        for booking in pending_bookings:
            professional_email = booking.user.email
            send_email(
                professional_email,
                "Daily Reminder: Pending Service Request",
                f"<p>Dear {booking.user.full_name},</p>"
                f"<p>You have a pending service request. Please visit or accept/reject it at your earliest convenience.</p>"
            )
@celery.task
def generate_monthly_report():
    from app import create_app
    app = create_app()
    with app.app_context():
        current_month = datetime.now().strftime('%B')
        current_year = datetime.now().year

        users = User.query.all()
        for user in users:
            services_closed = Bookings.query.filter_by(user_id=user.id, status=True).count()
            html_content = f"""
            <html>
            <head><title>Monthly Activity Report</title></head>
            <body>
                <p>Monthly Activity Report for {user.full_name}</p>
                <p>Services Closed in {current_month} {current_year}: {services_closed}</p>
            </body>
            </html>
            """
            send_email(user.email, "Monthly Activity Report", html_content)

@celery.task
def generate_daily_report():
    from app import create_app
    app = create_app()
    with app.app_context():
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Retrieve all users
        users = User.query.all()
        for user in users:
            # Calculate total bookings
            total_bookings = Bookings.query.filter_by(user_id=user.id).count()

            # Calculate completed bookings
            completed_bookings = Bookings.query.filter_by(user_id=user.id, status=True).count()

            # Calculate pending bookings
            pending_bookings = Bookings.query.filter_by(user_id=user.id, status=False).count()

            # Compose the HTML content for the email report
            html_content = f"""
            <html>
            <head><title>Daily Activity Report</title></head>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2 style="color: #2E86C1;">Daily Activity Report for {user.full_name}</h2>
                <p>Date: {current_date}</p>
                <hr>
                <h3>Booking Summary:</h3>
                <ul>
                    <li><strong>Total Bookings:</strong> {total_bookings}</li>
                    <li><strong>Completed Bookings:</strong> {completed_bookings}</li>
                    <li><strong>Pending Bookings:</strong> {pending_bookings}</li>
                    <li><strong>Rejected Bookings:</strong> {total_bookings - completed_bookings - pending_bookings}</li>
                </ul>
                <p>Thank you for using our services!</p>
                <footer style="margin-top: 20px; color: #888;">
                    <p>This report was generated automatically. Please do not reply to this email.</p>
                </footer>
            </body>
            </html>
            """

            # Compose a detailed subject for the report email
            subject = f"Daily Activity Report - {user.full_name} ({current_date})"

            # Send the email to the user
            send_email(user.email, subject, html_content)

def export_closed_service_as_csv(user_id):
    """Export closed service requests for a user into a CSV."""
    app = create_app()
    with app.app_context():
        bookings = (
            Bookings.query.filter_by(user_id=user_id, status=True)
            .join(Services, Bookings.service_id == Services.id)
            .all()
        )

        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer)
        csv_writer.writerow([
            "Booking ID", "Service Name", "Professional Name", "Request Date",
            "Completion Date", "Remarks"
        ])

        for booking in bookings:
            csv_writer.writerow([
                booking.id, booking.services.service_name,
                booking.professional_name, booking.request_date,
                booking.complete_date, booking.submit_feedback.remarks if booking.submit_feedback else ""
            ])

        return csv_buffer.getvalue()