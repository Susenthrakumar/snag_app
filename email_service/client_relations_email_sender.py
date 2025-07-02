import smtplib
import ssl
import secrets
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class ClientRelationsEmailSender:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email = "susenthrakumar@gmail.com"
        self.password = "oytj ipzo vilu qqon"
    
    def generate_registration_token(self):
        """Generate a secure registration token"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    
    def create_email_template(self, content_html, content_text):
        """Create a professional email template with HTML and text versions"""
        return content_html, content_text
    
    def send_client_invitation(self, client_email, registration_token, base_url="http://127.0.0.1:5000"):
        """Send professional invitation email to client"""
        try:
            # Registration URL
            registration_url = f"{base_url}/client_relations/register?token={registration_token}&email={client_email}"
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "🎯 You're Invited to Join SNAG Management System - Client Portal"
            msg['From'] = self.email
            msg['To'] = client_email
            
            # HTML version
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Client Portal Invitation - SNAG Management System</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }}
        
        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 10px;
        }}
        
        .header p {{
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
            text-align: center;
        }}
        
        .info-box {{
            background-color: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 25px 0;
            border-radius: 6px;
        }}
        
        .info-box h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 18px;
        }}
        
        .info-box ul {{
            list-style: none;
            padding: 0;
        }}
        
        .info-box li {{
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
            display: flex;
            align-items: center;
        }}
        
        .info-box li:last-child {{
            border-bottom: none;
        }}
        
        .info-box li::before {{
            content: "✓";
            color: #28a745;
            font-weight: bold;
            margin-right: 10px;
            font-size: 16px;
        }}
        
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            padding: 15px 35px;
            border-radius: 50px;
            font-weight: 600;
            font-size: 16px;
            text-align: center;
            margin: 30px 0;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .cta-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }}
        
        .button-container {{
            text-align: center;
            margin: 30px 0;
        }}
        
        .footer {{
            background-color: #2c3e50;
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .footer p {{
            margin-bottom: 10px;
            opacity: 0.8;
        }}
        
        .contact-info {{
            background-color: #34495e;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        
        .contact-info h4 {{
            margin-bottom: 15px;
            color: #ecf0f1;
        }}
        
        .contact-info p {{
            margin-bottom: 8px;
            opacity: 0.9;
        }}
        
        .security-note {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
            font-size: 14px;
        }}
        
        .security-note strong {{
            color: #d63031;
        }}
        
        @media (max-width: 600px) {{
            .email-container {{
                margin: 0;
                border-radius: 0;
            }}
            
            .header, .content, .footer {{
                padding: 20px;
            }}
            
            .header h1 {{
                font-size: 24px;
            }}
            
            .cta-button {{
                padding: 12px 25px;
                font-size: 14px;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>🎯 Client Portal Invitation</h1>
            <p>SNAG Management System</p>
        </div>
        
        <div class="content">
            <p class="welcome-text">
                <strong>Welcome to SNAG Management System!</strong><br>
                You've been invited to join our client portal.
            </p>
            
            <div class="info-box">
                <h3>🌟 What You'll Get Access To:</h3>
                <ul>
                    <li>Project progress tracking and updates</li>
                    <li>Real-time communication with project teams</li>
                    <li>Document and report access</li>
                    <li>Quality inspection reports and SNAG lists</li>
                    <li>Direct communication with contractors and inspectors</li>
                    <li>Project timeline and milestone tracking</li>
                </ul>
            </div>
            
            <div class="button-container">
                <a href="{registration_url}" class="cta-button">
                    🚀 Complete Your Registration
                </a>
            </div>
            
            <div class="security-note">
                <strong>🔒 Security Notice:</strong> This invitation link is unique to your email address and will expire after use. Please complete your registration as soon as possible.
            </div>
            
            <p style="text-align: center; color: #6c757d; font-size: 14px; margin-top: 30px;">
                If the button doesn't work, copy and paste this link into your browser:<br>
                <a href="{registration_url}" style="color: #667eea; word-break: break-all;">{registration_url}</a>
            </p>
        </div>
        
        <div class="footer">
            <p><strong>SNAG Management System</strong></p>
            <p>Professional Project Management & Quality Control</p>
            
            <div class="contact-info">
                <h4>📞 Need Help?</h4>
                <p>Email: support@snagmanagement.com</p>
                <p>Phone: +91 98765 43210</p>
                <p>Available: Monday - Friday, 9 AM - 6 PM</p>
            </div>
        </div>
    </div>
</body>
</html>
            """
            
            # Text version
            text_content = f"""
SNAG Management System - Client Portal Invitation

Welcome to SNAG Management System!

You've been invited to join our client portal where you can:
- Track project progress and updates
- Communicate with project teams
- Access documents and reports
- View quality inspection reports
- Communicate with contractors and inspectors
- Track project timelines and milestones

Complete your registration by clicking this link:
{registration_url}

If you have any questions, please contact our support team:
Email: support@snagmanagement.com
Phone: +91 98765 43210

Thank you for choosing SNAG Management System!

---
This is an automated email. Please do not reply to this message.
            """
            
            # Create message parts
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            
            # Add parts to message
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email, self.password)
                server.send_message(msg)
            
            print(f"Client invitation sent successfully to {client_email}")
            return True
            
        except Exception as e:
            print(f"Error sending client invitation to {client_email}: {e}")
            return False

    def send_welcome_email(self, client_email, client_name):
        """Send professional welcome email after successful registration"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🎉 Welcome to SNAG Management System, {client_name}!"
            msg['From'] = self.email
            msg['To'] = client_email

            # HTML version
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to SNAG Management System</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }}

        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}

        .header {{
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 10px;
        }}

        .content {{
            padding: 40px 30px;
        }}

        .welcome-text {{
            font-size: 18px;
            color: #2c3e50;
            margin-bottom: 25px;
            text-align: center;
        }}

        .success-badge {{
            background-color: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            margin: 20px 0;
            border: 1px solid #c3e6cb;
        }}

        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            text-decoration: none;
            padding: 15px 35px;
            border-radius: 50px;
            font-weight: 600;
            font-size: 16px;
            text-align: center;
            margin: 30px 0;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(40, 167, 69, 0.4);
        }}

        .button-container {{
            text-align: center;
            margin: 30px 0;
        }}

        .footer {{
            background-color: #2c3e50;
            color: white;
            padding: 30px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>🎉 Welcome, {client_name}!</h1>
            <p>Your Client Portal is Ready</p>
        </div>

        <div class="content">
            <div class="success-badge">
                <strong>✅ Registration Successful!</strong><br>
                Your client account has been activated.
            </div>

            <p class="welcome-text">
                Thank you for joining SNAG Management System! You now have access to our comprehensive client portal.
            </p>

            <div class="button-container">
                <a href="http://127.0.0.1:5000/login" class="cta-button">
                    🚀 Access Your Dashboard
                </a>
            </div>
        </div>

        <div class="footer">
            <p><strong>SNAG Management System</strong></p>
            <p>Professional Project Management & Quality Control</p>
        </div>
    </div>
</body>
</html>
            """

            # Text version
            text_content = f"""
Welcome to SNAG Management System, {client_name}!

Your client account has been successfully activated.

You can now access your dashboard at: http://127.0.0.1:5000/login

Thank you for joining SNAG Management System!

---
SNAG Management System
Professional Project Management & Quality Control
            """

            # Create message parts
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')

            # Add parts to message
            msg.attach(part1)
            msg.attach(part2)

            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email, self.password)
                server.send_message(msg)

            print(f"Welcome email sent successfully to {client_email}")
            return True

        except Exception as e:
            print(f"Error sending welcome email to {client_email}: {e}")
            return False
