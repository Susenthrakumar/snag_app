import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdminAppointmentEmailSender:
    def __init__(self):
        # Email configuration - using working credentials
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_address = "susenthrakumar@gmail.com"
        self.email_password = "oytj ipzo vilu qqon"
        
    def send_owner_notification(self, unit_details, inspector_details, appointment_date, time_slot, title, notes, admin_name):
        """Send appointment notification email to unit owner"""
        try:
            # Format date
            formatted_date = datetime.strptime(appointment_date, '%Y-%m-%d').strftime('%B %d, %Y')
            
            subject = f"Appointment Scheduled - {title}"
            
            # HTML email template for unit owner
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                        border-radius: 10px 10px 0 0;
                    }}
                    .content {{
                        background: #f8f9fa;
                        padding: 30px;
                        border-radius: 0 0 10px 10px;
                    }}
                    .appointment-details {{
                        background: white;
                        padding: 20px;
                        border-radius: 8px;
                        margin: 20px 0;
                        border-left: 4px solid #667eea;
                    }}
                    .detail-row {{
                        display: flex;
                        justify-content: space-between;
                        margin: 10px 0;
                        padding: 8px 0;
                        border-bottom: 1px solid #eee;
                    }}
                    .detail-label {{
                        font-weight: bold;
                        color: #667eea;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding: 20px;
                        background: #e9ecef;
                        border-radius: 8px;
                        font-size: 14px;
                        color: #6c757d;
                    }}
                    .company-name {{
                        font-size: 24px;
                        font-weight: bold;
                        margin-bottom: 10px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <div class="company-name">Better Communities</div>
                    <p>Appointment Scheduled by Admin</p>
                </div>
                
                <div class="content">
                    <h2>Dear {unit_details['owner_name']},</h2>
                    
                    <p>An appointment has been scheduled for your unit by our admin team. Please find the details below:</p>
                    
                    <div class="appointment-details">
                        <h3 style="color: #667eea; margin-top: 0;">Appointment Details</h3>
                        
                        <div class="detail-row">
                            <span class="detail-label">Title:</span>
                            <span>{title}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="detail-label">Date:</span>
                            <span>{formatted_date}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="detail-label">Time:</span>
                            <span>{time_slot}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="detail-label">Unit:</span>
                            <span>{unit_details['unit_number']} - {unit_details['floor_name']}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="detail-label">Project:</span>
                            <span>{unit_details['project_name']}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="detail-label">Inspector:</span>
                            <span>{inspector_details['name']}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="detail-label">Inspector Contact:</span>
                            <span>{inspector_details['email']} | {inspector_details['phone']}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="detail-label">Scheduled By:</span>
                            <span>{admin_name} (Admin)</span>
                        </div>
                        
                        {f'<div class="detail-row"><span class="detail-label">Notes:</span><span>{notes}</span></div>' if notes else ''}
                    </div>
                    
                    <p><strong>Important:</strong> Please ensure you are available at the scheduled time. If you need to reschedule, please contact our admin team as soon as possible.</p>
                    
                    <p>Thank you for your cooperation.</p>
                </div>
                
                <div class="footer">
                    <p><strong>Better Communities</strong><br>
                    Professional Property Management Services<br>
                    Email: bettercommunities.ae@gmail.com</p>
                </div>
            </body>
            </html>
            """
            
            # Send email
            self._send_email(unit_details['owner_email'], subject, html_body)
            logger.info(f"Owner notification email sent to {unit_details['owner_email']}")
            
        except Exception as e:
            logger.error(f"Error sending owner notification email: {str(e)}")
            raise
    
    def send_inspector_notification(self, unit_details, inspector_details, appointment_date, time_slot, title, notes, admin_name):
        """Send appointment notification email to inspector"""
        try:
            # Format date
            formatted_date = datetime.strptime(appointment_date, '%Y-%m-%d').strftime('%B %d, %Y')
            
            subject = f"New Appointment Assignment - {title}"
            
            # HTML email template for inspector
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                        border-radius: 10px 10px 0 0;
                    }}
                    .content {{
                        background: #f8f9fa;
                        padding: 30px;
                        border-radius: 0 0 10px 10px;
                    }}
                    .appointment-details {{
                        background: white;
                        padding: 20px;
                        border-radius: 8px;
                        margin: 20px 0;
                        border-left: 4px solid #28a745;
                    }}
                    .detail-row {{
                        display: flex;
                        justify-content: space-between;
                        margin: 10px 0;
                        padding: 8px 0;
                        border-bottom: 1px solid #eee;
                    }}
                    .detail-label {{
                        font-weight: bold;
                        color: #28a745;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding: 20px;
                        background: #e9ecef;
                        border-radius: 8px;
                        font-size: 14px;
                        color: #6c757d;
                    }}
                    .company-name {{
                        font-size: 24px;
                        font-weight: bold;
                        margin-bottom: 10px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <div class="company-name">Better Communities</div>
                    <p>New Appointment Assignment</p>
                </div>
                
                <div class="content">
                    <h2>Dear {inspector_details['name']},</h2>
                    
                    <p>You have been assigned a new appointment by our admin team. Please find the details below:</p>
                    
                    <div class="appointment-details">
                        <h3 style="color: #28a745; margin-top: 0;">Appointment Details</h3>
                        
                        <div class="detail-row">
                            <span class="detail-label">Title:</span>
                            <span>{title}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="detail-label">Date:</span>
                            <span>{formatted_date}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="detail-label">Time:</span>
                            <span>{time_slot}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="detail-label">Unit Owner:</span>
                            <span>{unit_details['owner_name']}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="detail-label">Owner Contact:</span>
                            <span>{unit_details['owner_email']} | {unit_details['owner_phone']}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="detail-label">Unit:</span>
                            <span>{unit_details['unit_number']} - {unit_details['floor_name']}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="detail-label">Project:</span>
                            <span>{unit_details['project_name']}</span>
                        </div>
                        
                        <div class="detail-row">
                            <span class="detail-label">Assigned By:</span>
                            <span>{admin_name} (Admin)</span>
                        </div>
                        
                        {f'<div class="detail-row"><span class="detail-label">Notes:</span><span>{notes}</span></div>' if notes else ''}
                    </div>
                    
                    <p><strong>Action Required:</strong> Please confirm your availability and prepare for the scheduled appointment. Contact the unit owner if needed to coordinate the visit.</p>
                    
                    <p>Thank you for your service.</p>
                </div>
                
                <div class="footer">
                    <p><strong>Better Communities</strong><br>
                    Professional Property Management Services<br>
                    Email: bettercommunities.ae@gmail.com</p>
                </div>
            </body>
            </html>
            """
            
            # Send email
            self._send_email(inspector_details['email'], subject, html_body)
            logger.info(f"Inspector notification email sent to {inspector_details['email']}")
            
        except Exception as e:
            logger.error(f"Error sending inspector notification email: {str(e)}")
            raise
    
    def _send_email(self, to_email, subject, html_body):
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_address
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add HTML content
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)

            # Send email with SSL context
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email_address, self.email_password)
                server.sendmail(self.email_address, to_email, msg.as_string())

        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            raise
