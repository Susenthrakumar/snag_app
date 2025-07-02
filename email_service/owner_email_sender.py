import smtplib
import ssl
import secrets
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class OwnerEmailSender:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email = "susenthrakumar@gmail.com"
        self.password = "oytj ipzo vilu qqon"
    
    def generate_invitation_token(self):
        """Generate a secure invitation token"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    
    def send_unit_assignment_invitation(self, owner_email, owner_name, unit_number, floor_name, project_name, invitation_token, base_url="http://127.0.0.1:5000"):
        """Send professional unit assignment invitation email to owner"""
        try:
            # Registration URL
            registration_url = f"{base_url}/owner/register?token={invitation_token}&email={owner_email}"
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🏠 Unit Assignment - {project_name} | {floor_name} - Unit {unit_number}"
            msg['From'] = self.email
            msg['To'] = owner_email
            
            # HTML version
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unit Assignment Invitation</title>
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
            margin-bottom: 10px;
            font-weight: 700;
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
            margin-bottom: 30px;
            text-align: center;
            color: #2c3e50;
        }}

        .unit-details {{
            background: #f8f9fa;
            border-radius: 12px;
            padding: 25px;
            margin: 30px 0;
            border-left: 5px solid #667eea;
        }}

        .unit-details h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 20px;
        }}

        .detail-item {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }}

        .detail-item:last-child {{
            border-bottom: none;
        }}

        .detail-label {{
            font-weight: 600;
            color: #495057;
        }}

        .detail-value {{
            color: #2c3e50;
            font-weight: 500;
        }}

        .info-box {{
            background: #e8f4fd;
            border-radius: 12px;
            padding: 25px;
            margin: 30px 0;
            border-left: 5px solid #3498db;
        }}

        .info-box h3 {{
            color: #2980b9;
            margin-bottom: 15px;
            font-size: 18px;
        }}

        .info-box ul {{
            list-style: none;
            padding: 0;
        }}

        .info-box li {{
            padding: 8px 0;
            color: #34495e;
            position: relative;
            padding-left: 25px;
        }}

        .info-box li:before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: #27ae60;
            font-weight: bold;
        }}

        .button-container {{
            text-align: center;
            margin: 40px 0;
        }}

        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 18px 40px;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }}

        .cta-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
            color: white;
            text-decoration: none;
        }}

        .footer {{
            background: #2c3e50;
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .footer h3 {{
            margin-bottom: 15px;
            color: #ecf0f1;
        }}

        .footer p {{
            margin-bottom: 10px;
            opacity: 0.8;
        }}

        .footer .contact-info {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #34495e;
        }}

        .warning-box {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 20px;
            margin: 25px 0;
            color: #856404;
        }}

        .warning-box strong {{
            color: #b8860b;
        }}

        @media (max-width: 600px) {{
            .email-container {{
                margin: 0;
                border-radius: 0;
            }}
            
            .header, .content, .footer {{
                padding: 25px 20px;
            }}
            
            .unit-details, .info-box {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>🏠 Unit Assignment</h1>
            <p>SNAG Management System</p>
        </div>
        
        <div class="content">
            <p class="welcome-text">
                <strong>Dear {owner_name},</strong><br>
                You have been assigned a unit in our project. Please confirm and register to access your unit details.
            </p>
            
            <div class="unit-details">
                <h3>📋 Your Unit Details</h3>
                <div class="detail-item">
                    <span class="detail-label">Project:</span>
                    <span class="detail-value">{project_name}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Floor:</span>
                    <span class="detail-value">{floor_name}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Unit Number:</span>
                    <span class="detail-value">{unit_number}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Email:</span>
                    <span class="detail-value">{owner_email}</span>
                </div>
            </div>
            
            <div class="info-box">
                <h3>🌟 What You'll Get Access To:</h3>
                <ul>
                    <li>Unit progress tracking and updates</li>
                    <li>Quality inspection reports and SNAG lists</li>
                    <li>Direct communication with project teams</li>
                    <li>Document and report access</li>
                    <li>Project timeline and milestone tracking</li>
                    <li>Maintenance request submission</li>
                </ul>
            </div>
            
            <div class="button-container">
                <a href="{registration_url}" class="cta-button">
                    🚀 Confirm & Register
                </a>
            </div>
            
            <div class="warning-box">
                <strong>Important:</strong> This invitation link is valid for a limited time. Please complete your registration as soon as possible to access your unit information.
            </div>
        </div>
        
        <div class="footer">
            <h3>SNAG Management System</h3>
            <p>Quality Assurance & Project Management Platform</p>
            
            <div class="contact-info">
                <p><strong>Need Help?</strong></p>
                <p>Email: support@snagmanagement.com</p>
                <p>Phone: +971 50 123 4567</p>
            </div>
        </div>
    </div>
</body>
</html>
            """
            
            # Text version
            text_content = f"""
Unit Assignment - {project_name}

Dear {owner_name},

You have been assigned a unit in our project. Please confirm and register to access your unit details.

Your Unit Details:
- Project: {project_name}
- Floor: {floor_name}
- Unit Number: {unit_number}
- Email: {owner_email}

What You'll Get Access To:
- Unit progress tracking and updates
- Quality inspection reports and SNAG lists
- Direct communication with project teams
- Document and report access
- Project timeline and milestone tracking
- Maintenance request submission

Complete your registration by clicking this link:
{registration_url}

Important: This invitation link is valid for a limited time. Please complete your registration as soon as possible.

If you have any questions, please contact our support team:
Email: support@snagmanagement.com
Phone: +971 50 123 4567

Thank you for choosing SNAG Management System!

SNAG Management System
Quality Assurance & Project Management Platform
            """
            
            # Create message parts
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email, self.password)
                server.sendmail(self.email, owner_email, msg.as_string())
            
            return True
            
        except Exception as e:
            print(f"Error sending unit assignment invitation: {e}")
            return False
    
    def send_welcome_email(self, owner_email, owner_name, unit_number, floor_name, project_name):
        """Send professional welcome email after successful registration"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🎉 Welcome to {project_name} - Unit {unit_number}!"
            msg['From'] = self.email
            msg['To'] = owner_email

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
            background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        .content {{
            padding: 40px 30px;
        }}

        .welcome-text {{
            font-size: 18px;
            margin-bottom: 30px;
            text-align: center;
            color: #2c3e50;
        }}

        .success-box {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 12px;
            padding: 25px;
            margin: 30px 0;
            text-align: center;
        }}

        .success-box h3 {{
            color: #155724;
            margin-bottom: 15px;
            font-size: 20px;
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
            <h1>🎉 Welcome!</h1>
            <p>Registration Successful</p>
        </div>
        
        <div class="content">
            <p class="welcome-text">
                <strong>Dear {owner_name},</strong><br>
                Your registration has been completed successfully! You can now access your unit information and track project progress.
            </p>
            
            <div class="success-box">
                <h3>✅ Registration Complete</h3>
                <p>You are now registered as the owner of Unit {unit_number} in {floor_name}, {project_name}.</p>
            </div>
        </div>
        
        <div class="footer">
            <h3>SNAG Management System</h3>
            <p>Quality Assurance & Project Management Platform</p>
        </div>
    </div>
</body>
</html>
            """
            
            # Text version
            text_content = f"""
Welcome to {project_name}!

Dear {owner_name},

Your registration has been completed successfully! You can now access your unit information and track project progress.

Registration Complete: You are now registered as the owner of Unit {unit_number} in {floor_name}, {project_name}.

Thank you for choosing SNAG Management System!

SNAG Management System
Quality Assurance & Project Management Platform
            """
            
            # Create message parts
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email, self.password)
                server.sendmail(self.email, owner_email, msg.as_string())
            
            return True
            
        except Exception as e:
            print(f"Error sending welcome email: {e}")
            return False

    def send_document_rejection_email(self, owner_email, owner_name, unit_number, floor_name, project_name, document_type, rejection_reason):
        """Send professional document rejection email to owner"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"📋 Document Rejection - {project_name} | {floor_name} - Unit {unit_number}"
            msg['From'] = self.email
            msg['To'] = owner_email

            # HTML version
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Rejection Notice</title>
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
            background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        .content {{
            padding: 40px 30px;
        }}

        .notice-text {{
            font-size: 18px;
            margin-bottom: 30px;
            text-align: center;
            color: #2c3e50;
        }}

        .unit-details {{
            background: #f8f9fa;
            border-radius: 12px;
            padding: 25px;
            margin: 30px 0;
            border-left: 5px solid #dc3545;
        }}

        .unit-details h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 20px;
        }}

        .detail-item {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }}

        .detail-item:last-child {{
            border-bottom: none;
        }}

        .detail-label {{
            font-weight: 600;
            color: #495057;
        }}

        .detail-value {{
            color: #2c3e50;
            font-weight: 500;
        }}

        .rejection-box {{
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 12px;
            padding: 25px;
            margin: 30px 0;
        }}

        .rejection-box h3 {{
            color: #721c24;
            margin-bottom: 15px;
            font-size: 18px;
        }}

        .rejection-reason {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #dc3545;
            color: #495057;
            font-style: italic;
        }}

        .action-box {{
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            border-radius: 12px;
            padding: 25px;
            margin: 30px 0;
            text-align: center;
        }}

        .action-box h3 {{
            color: #0c5460;
            margin-bottom: 15px;
            font-size: 18px;
        }}

        .action-box p {{
            color: #0c5460;
            margin-bottom: 20px;
        }}

        .button-container {{
            text-align: center;
            margin: 40px 0;
        }}

        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
            color: white;
            padding: 18px 40px;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(0, 123, 255, 0.3);
        }}

        .cta-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 123, 255, 0.4);
            color: white;
            text-decoration: none;
        }}

        .footer {{
            background: #2c3e50;
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .footer h3 {{
            margin-bottom: 15px;
            color: #ecf0f1;
        }}

        .footer p {{
            margin-bottom: 10px;
            opacity: 0.8;
        }}

        .footer .contact-info {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #34495e;
        }}

        @media (max-width: 600px) {{
            .email-container {{
                margin: 0;
                border-radius: 0;
            }}

            .header, .content, .footer {{
                padding: 25px 20px;
            }}

            .unit-details, .rejection-box, .action-box {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>📋 Document Rejection</h1>
            <p>SNAG Management System</p>
        </div>

        <div class="content">
            <p class="notice-text">
                <strong>Dear {owner_name},</strong><br>
                Your document submission has been reviewed and requires revision.
            </p>

            <div class="unit-details">
                <h3>📋 Unit Information</h3>
                <div class="detail-item">
                    <span class="detail-label">Project:</span>
                    <span class="detail-value">{project_name}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Floor:</span>
                    <span class="detail-value">{floor_name}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Unit Number:</span>
                    <span class="detail-value">{unit_number}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Document Type:</span>
                    <span class="detail-value">{document_type}</span>
                </div>
            </div>

            <div class="rejection-box">
                <h3>❌ Rejection Details</h3>
                <div class="rejection-reason">
                    {rejection_reason}
                </div>
            </div>

            <div class="action-box">
                <h3>🔄 Next Steps</h3>
                <p>Please review the rejection reason above and re-upload the corrected document through your dashboard.</p>
                <p>Once you upload the revised document, it will be reviewed again by our team.</p>
            </div>

            <div class="button-container">
                <a href="http://127.0.0.1:5000/login" class="cta-button">
                    🚀 Access Dashboard
                </a>
            </div>
        </div>

        <div class="footer">
            <h3>SNAG Management System</h3>
            <p>Quality Assurance & Project Management Platform</p>

            <div class="contact-info">
                <p><strong>Need Help?</strong></p>
                <p>Email: support@snagmanagement.com</p>
                <p>Phone: +971 50 123 4567</p>
            </div>
        </div>
    </div>
</body>
</html>
            """

            # Text version
            text_content = f"""
Document Rejection - {project_name}

Dear {owner_name},

Your document submission has been reviewed and requires revision.

Unit Information:
- Project: {project_name}
- Floor: {floor_name}
- Unit Number: {unit_number}
- Document Type: {document_type}

Rejection Reason:
{rejection_reason}

Next Steps:
Please review the rejection reason above and re-upload the corrected document through your dashboard. Once you upload the revised document, it will be reviewed again by our team.

Access your dashboard: http://127.0.0.1:5000/login

If you have any questions, please contact our support team:
Email: support@snagmanagement.com
Phone: +971 50 123 4567

Thank you for your cooperation.

SNAG Management System
Quality Assurance & Project Management Platform
            """

            # Create message parts
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')

            msg.attach(part1)
            msg.attach(part2)

            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email, self.password)
                server.sendmail(self.email, owner_email, msg.as_string())

            return True

        except Exception as e:
            print(f"Error sending document rejection email: {e}")
            return False

    def send_document_verification_email(self, owner_email, owner_name, unit_number, floor_name, project_name, document_type):
        """Send professional document verification email to owner"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"✅ Document Verified - {project_name} | {floor_name} - Unit {unit_number}"
            msg['From'] = self.email
            msg['To'] = owner_email

            # HTML version
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Verification Confirmation</title>
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
            margin-bottom: 10px;
            font-weight: 700;
        }}

        .content {{
            padding: 40px 30px;
        }}

        .success-text {{
            font-size: 18px;
            margin-bottom: 30px;
            text-align: center;
            color: #2c3e50;
        }}

        .unit-details {{
            background: #f8f9fa;
            border-radius: 12px;
            padding: 25px;
            margin: 30px 0;
            border-left: 5px solid #28a745;
        }}

        .unit-details h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 20px;
        }}

        .detail-item {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }}

        .detail-item:last-child {{
            border-bottom: none;
        }}

        .detail-label {{
            font-weight: 600;
            color: #495057;
        }}

        .detail-value {{
            color: #2c3e50;
            font-weight: 500;
        }}

        .verification-box {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 12px;
            padding: 25px;
            margin: 30px 0;
            text-align: center;
        }}

        .verification-box h3 {{
            color: #155724;
            margin-bottom: 15px;
            font-size: 18px;
        }}

        .verification-box .check-icon {{
            font-size: 48px;
            color: #28a745;
            margin-bottom: 15px;
        }}

        .next-steps {{
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            border-radius: 12px;
            padding: 25px;
            margin: 30px 0;
        }}

        .next-steps h3 {{
            color: #0c5460;
            margin-bottom: 15px;
            font-size: 18px;
        }}

        .next-steps p {{
            color: #0c5460;
            margin-bottom: 10px;
        }}

        .button-container {{
            text-align: center;
            margin: 40px 0;
        }}

        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 18px 40px;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(40, 167, 69, 0.3);
        }}

        .cta-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(40, 167, 69, 0.4);
            color: white;
            text-decoration: none;
        }}

        .footer {{
            background: #2c3e50;
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .footer h3 {{
            margin-bottom: 15px;
            color: #ecf0f1;
        }}

        .footer p {{
            margin-bottom: 10px;
            opacity: 0.8;
        }}

        .footer .contact-info {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #34495e;
        }}

        @media (max-width: 600px) {{
            .email-container {{
                margin: 0;
                border-radius: 0;
            }}

            .header, .content, .footer {{
                padding: 25px 20px;
            }}

            .unit-details, .verification-box, .next-steps {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>✅ Document Verified</h1>
            <p>SNAG Management System</p>
        </div>

        <div class="content">
            <p class="success-text">
                <strong>Dear {owner_name},</strong><br>
                Great news! Your document has been successfully verified.
            </p>

            <div class="unit-details">
                <h3>📋 Unit Information</h3>
                <div class="detail-item">
                    <span class="detail-label">Project:</span>
                    <span class="detail-value">{project_name}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Floor:</span>
                    <span class="detail-value">{floor_name}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Unit Number:</span>
                    <span class="detail-value">{unit_number}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Document Type:</span>
                    <span class="detail-value">{document_type}</span>
                </div>
            </div>

            <div class="verification-box">
                <div class="check-icon">✅</div>
                <h3>Document Verified Successfully</h3>
                <p>Your {document_type} has been reviewed and approved by our verification team.</p>
            </div>

            <div class="next-steps">
                <h3>🎉 What's Next?</h3>
                <p>• Your document is now approved and on file</p>
                <p>• You can access your dashboard to view the verification status</p>
                <p>• If this was your final required document, you now have full access to all features</p>
                <p>• You will receive updates on your unit's progress through the system</p>
            </div>

            <div class="button-container">
                <a href="http://127.0.0.1:5000/login" class="cta-button">
                    🚀 Access Dashboard
                </a>
            </div>
        </div>

        <div class="footer">
            <h3>SNAG Management System</h3>
            <p>Quality Assurance & Project Management Platform</p>

            <div class="contact-info">
                <p><strong>Need Help?</strong></p>
                <p>Email: support@snagmanagement.com</p>
                <p>Phone: +971 50 123 4567</p>
            </div>
        </div>
    </div>
</body>
</html>
            """

            # Text version
            text_content = f"""
Document Verification Confirmation - {project_name}

Dear {owner_name},

Great news! Your document has been successfully verified.

Unit Information:
- Project: {project_name}
- Floor: {floor_name}
- Unit Number: {unit_number}
- Document Type: {document_type}

Document Verified Successfully:
Your {document_type} has been reviewed and approved by our verification team.

What's Next?
• Your document is now approved and on file
• You can access your dashboard to view the verification status
• If this was your final required document, you now have full access to all features
• You will receive updates on your unit's progress through the system

Access your dashboard: http://127.0.0.1:5000/login

If you have any questions, please contact our support team:
Email: support@snagmanagement.com
Phone: +971 50 123 4567

Thank you for your cooperation.

SNAG Management System
Quality Assurance & Project Management Platform
            """

            # Create message parts
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')

            msg.attach(part1)
            msg.attach(part2)

            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email, self.password)
                server.sendmail(self.email, owner_email, msg.as_string())

            return True

        except Exception as e:
            print(f"Error sending document verification email: {e}")
            return False

    def send_all_documents_verified_email(self, owner_email, owner_name, unit_number, floor_name, project_name):
        """Send professional email when all documents are verified and approved"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🎉 All Documents Approved - Welcome to {project_name}!"
            msg['From'] = self.email
            msg['To'] = owner_email

            # HTML version
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>All Documents Approved</title>
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
            margin-bottom: 10px;
            font-weight: 700;
        }}

        .content {{
            padding: 40px 30px;
        }}

        .success-text {{
            font-size: 18px;
            margin-bottom: 30px;
            text-align: center;
            color: #2c3e50;
        }}

        .unit-details {{
            background: #f8f9fa;
            border-radius: 12px;
            padding: 25px;
            margin: 30px 0;
            border-left: 5px solid #28a745;
        }}

        .unit-details h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 20px;
        }}

        .detail-item {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid #e9ecef;
        }}

        .detail-item:last-child {{
            border-bottom: none;
        }}

        .detail-label {{
            font-weight: 600;
            color: #495057;
        }}

        .detail-value {{
            color: #2c3e50;
            font-weight: 500;
        }}

        .success-box {{
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 12px;
            padding: 25px;
            margin: 30px 0;
            text-align: center;
        }}

        .success-box h3 {{
            color: #155724;
            margin-bottom: 15px;
            font-size: 18px;
        }}

        .success-box .check-icon {{
            font-size: 48px;
            color: #28a745;
            margin-bottom: 15px;
        }}

        .features-list {{
            background: #e3f2fd;
            border: 1px solid #bbdefb;
            border-radius: 12px;
            padding: 25px;
            margin: 30px 0;
        }}

        .features-list h3 {{
            color: #0d47a1;
            margin-bottom: 15px;
            font-size: 18px;
        }}

        .features-list ul {{
            list-style: none;
            padding: 0;
        }}

        .features-list li {{
            color: #1565c0;
            margin-bottom: 10px;
            padding-left: 25px;
            position: relative;
        }}

        .features-list li:before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: #28a745;
            font-weight: bold;
        }}

        .button-container {{
            text-align: center;
            margin: 40px 0;
        }}

        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 18px 40px;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(40, 167, 69, 0.3);
        }}

        .cta-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(40, 167, 69, 0.4);
            color: white;
            text-decoration: none;
        }}

        .footer {{
            background: #2c3e50;
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .footer h3 {{
            margin-bottom: 15px;
            color: #ecf0f1;
        }}

        .footer p {{
            margin-bottom: 10px;
            opacity: 0.8;
        }}

        .footer .contact-info {{
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #34495e;
        }}

        @media (max-width: 600px) {{
            .email-container {{
                margin: 0;
                border-radius: 0;
            }}

            .header, .content, .footer {{
                padding: 25px 20px;
            }}

            .unit-details, .success-box, .features-list {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <div class="header">
            <h1>🎉 Congratulations!</h1>
            <p>All Documents Approved</p>
        </div>

        <div class="content">
            <p class="success-text">
                <strong>Dear {owner_name},</strong><br>
                Excellent news! All your documents have been verified and approved. Welcome to your new unit!
            </p>

            <div class="unit-details">
                <h3>🏠 Your Unit Details</h3>
                <div class="detail-item">
                    <span class="detail-label">Project:</span>
                    <span class="detail-value">{project_name}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Floor:</span>
                    <span class="detail-value">{floor_name}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Unit Number:</span>
                    <span class="detail-value">{unit_number}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Status:</span>
                    <span class="detail-value" style="color: #28a745; font-weight: bold;">APPROVED ✓</span>
                </div>
            </div>

            <div class="success-box">
                <div class="check-icon">🎉</div>
                <h3>Verification Complete!</h3>
                <p>Both your Payment Proof and ID Proof have been successfully verified and approved by our team.</p>
            </div>

            <div class="features-list">
                <h3>🚀 What You Can Do Now:</h3>
                <ul>
                    <li>Access your complete dashboard with full features</li>
                    <li>View real-time updates on your unit's progress</li>
                    <li>Track construction milestones and completion status</li>
                    <li>Receive notifications about important project updates</li>
                    <li>Submit and track any maintenance requests</li>
                    <li>Access all project documents and reports</li>
                </ul>
            </div>

            <div class="button-container">
                <a href="http://127.0.0.1:5000/login" class="cta-button">
                    🏠 Access Your Dashboard
                </a>
            </div>
        </div>

        <div class="footer">
            <h3>SNAG Management System</h3>
            <p>Quality Assurance & Project Management Platform</p>

            <div class="contact-info">
                <p><strong>Need Help?</strong></p>
                <p>Email: support@snagmanagement.com</p>
                <p>Phone: +971 50 123 4567</p>
            </div>
        </div>
    </div>
</body>
</html>
            """

            # Text version
            text_content = f"""
Congratulations! All Documents Approved - {project_name}

Dear {owner_name},

Excellent news! All your documents have been verified and approved. Welcome to your new unit!

Your Unit Details:
- Project: {project_name}
- Floor: {floor_name}
- Unit Number: {unit_number}
- Status: APPROVED ✓

Verification Complete!
Both your Payment Proof and ID Proof have been successfully verified and approved by our team.

What You Can Do Now:
• Access your complete dashboard with full features
• View real-time updates on your unit's progress
• Track construction milestones and completion status
• Receive notifications about important project updates
• Submit and track any maintenance requests
• Access all project documents and reports

Access your dashboard: http://127.0.0.1:5000/login

If you have any questions, please contact our support team:
Email: support@snagmanagement.com
Phone: +971 50 123 4567

Thank you for choosing us!

SNAG Management System
Quality Assurance & Project Management Platform
            """

            # Create message parts
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')

            msg.attach(part1)
            msg.attach(part2)

            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.email, self.password)
                server.sendmail(self.email, owner_email, msg.as_string())

            return True

        except Exception as e:
            print(f"Error sending all documents verified email: {e}")
            return False
