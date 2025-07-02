import smtplib
import ssl
import secrets
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class InspectorEmailSender:
    def __init__(self):
        # SMTP Configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "susenthrakumar@gmail.com"
        self.sender_password = "oytj ipzo vilu qqon"
        self.sender_name = "SNAG Management System"
    
    def create_email_template(self, content_html, content_text):
        """Create a professional email template with HTML and text versions"""
        return content_html, content_text
    
    def send_inspector_invitation(self, inspector_email, registration_token, base_url="http://127.0.0.1:5000"):
        """Send professional invitation email to SNAG inspector"""
        try:
            # Registration URL
            registration_url = f"{base_url}/snag-inspectors/register?token={registration_token}&email={inspector_email}"
            
            # Email subject
            subject = "🔍 SNAG Inspector Invitation - Join Our Quality Assurance Team"
            
            # HTML email content
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>SNAG Inspector Invitation</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f8f9fa;
                    }}
                    .email-container {{
                        background: white;
                        border-radius: 16px;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                        overflow: hidden;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 40px 30px;
                        text-align: center;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 28px;
                        font-weight: 700;
                    }}
                    .header p {{
                        margin: 10px 0 0 0;
                        font-size: 16px;
                        opacity: 0.9;
                    }}
                    .content {{
                        padding: 40px 30px;
                    }}
                    .welcome-text {{
                        font-size: 18px;
                        color: #2c3e50;
                        margin-bottom: 25px;
                        font-weight: 600;
                    }}
                    .description {{
                        font-size: 16px;
                        color: #555;
                        margin-bottom: 30px;
                        line-height: 1.7;
                    }}
                    .cta-button {{
                        display: inline-block;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        text-decoration: none;
                        padding: 16px 32px;
                        border-radius: 50px;
                        font-weight: 600;
                        font-size: 16px;
                        margin: 20px 0;
                        transition: transform 0.3s ease;
                    }}
                    .cta-button:hover {{
                        transform: translateY(-2px);
                    }}
                    .features {{
                        background: #f8f9fa;
                        border-radius: 12px;
                        padding: 25px;
                        margin: 30px 0;
                    }}
                    .features h3 {{
                        color: #2c3e50;
                        margin-bottom: 15px;
                        font-size: 18px;
                    }}
                    .features ul {{
                        list-style: none;
                        padding: 0;
                        margin: 0;
                    }}
                    .features li {{
                        padding: 8px 0;
                        color: #555;
                        position: relative;
                        padding-left: 25px;
                    }}
                    .features li:before {{
                        content: "✓";
                        position: absolute;
                        left: 0;
                        color: #27ae60;
                        font-weight: bold;
                    }}
                    .footer {{
                        background: #2c3e50;
                        color: white;
                        padding: 30px;
                        text-align: center;
                    }}
                    .footer p {{
                        margin: 5px 0;
                        opacity: 0.8;
                    }}
                    .credentials {{
                        background: #e8f4fd;
                        border-left: 4px solid #3498db;
                        padding: 20px;
                        margin: 25px 0;
                        border-radius: 0 8px 8px 0;
                    }}
                    .credentials h4 {{
                        color: #2980b9;
                        margin-bottom: 10px;
                    }}
                    .credentials p {{
                        margin: 5px 0;
                        color: #34495e;
                    }}
                    @media (max-width: 600px) {{
                        body {{
                            padding: 10px;
                        }}
                        .header, .content, .footer {{
                            padding: 20px;
                        }}
                        .header h1 {{
                            font-size: 24px;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="header">
                        <h1>🔍 SNAG Inspector Invitation</h1>
                        <p>Join Our Quality Assurance Team</p>
                    </div>
                    
                    <div class="content">
                        <div class="welcome-text">
                            Welcome to SNAG Management System!
                        </div>
                        
                        <div class="description">
                            You have been invited to join our team as a <strong>SNAG Inspector</strong>. As a quality assurance professional, you'll play a crucial role in ensuring project excellence through comprehensive inspections and detailed reporting.
                        </div>
                        
                        <div class="features">
                            <h3>🎯 Your Inspector Responsibilities:</h3>
                            <ul>
                                <li>Conduct thorough SNAG inspections</li>
                                <li>Document quality issues with photos</li>
                                <li>Generate detailed inspection reports</li>
                                <li>Track resolution progress</li>
                                <li>Collaborate with project teams</li>
                                <li>Ensure compliance standards</li>
                            </ul>
                        </div>
                        
                        <div style="text-align: center;">
                            <a href="{registration_url}" class="cta-button">
                                🚀 Complete Registration
                            </a>
                        </div>
                        
                        <div class="credentials">
                            <h4>📧 Your Registration Details:</h4>
                            <p><strong>Email:</strong> {inspector_email}</p>
                            <p><strong>Role:</strong> SNAG Inspector</p>
                            <p><strong>Registration Link:</strong> Valid for 7 days</p>
                        </div>
                        
                        <div class="description">
                            <strong>Next Steps:</strong><br>
                            1. Click the registration button above<br>
                            2. Complete your profile setup<br>
                            3. Set up your secure password<br>
                            4. Start your first inspection assignment
                        </div>
                        
                        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 14px; color: #666;">
                            <p><strong>Need Help?</strong> Contact our support team if you have any questions about the registration process.</p>
                            <p>You can login to your dashboard at: <a href="{base_url}/login" style="color: #667eea;">{base_url}/login</a></p>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p><strong>SNAG Management System</strong></p>
                        <p>Quality Assurance & Project Management Platform</p>
                        <p>© 2025 All rights reserved</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            text_content = f"""
            SNAG Inspector Invitation - Join Our Quality Assurance Team
            
            Welcome to SNAG Management System!
            
            You have been invited to join our team as a SNAG Inspector. As a quality assurance professional, you'll play a crucial role in ensuring project excellence through comprehensive inspections and detailed reporting.
            
            Your Inspector Responsibilities:
            • Conduct thorough SNAG inspections
            • Document quality issues with photos
            • Generate detailed inspection reports
            • Track resolution progress
            • Collaborate with project teams
            • Ensure compliance standards
            
            Registration Details:
            Email: {inspector_email}
            Role: SNAG Inspector
            Registration Link: Valid for 7 days
            
            Complete your registration here: {registration_url}
            
            Next Steps:
            1. Click the registration link above
            2. Complete your profile setup
            3. Set up your secure password
            4. Start your first inspection assignment
            
            You can login to your dashboard at: {base_url}/login
            
            Need Help? Contact our support team if you have any questions about the registration process.
            
            SNAG Management System
            Quality Assurance & Project Management Platform
            © 2025 All rights reserved
            """
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.sender_name} <{self.sender_email}>"
            message["To"] = inspector_email
            
            # Add both versions
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, inspector_email, message.as_string())
            
            return True, "Professional invitation email sent successfully"
            
        except Exception as e:
            return False, f"Failed to send invitation email: {str(e)}"
    
    def send_welcome_email(self, inspector_email, inspector_name):
        """Send professional welcome email after successful registration"""
        try:
            # Email subject
            subject = "🎉 Welcome to SNAG Management System - Inspector Account Activated"
            
            # HTML email content
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Welcome SNAG Inspector</title>
                <style>
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f8f9fa;
                    }}
                    .email-container {{
                        background: white;
                        border-radius: 16px;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                        overflow: hidden;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
                        color: white;
                        padding: 40px 30px;
                        text-align: center;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 28px;
                        font-weight: 700;
                    }}
                    .content {{
                        padding: 40px 30px;
                    }}
                    .welcome-text {{
                        font-size: 18px;
                        color: #2c3e50;
                        margin-bottom: 25px;
                        font-weight: 600;
                    }}
                    .cta-button {{
                        display: inline-block;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        text-decoration: none;
                        padding: 16px 32px;
                        border-radius: 50px;
                        font-weight: 600;
                        font-size: 16px;
                        margin: 20px 0;
                    }}
                    .footer {{
                        background: #2c3e50;
                        color: white;
                        padding: 30px;
                        text-align: center;
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="header">
                        <h1>🎉 Welcome {inspector_name}!</h1>
                        <p>Your SNAG Inspector account is now active</p>
                    </div>
                    
                    <div class="content">
                        <div class="welcome-text">
                            Congratulations! Your registration is complete.
                        </div>
                        
                        <p>You can now access your inspector dashboard and start managing SNAG inspections.</p>
                        
                        <div style="text-align: center;">
                            <a href="http://127.0.0.1:5000/login" class="cta-button">
                                🚀 Access Dashboard
                            </a>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p><strong>SNAG Management System</strong></p>
                        <p>Quality Assurance & Project Management Platform</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            text_content = f"""
            Welcome {inspector_name}!
            
            Congratulations! Your SNAG Inspector registration is complete.
            
            You can now access your inspector dashboard and start managing SNAG inspections.
            
            Login at: http://127.0.0.1:5000/login
            
            SNAG Management System
            Quality Assurance & Project Management Platform
            """
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.sender_name} <{self.sender_email}>"
            message["To"] = inspector_email
            
            # Add both versions
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            
            message.attach(part1)
            message.attach(part2)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, inspector_email, message.as_string())
            
            return True, "Welcome email sent successfully"
            
        except Exception as e:
            return False, f"Failed to send welcome email: {str(e)}"
