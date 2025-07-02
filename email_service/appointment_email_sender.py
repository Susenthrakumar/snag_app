import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class AppointmentEmailSender:
    def __init__(self):
        # SMTP Configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "susenthrakumar@gmail.com"
        self.sender_password = "oytj ipzo vilu qqon"
        self.sender_name = "SNAG Management System"
    
    def send_appointment_confirmation_to_owner(self, owner_email, owner_name, appointment_data, unit_data, inspector_data):
        """Send appointment confirmation email to unit owner"""
        try:
            # Format appointment date
            appointment_date = appointment_data['appointment_date']
            if isinstance(appointment_date, str):
                appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d')
            formatted_date = appointment_date.strftime('%A, %B %d, %Y')
            
            # Email subject
            subject = f"🏠 SNAG Inspection Appointment Confirmed - {unit_data.get('project_name', 'Your Unit')}"
            
            # HTML content
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Appointment Confirmation</title>
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
            background-color: #f4f4f4;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        .content {{
            padding: 30px;
        }}
        .appointment-details {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .detail-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        .detail-label {{
            font-weight: bold;
            color: #555;
        }}
        .detail-value {{
            color: #333;
        }}
        .inspector-info {{
            background: #e8f5e8;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            margin: 20px 0;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏠 Appointment Confirmed</h1>
            <p>Your SNAG inspection has been successfully scheduled</p>
        </div>
        
        <div class="content">
            <p>Dear {owner_name},</p>
            
            <p>Your SNAG inspection appointment has been confirmed. Please find the details below:</p>
            
            <div class="appointment-details">
                <h3>📅 Appointment Details</h3>
                <div class="detail-row">
                    <span class="detail-label">Date:</span>
                    <span class="detail-value">{formatted_date}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Time:</span>
                    <span class="detail-value">{appointment_data['start_time']} - {appointment_data['end_time']}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Status:</span>
                    <span class="detail-value">Confirmed</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Type:</span>
                    <span class="detail-value">SNAG Inspection</span>
                </div>
            </div>
            
            <div class="appointment-details">
                <h3>🏢 Unit Information</h3>
                <div class="detail-row">
                    <span class="detail-label">Project:</span>
                    <span class="detail-value">{unit_data.get('project_name', 'N/A')}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Floor:</span>
                    <span class="detail-value">{unit_data.get('floor_name', 'N/A')}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Unit Number:</span>
                    <span class="detail-value">{unit_data.get('unit_number', 'N/A')}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Unit Size:</span>
                    <span class="detail-value">{unit_data.get('unit_size', 'N/A')}</span>
                </div>
            </div>
            
            <div class="inspector-info">
                <h3>👨‍🔧 Inspector Information</h3>
                <div class="detail-row">
                    <span class="detail-label">Name:</span>
                    <span class="detail-value">{inspector_data.get('name', 'TBA')}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Specialization:</span>
                    <span class="detail-value">{inspector_data.get('specialization', 'SNAG Inspector')}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Phone:</span>
                    <span class="detail-value">{inspector_data.get('phone', 'Will be provided')}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Email:</span>
                    <span class="detail-value">{inspector_data.get('email', 'Will be provided')}</span>
                </div>
            </div>
            
            <p><strong>Important Notes:</strong></p>
            <ul>
                <li>Please ensure someone is available at the unit during the scheduled time</li>
                <li>The inspector will contact you before the appointment</li>
                <li>Please have your unit keys ready</li>
                <li>The inspection typically takes 2-3 hours</li>
            </ul>
            
            <div style="text-align: center;">
                <a href="http://127.0.0.1:5000/owner/appointments" class="cta-button">
                    📱 View Appointment Details
                </a>
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
SNAG Inspection Appointment Confirmed

Dear {owner_name},

Your SNAG inspection appointment has been confirmed. Please find the details below:

Appointment Details:
- Date: {formatted_date}
- Time: {appointment_data['start_time']} - {appointment_data['end_time']}
- Status: Confirmed
- Type: SNAG Inspection

Unit Information:
- Project: {unit_data.get('project_name', 'N/A')}
- Floor: {unit_data.get('floor_name', 'N/A')}
- Unit Number: {unit_data.get('unit_number', 'N/A')}
- Unit Size: {unit_data.get('unit_size', 'N/A')}

Inspector Information:
- Name: {inspector_data.get('name', 'TBA')}
- Specialization: {inspector_data.get('specialization', 'SNAG Inspector')}
- Phone: {inspector_data.get('phone', 'Will be provided')}
- Email: {inspector_data.get('email', 'Will be provided')}

Important Notes:
- Please ensure someone is available at the unit during the scheduled time
- The inspector will contact you before the appointment
- Please have your unit keys ready
- The inspection typically takes 2-3 hours

View appointment details: http://127.0.0.1:5000/owner/appointments

SNAG Management System
Quality Assurance & Project Management Platform
© 2025 All rights reserved
            """
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.sender_name} <{self.sender_email}>"
            message["To"] = owner_email
            
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
                server.sendmail(self.sender_email, owner_email, message.as_string())
            
            print(f"✅ Appointment confirmation email sent to owner: {owner_email}")
            return True, "Appointment confirmation email sent to owner successfully"

        except Exception as e:
            print(f"❌ Error sending appointment confirmation email to owner: {e}")
            return False, f"Failed to send appointment confirmation email to owner: {str(e)}"

    def send_appointment_notification_to_inspector(self, inspector_email, inspector_name, appointment_data, unit_data, owner_data):
        """Send appointment notification email to inspector"""
        try:
            # Format appointment date
            appointment_date = appointment_data['appointment_date']
            if isinstance(appointment_date, str):
                appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d')
            formatted_date = appointment_date.strftime('%A, %B %d, %Y')

            # Email subject
            subject = f"🔍 New SNAG Inspection Assignment - {unit_data.get('project_name', 'Project')} | {formatted_date}"

            # HTML content
            html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>New Inspection Assignment</title>
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
            background-color: #f4f4f4;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        .content {{
            padding: 30px;
        }}
        .assignment-details {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .detail-row {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid #eee;
        }}
        .detail-label {{
            font-weight: bold;
            color: #555;
        }}
        .detail-value {{
            color: #333;
        }}
        .owner-info {{
            background: #e3f2fd;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 12px 30px;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            margin: 20px 0;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 14px;
        }}
        .priority {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 5px;
            padding: 10px;
            margin: 15px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 New Inspection Assignment</h1>
            <p>You have been assigned a new SNAG inspection</p>
        </div>

        <div class="content">
            <p>Dear {inspector_name},</p>

            <p>You have been assigned a new SNAG inspection. Please review the details below and prepare for the scheduled appointment.</p>

            <div class="assignment-details">
                <h3>📅 Inspection Schedule</h3>
                <div class="detail-row">
                    <span class="detail-label">Date:</span>
                    <span class="detail-value">{formatted_date}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Time:</span>
                    <span class="detail-value">{appointment_data['start_time']} - {appointment_data['end_time']}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Type:</span>
                    <span class="detail-value">SNAG Inspection</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Status:</span>
                    <span class="detail-value">Scheduled</span>
                </div>
            </div>

            <div class="assignment-details">
                <h3>🏢 Property Details</h3>
                <div class="detail-row">
                    <span class="detail-label">Project:</span>
                    <span class="detail-value">{unit_data.get('project_name', 'N/A')}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Floor:</span>
                    <span class="detail-value">{unit_data.get('floor_name', 'N/A')}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Unit Number:</span>
                    <span class="detail-value">{unit_data.get('unit_number', 'N/A')}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Unit Size:</span>
                    <span class="detail-value">{unit_data.get('unit_size', 'N/A')}</span>
                </div>
            </div>

            <div class="owner-info">
                <h3>👤 Owner Contact Information</h3>
                <div class="detail-row">
                    <span class="detail-label">Name:</span>
                    <span class="detail-value">{owner_data.get('name', 'N/A')}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Email:</span>
                    <span class="detail-value">{owner_data.get('email', 'N/A')}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Phone:</span>
                    <span class="detail-value">{owner_data.get('phone', 'N/A')}</span>
                </div>
            </div>

            <div class="priority">
                <h4>📋 Pre-Inspection Checklist:</h4>
                <ul>
                    <li>Review unit specifications and floor plans</li>
                    <li>Prepare inspection equipment and tools</li>
                    <li>Contact owner 24 hours before appointment</li>
                    <li>Confirm access arrangements</li>
                    <li>Prepare digital inspection forms</li>
                </ul>
            </div>

            <p><strong>Important Notes:</strong></p>
            <ul>
                <li>Please contact the owner to confirm the appointment</li>
                <li>Arrive 10 minutes early for the inspection</li>
                <li>Bring all necessary inspection equipment</li>
                <li>Document all findings with photos</li>
                <li>Submit the inspection report within 24 hours</li>
            </ul>

            <div style="text-align: center;">
                <a href="http://127.0.0.1:5000/login" class="cta-button">
                    📱 Access Inspector Dashboard
                </a>
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
New SNAG Inspection Assignment

Dear {inspector_name},

You have been assigned a new SNAG inspection. Please review the details below and prepare for the scheduled appointment.

Inspection Schedule:
- Date: {formatted_date}
- Time: {appointment_data['start_time']} - {appointment_data['end_time']}
- Type: SNAG Inspection
- Status: Scheduled

Property Details:
- Project: {unit_data.get('project_name', 'N/A')}
- Floor: {unit_data.get('floor_name', 'N/A')}
- Unit Number: {unit_data.get('unit_number', 'N/A')}
- Unit Size: {unit_data.get('unit_size', 'N/A')}

Owner Contact Information:
- Name: {owner_data.get('name', 'N/A')}
- Email: {owner_data.get('email', 'N/A')}
- Phone: {owner_data.get('phone', 'N/A')}

Pre-Inspection Checklist:
- Review unit specifications and floor plans
- Prepare inspection equipment and tools
- Contact owner 24 hours before appointment
- Confirm access arrangements
- Prepare digital inspection forms

Important Notes:
- Please contact the owner to confirm the appointment
- Arrive 10 minutes early for the inspection
- Bring all necessary inspection equipment
- Document all findings with photos
- Submit the inspection report within 24 hours

Access Inspector Dashboard: http://127.0.0.1:5000/login

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

            print(f"✅ Appointment notification email sent to inspector: {inspector_email}")
            return True, "Appointment notification email sent to inspector successfully"

        except Exception as e:
            print(f"❌ Error sending appointment notification email to inspector: {e}")
            return False, f"Failed to send appointment notification email to inspector: {str(e)}"

    def send_cancellation_email(self, appointment_data, cancellation_reason):
        """Send cancellation email to unit owner"""
        try:
            print(f"🔍 Starting cancellation email to owner...")
            print(f"🔍 Appointment data keys: {list(appointment_data.keys())}")

            # Format appointment details with better error handling
            try:
                if isinstance(appointment_data['appointment_date'], str):
                    from datetime import datetime
                    appointment_date_obj = datetime.strptime(appointment_data['appointment_date'], '%Y-%m-%d')
                    appointment_date = appointment_date_obj.strftime('%B %d, %Y')
                else:
                    appointment_date = appointment_data['appointment_date'].strftime('%B %d, %Y') if appointment_data['appointment_date'] else 'N/A'
            except Exception as date_error:
                print(f"❌ Date formatting error: {date_error}")
                appointment_date = str(appointment_data.get('appointment_date', 'N/A'))

            try:
                if isinstance(appointment_data['start_time'], str):
                    from datetime import datetime
                    start_time_obj = datetime.strptime(appointment_data['start_time'], '%H:%M:%S')
                    start_time = start_time_obj.strftime('%I:%M %p')
                else:
                    start_time = appointment_data['start_time'].strftime('%I:%M %p') if appointment_data['start_time'] else 'N/A'
            except Exception as time_error:
                print(f"❌ Start time formatting error: {time_error}")
                start_time = str(appointment_data.get('start_time', 'N/A'))

            try:
                if isinstance(appointment_data['end_time'], str):
                    from datetime import datetime
                    end_time_obj = datetime.strptime(appointment_data['end_time'], '%H:%M:%S')
                    end_time = end_time_obj.strftime('%I:%M %p')
                else:
                    end_time = appointment_data['end_time'].strftime('%I:%M %p') if appointment_data['end_time'] else 'N/A'
            except Exception as time_error:
                print(f"❌ End time formatting error: {time_error}")
                end_time = str(appointment_data.get('end_time', 'N/A'))

            time_slot = f"{start_time} - {end_time}"
            print(f"🔍 Formatted date: {appointment_date}, time: {time_slot}")

            # Create email content
            subject = f"Appointment Cancelled - {appointment_data.get('project_name', 'N/A')} Unit {appointment_data.get('unit_number', 'N/A')}"

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Appointment Cancelled</title>
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
                        border-radius: 10px;
                        padding: 30px;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    }}
                    .header {{
                        background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
                        color: white;
                        padding: 20px;
                        border-radius: 8px;
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 24px;
                    }}
                    .content {{
                        margin-bottom: 30px;
                    }}
                    .appointment-details {{
                        background: #f8f9fa;
                        border-left: 4px solid #dc3545;
                        padding: 20px;
                        margin: 20px 0;
                        border-radius: 0 8px 8px 0;
                    }}
                    .detail-row {{
                        display: flex;
                        justify-content: space-between;
                        margin-bottom: 10px;
                        padding: 8px 0;
                        border-bottom: 1px solid #e9ecef;
                    }}
                    .detail-label {{
                        font-weight: bold;
                        color: #495057;
                    }}
                    .detail-value {{
                        color: #6c757d;
                    }}
                    .reason-box {{
                        background: #fff3cd;
                        border: 1px solid #ffeaa7;
                        border-radius: 8px;
                        padding: 15px;
                        margin: 20px 0;
                    }}
                    .reason-title {{
                        font-weight: bold;
                        color: #856404;
                        margin-bottom: 10px;
                    }}
                    .reason-text {{
                        color: #856404;
                    }}
                    .action-section {{
                        background: #d1ecf1;
                        border: 1px solid #bee5eb;
                        border-radius: 8px;
                        padding: 20px;
                        margin: 20px 0;
                        text-align: center;
                    }}
                    .action-title {{
                        font-weight: bold;
                        color: #0c5460;
                        margin-bottom: 10px;
                    }}
                    .footer {{
                        text-align: center;
                        color: #6c757d;
                        font-size: 14px;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #e9ecef;
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="header">
                        <h1>🚫 Appointment Cancelled</h1>
                        <p style="margin: 10px 0 0 0;">Better Communities Property Services</p>
                    </div>

                    <div class="content">
                        <p>Dear <strong>{appointment_data['owner_name']}</strong>,</p>

                        <p>We regret to inform you that your scheduled SNAG inspection appointment has been cancelled by our administration team.</p>

                        <div class="appointment-details">
                            <h3 style="margin-top: 0; color: #dc3545;">Cancelled Appointment Details</h3>
                            <div class="detail-row">
                                <span class="detail-label">Project:</span>
                                <span class="detail-value">{appointment_data['project_name']}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Unit:</span>
                                <span class="detail-value">{appointment_data['floor_name']} - Unit {appointment_data['unit_number']}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Date:</span>
                                <span class="detail-value">{appointment_date}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Time:</span>
                                <span class="detail-value">{time_slot}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">Inspector:</span>
                                <span class="detail-value">{appointment_data['inspector_name']}</span>
                            </div>
                        </div>

                        {f'''
                        <div class="reason-box">
                            <div class="reason-title">Cancellation Reason:</div>
                            <div class="reason-text">{cancellation_reason}</div>
                        </div>
                        ''' if cancellation_reason else ''}

                        <div class="action-section">
                            <div class="action-title">📅 Re-booking Available</div>
                            <p>You can now book a new appointment for your SNAG inspection. Please log in to your owner portal to schedule a new appointment at your convenience.</p>
                            <p><strong>Note:</strong> Please ensure to book at least 48 hours in advance.</p>
                        </div>

                        <p>We apologize for any inconvenience caused and appreciate your understanding. If you have any questions or concerns, please don't hesitate to contact our customer service team.</p>
                    </div>

                    <div class="footer">
                        <p><strong>Better Communities Property Services</strong></p>
                        <p>Professional Property Management & Development Solutions</p>
                        <p>This is an automated email. Please do not reply to this message.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.sender_name} <{self.sender_email}>"
            message["To"] = appointment_data['owner_email']

            # Add HTML content
            part = MIMEText(html_content, "html")
            message.attach(part)

            # Send email
            print(f"🔍 Attempting to send email to: {appointment_data.get('owner_email')}")
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                print(f"🔍 Connecting to SMTP server...")
                server.starttls(context=context)
                print(f"🔍 Starting TLS...")
                server.login(self.sender_email, self.sender_password)
                print(f"🔍 Logged in successfully...")
                server.sendmail(self.sender_email, appointment_data['owner_email'], message.as_string())
                print(f"🔍 Email sent successfully...")

            print(f"✅ Cancellation email sent to owner: {appointment_data['owner_email']}")
            return True, "Cancellation email sent successfully"

        except Exception as e:
            print(f"❌ Error sending cancellation email: {e}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            return False, f"Failed to send cancellation email: {str(e)}"

    def send_cancellation_email_to_inspector(self, appointment_data, cancellation_reason):
        """Send cancellation email to inspector"""
        try:
            print(f"🔍 Starting cancellation email to inspector...")
            print(f"🔍 Appointment data keys: {list(appointment_data.keys())}")

            # Format appointment details with better error handling
            try:
                if isinstance(appointment_data['appointment_date'], str):
                    from datetime import datetime
                    appointment_date_obj = datetime.strptime(appointment_data['appointment_date'], '%Y-%m-%d')
                    appointment_date = appointment_date_obj.strftime('%B %d, %Y')
                else:
                    appointment_date = appointment_data['appointment_date'].strftime('%B %d, %Y') if appointment_data['appointment_date'] else 'N/A'
            except Exception as date_error:
                print(f"❌ Date formatting error: {date_error}")
                appointment_date = str(appointment_data.get('appointment_date', 'N/A'))

            try:
                if isinstance(appointment_data['start_time'], str):
                    from datetime import datetime
                    start_time_obj = datetime.strptime(appointment_data['start_time'], '%H:%M:%S')
                    start_time = start_time_obj.strftime('%I:%M %p')
                else:
                    start_time = appointment_data['start_time'].strftime('%I:%M %p') if appointment_data['start_time'] else 'N/A'
            except Exception as time_error:
                print(f"❌ Start time formatting error: {time_error}")
                start_time = str(appointment_data.get('start_time', 'N/A'))

            try:
                if isinstance(appointment_data['end_time'], str):
                    from datetime import datetime
                    end_time_obj = datetime.strptime(appointment_data['end_time'], '%H:%M:%S')
                    end_time = end_time_obj.strftime('%I:%M %p')
                else:
                    end_time = appointment_data['end_time'].strftime('%I:%M %p') if appointment_data['end_time'] else 'N/A'
            except Exception as time_error:
                print(f"❌ End time formatting error: {time_error}")
                end_time = str(appointment_data.get('end_time', 'N/A'))

            time_slot = f"{start_time} - {end_time}"
            print(f"🔍 Formatted date: {appointment_date}, time: {time_slot}")

            # Create email content
            subject = f"Appointment Cancelled - {appointment_data.get('project_name', 'N/A')} Unit {appointment_data.get('unit_number', 'N/A')}"

            # Plain text version
            text_content = f"""
APPOINTMENT CANCELLED

Dear {appointment_data['inspector_name']},

We regret to inform you that the following SNAG inspection appointment has been cancelled by the administration:

APPOINTMENT DETAILS:
- Date: {appointment_date}
- Time: {time_slot}
- Property: {appointment_data['project_name']} - {appointment_data['floor_name']} Unit {appointment_data['unit_number']}
- Unit Owner: {appointment_data['owner_name']}

{f'CANCELLATION REASON: {cancellation_reason}' if cancellation_reason else ''}

This appointment slot is now available for other bookings. You will be notified of any new appointments assigned to you.

If you have any questions, please contact the administration.

Best regards,
Better Communities
SNAG Management System
Quality Assurance & Project Management Platform
© 2025 All rights reserved
            """

            # HTML version
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Appointment Cancelled</title>
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
                        border-radius: 15px;
                        overflow: hidden;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                    }}
                    .header {{
                        background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
                        color: white;
                        padding: 30px;
                        text-align: center;
                    }}
                    .header h1 {{
                        margin: 0;
                        font-size: 28px;
                        font-weight: 600;
                    }}
                    .content {{
                        padding: 40px 30px;
                    }}
                    .greeting {{
                        font-size: 18px;
                        margin-bottom: 25px;
                        color: #2c3e50;
                    }}
                    .message {{
                        font-size: 16px;
                        margin-bottom: 30px;
                        line-height: 1.8;
                    }}
                    .details-section {{
                        background: #f8f9fa;
                        border-radius: 12px;
                        padding: 25px;
                        margin: 25px 0;
                        border-left: 5px solid #dc3545;
                    }}
                    .details-title {{
                        font-size: 18px;
                        font-weight: 600;
                        color: #dc3545;
                        margin-bottom: 20px;
                        display: flex;
                        align-items: center;
                    }}
                    .detail-row {{
                        display: flex;
                        justify-content: space-between;
                        margin-bottom: 12px;
                        padding: 8px 0;
                        border-bottom: 1px solid #e9ecef;
                    }}
                    .detail-row:last-child {{
                        border-bottom: none;
                        margin-bottom: 0;
                    }}
                    .detail-label {{
                        font-weight: 600;
                        color: #495057;
                        flex: 1;
                    }}
                    .detail-value {{
                        color: #212529;
                        flex: 2;
                        text-align: right;
                    }}
                    .reason-box {{
                        background: #fff3cd;
                        border: 1px solid #ffeaa7;
                        border-radius: 8px;
                        padding: 20px;
                        margin: 20px 0;
                    }}
                    .reason-title {{
                        font-weight: 600;
                        color: #856404;
                        margin-bottom: 10px;
                    }}
                    .reason-text {{
                        color: #856404;
                        font-style: italic;
                    }}
                    .footer {{
                        background: #2c3e50;
                        color: white;
                        padding: 25px;
                        text-align: center;
                        font-size: 14px;
                    }}
                    .footer-title {{
                        font-size: 18px;
                        font-weight: 600;
                        margin-bottom: 10px;
                    }}
                    .footer-subtitle {{
                        color: #bdc3c7;
                        margin-bottom: 15px;
                    }}
                </style>
            </head>
            <body>
                <div class="email-container">
                    <div class="header">
                        <h1>🚫 Appointment Cancelled</h1>
                    </div>

                    <div class="content">
                        <div class="greeting">
                            Dear {appointment_data['inspector_name']},
                        </div>

                        <div class="message">
                            We regret to inform you that the following SNAG inspection appointment has been <strong>cancelled by the administration</strong>. This appointment slot is now available for other bookings.
                        </div>

                        <div class="details-section">
                            <div class="details-title">
                                📋 Cancelled Appointment Details
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">📅 Date:</span>
                                <span class="detail-value">{appointment_date}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">⏰ Time:</span>
                                <span class="detail-value">{time_slot}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">🏢 Property:</span>
                                <span class="detail-value">{appointment_data['project_name']}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">🏠 Unit:</span>
                                <span class="detail-value">{appointment_data['floor_name']} Unit {appointment_data['unit_number']}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">👤 Unit Owner:</span>
                                <span class="detail-value">{appointment_data['owner_name']}</span>
                            </div>
                        </div>

                        {f'''
                        <div class="reason-box">
                            <div class="reason-title">Cancellation Reason:</div>
                            <div class="reason-text">{cancellation_reason}</div>
                        </div>
                        ''' if cancellation_reason else ''}

                        <div class="message">
                            You will be notified of any new appointments assigned to you. If you have any questions regarding this cancellation, please contact the administration.
                        </div>
                    </div>

                    <div class="footer">
                        <div class="footer-title">Better Communities</div>
                        <div class="footer-subtitle">SNAG Management System</div>
                        <div>Quality Assurance & Project Management Platform</div>
                        <div style="margin-top: 10px; color: #95a5a6;">© 2025 All rights reserved</div>
                    </div>
                </div>
            </body>
            </html>
            """

            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.sender_name} <{self.sender_email}>"
            message["To"] = appointment_data['inspector_email']

            # Add both versions
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")

            message.attach(part1)
            message.attach(part2)

            # Send email
            print(f"🔍 Attempting to send email to inspector: {appointment_data.get('inspector_email')}")
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                print(f"🔍 Connecting to SMTP server...")
                server.starttls(context=context)
                print(f"🔍 Starting TLS...")
                server.login(self.sender_email, self.sender_password)
                print(f"🔍 Logged in successfully...")
                server.sendmail(self.sender_email, appointment_data['inspector_email'], message.as_string())
                print(f"🔍 Email sent successfully...")

            print(f"✅ Cancellation email sent to inspector: {appointment_data['inspector_email']}")
            return True, "Cancellation email sent to inspector successfully"

        except Exception as e:
            print(f"❌ Error sending cancellation email to inspector: {e}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            return False, f"Failed to send cancellation email to inspector: {str(e)}"


# Global functions for easy import
def send_appointment_emails(owner_email, owner_name, appointment_data, unit_data, inspector_data):
    """Send appointment confirmation emails to both owner and inspector"""
    sender = AppointmentEmailSender()

    # Send to owner
    owner_result = sender.send_appointment_confirmation_to_owner(
        owner_email, owner_name, appointment_data, unit_data, inspector_data
    )

    # Send to inspector
    inspector_result = sender.send_appointment_notification_to_inspector(
        inspector_data.get('email'), inspector_data.get('name'),
        appointment_data, unit_data, {'name': owner_name, 'email': owner_email, 'phone': unit_data.get('owner_phone')}
    )

    return owner_result[0] and inspector_result[0], f"Owner: {owner_result[1]}, Inspector: {inspector_result[1]}"

def send_cancellation_email(appointment_data, cancellation_reason):
    """Send cancellation email to unit owner"""
    sender = AppointmentEmailSender()
    return sender.send_cancellation_email(appointment_data, cancellation_reason)
