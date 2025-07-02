import smtplib
import ssl
import secrets
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailSender:
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
    
    def send_contractor_invitation(self, contractor_email, registration_token, base_url="http://127.0.0.1:5000"):
        """Send professional invitation email to contractor"""
        try:
            # Registration URL
            registration_url = f"{base_url}/contractors/register?token={registration_token}&email={contractor_email}"
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "🎯 You're Invited to Join SNAG Management System"
            msg['From'] = self.email
            msg['To'] = contractor_email
            
            # HTML version with professional design
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SNAG Management System Invitation</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }}
        
        .container {{
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
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
        
        .invitation-card {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            text-align: center;
            margin: 30px 0;
        }}
        
        .invitation-card h2 {{
            font-size: 24px;
            margin-bottom: 15px;
        }}
        
        .invitation-card p {{
            font-size: 16px;
            opacity: 0.9;
            margin-bottom: 25px;
        }}
        
        .register-btn {{
            display: inline-block;
            background-color: #ffffff;
            color: #f5576c;
            padding: 15px 35px;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }}
        
        .register-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        }}
        
        .features {{
            margin: 30px 0;
        }}
        
        .features h3 {{
            color: #2c3e50;
            font-size: 20px;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .feature-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .feature-item {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        
        .feature-item h4 {{
            color: #2c3e50;
            font-size: 16px;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
        }}
        
        .feature-item p {{
            color: #6c757d;
            font-size: 14px;
        }}
        
        .feature-icon {{
            margin-right: 8px;
            font-size: 18px;
        }}
        
        .expiry-notice {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 8px;
            margin: 25px 0;
            text-align: center;
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
        
        .social-links {{
            margin: 20px 0;
        }}
        
        .social-links a {{
            color: white;
            text-decoration: none;
            margin: 0 10px;
            opacity: 0.8;
        }}
        
        @media (max-width: 600px) {{
            .container {{
                margin: 10px;
                border-radius: 8px;
            }}
            
            .header, .content, .footer {{
                padding: 20px;
            }}
            
            .header h1 {{
                font-size: 24px;
            }}
            
            .invitation-card {{
                padding: 20px;
            }}
            
            .feature-grid {{
                grid-template-columns: 1fr;
            }}
            
            .register-btn {{
                padding: 12px 25px;
                font-size: 14px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 SNAG Management System</h1>
            <p>Professional Project Management Platform</p>
        </div>
        
        <div class="content">
            <p class="welcome-text">Hello there! 👋</p>
            
            <div class="invitation-card">
                <h2>You're Invited!</h2>
                <p>Join our professional SNAG Management System as a contractor and take your project management to the next level.</p>
                <a href="{registration_url}" class="register-btn">Register Now</a>
            </div>
            
            <div class="features">
                <h3>🚀 What You'll Get Access To:</h3>
                <div class="feature-grid">
                    <div class="feature-item">
                        <h4><span class="feature-icon">📋</span>Project Management</h4>
                        <p>View and manage your assigned projects with advanced tools and real-time updates.</p>
                    </div>
                    <div class="feature-item">
                        <h4><span class="feature-icon">✅</span>Task Tracking</h4>
                        <p>Track progress, update task status, and collaborate seamlessly with your team.</p>
                    </div>
                    <div class="feature-item">
                        <h4><span class="feature-icon">💬</span>Communication Hub</h4>
                        <p>Connect with team members and clients through integrated communication tools.</p>
                    </div>
                    <div class="feature-item">
                        <h4><span class="feature-icon">📊</span>Analytics & Reports</h4>
                        <p>Access detailed project reports and analytics to optimize your workflow.</p>
                    </div>
                </div>
            </div>
            
            <div class="expiry-notice">
                <strong>⏰ Important:</strong> This invitation link will expire in 7 days. Please register soon!
            </div>
        </div>
        
        <div class="footer">
            <p><strong>SNAG Management Team</strong></p>
            <p>Professional Project Management Solutions</p>
            <div class="social-links">
                <a href="#">📧 Support</a>
                <a href="#">🌐 Website</a>
                <a href="#">📱 Mobile App</a>
            </div>
            <p style="font-size: 12px; margin-top: 20px;">
                This email was sent to {contractor_email}<br>
                If you didn't expect this invitation, you can safely ignore this email.
            </p>
        </div>
    </div>
</body>
</html>
"""
            
            # Plain text version
            text_content = f"""
SNAG Management System - Contractor Invitation

Hello!

You have been invited to join our professional SNAG Management System as a contractor.

REGISTER NOW: {registration_url}

What you'll get access to:
• Project Management - View and manage your assigned projects
• Task Tracking - Track progress and update task status  
• Communication Hub - Collaborate with team members and clients
• Analytics & Reports - View detailed project reports

IMPORTANT: This invitation link will expire in 7 days.

If you have any questions, please contact our support team.

Best regards,
SNAG Management Team

---
This email was sent to {contractor_email}
If you didn't expect this invitation, you can safely ignore this email.
"""
            
            # Create text and HTML parts
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
            
            return True, "Professional invitation email sent successfully"
            
        except Exception as e:
            return False, f"Failed to send invitation email: {str(e)}"
    
    def send_welcome_email(self, contractor_email, contractor_name):
        """Send professional welcome email after successful registration"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🎉 Welcome to SNAG Management System, {contractor_name}!"
            msg['From'] = self.email
            msg['To'] = contractor_email
            
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }}
        
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        
        .header {{
            background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
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
        
        .welcome-badge {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            text-align: center;
            margin: 30px 0;
        }}
        
        .welcome-badge h2 {{
            font-size: 24px;
            margin-bottom: 15px;
        }}
        
        .welcome-badge p {{
            font-size: 16px;
            opacity: 0.9;
        }}
        
        .login-btn {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 35px;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            font-size: 16px;
            margin: 20px 0;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }}
        
        .login-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
        }}
        
        .next-steps {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 8px;
            margin: 25px 0;
        }}
        
        .next-steps h3 {{
            color: #2c3e50;
            font-size: 18px;
            margin-bottom: 15px;
        }}
        
        .step {{
            display: flex;
            align-items: flex-start;
            margin: 15px 0;
        }}
        
        .step-number {{
            background: #667eea;
            color: white;
            width: 25px;
            height: 25px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 12px;
            margin-right: 15px;
            flex-shrink: 0;
        }}
        
        .step-content {{
            flex: 1;
        }}
        
        .step-content h4 {{
            color: #2c3e50;
            font-size: 16px;
            margin-bottom: 5px;
        }}
        
        .step-content p {{
            color: #6c757d;
            font-size: 14px;
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
        
        .contact-info {{
            background: #e8f4fd;
            border-left: 4px solid #007bff;
            padding: 20px;
            margin: 25px 0;
        }}
        
        .contact-info h4 {{
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .contact-info p {{
            color: #6c757d;
            margin: 5px 0;
        }}
        
        @media (max-width: 600px) {{
            .container {{
                margin: 10px;
                border-radius: 8px;
            }}
            
            .header, .content, .footer {{
                padding: 20px;
            }}
            
            .header h1 {{
                font-size: 24px;
            }}
            
            .welcome-badge {{
                padding: 20px;
            }}
            
            .login-btn {{
                padding: 12px 25px;
                font-size: 14px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Welcome to SNAG!</h1>
            <p>Your account is ready to go</p>
        </div>
        
        <div class="content">
            <div class="welcome-badge">
                <h2>Hello {contractor_name}! 👋</h2>
                <p>Your contractor account has been successfully created and is now active. You're all set to start managing projects like a pro!</p>
            </div>
            
            <div style="text-align: center;">
                <a href="http://127.0.0.1:5000/login" class="login-btn">Access Your Dashboard</a>
            </div>
            
            <div class="next-steps">
                <h3>🚀 Next Steps:</h3>
                
                <div class="step">
                    <div class="step-number">1</div>
                    <div class="step-content">
                        <h4>Complete Your Profile</h4>
                        <p>Add your professional details, skills, and preferences to get better project matches.</p>
                    </div>
                </div>
                
                <div class="step">
                    <div class="step-number">2</div>
                    <div class="step-content">
                        <h4>Explore Your Dashboard</h4>
                        <p>Familiarize yourself with the project management tools and features available.</p>
                    </div>
                </div>
                
                <div class="step">
                    <div class="step-number">3</div>
                    <div class="step-content">
                        <h4>Start Your First Project</h4>
                        <p>Once assigned, you can begin tracking tasks and collaborating with your team.</p>
                    </div>
                </div>
            </div>
            
            <div class="contact-info">
                <h4>📞 Need Help Getting Started?</h4>
                <p>📧 Email: support@snagmanagement.com</p>
                <p>💬 Live Chat: Available in your dashboard</p>
                <p>📚 Documentation: Complete guides and tutorials available</p>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>SNAG Management Team</strong></p>
            <p>Professional Project Management Solutions</p>
            <p style="font-size: 12px; margin-top: 20px;">
                Welcome aboard, {contractor_name}! We're excited to have you on our team.
            </p>
        </div>
    </div>
</body>
</html>
"""
            
            # Plain text version
            text_content = f"""
Welcome to SNAG Management System!

Hello {contractor_name}!

Your contractor account has been successfully created and is now active.

ACCESS YOUR DASHBOARD: http://127.0.0.1:5000/login

Next Steps:
1. Complete Your Profile - Add your professional details and skills
2. Explore Your Dashboard - Get familiar with the tools and features  
3. Start Your First Project - Begin tracking tasks and collaborating

Need Help?
- Email: support@snagmanagement.com
- Live Chat: Available in your dashboard
- Documentation: Complete guides available

Welcome aboard! We're excited to have you on our team.

Best regards,
SNAG Management Team
"""
            
            # Create text and HTML parts
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
            
            return True, "Professional welcome email sent successfully"
            
        except Exception as e:
            return False, f"Failed to send welcome email: {str(e)}"

