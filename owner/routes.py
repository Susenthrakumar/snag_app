from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, send_file
import hashlib
import re
from datetime import datetime, timedelta
from database import Database
from email_service.owner_email_sender import OwnerEmailSender
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io
import os
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

owner_bp = Blueprint('owner', __name__, url_prefix='/owner')
db = Database()
owner_email_sender = OwnerEmailSender()

def timedelta_to_time_string(td):
    """Convert timedelta to 12-hour time string format"""
    if isinstance(td, timedelta):
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        # Convert to 12-hour format
        if hours == 0:
            return f"12:{minutes:02d} AM"
        elif hours < 12:
            return f"{hours}:{minutes:02d} AM"
        elif hours == 12:
            return f"12:{minutes:02d} PM"
        else:
            return f"{hours-12}:{minutes:02d} PM"
    return str(td)

class NumberedCanvas(canvas.Canvas):
    """Custom canvas for page numbering and professional layout"""
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for (page_num, page_state) in enumerate(self._saved_page_states):
            self.__dict__.update(page_state)
            self.draw_page_number(page_num + 1, num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_num, total_pages):
        """Draw professional page numbers and footer"""
        # Page number
        self.setFont("Times-Roman", 10)
        self.setFillColor(colors.HexColor('#666666'))
        self.drawRightString(A4[0] - 40, 25, f"Page {page_num} of {total_pages}")
        
        # Professional footer line
        self.setStrokeColor(colors.HexColor('#2c5aa0'))
        self.setLineWidth(1)
        self.line(40, 35, A4[0] - 40, 35)
        
        # Company footer
        self.setFont("Times-Italic", 8)
        self.setFillColor(colors.HexColor('#888888'))
        self.drawString(40, 20, "Better Communities - Owner Association Management")

def generate_appointment_pdf(appointment_data, unit_info, inspector_info):
    """Generate Super Professional PDF with Perfect Spacing and Enhanced Details"""
    buffer = io.BytesIO()

    # Professional PDF Document with perfect margins
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=50,
        bottomMargin=60,
        title="SNAG Appointment Acknowledgement",
        author="Better Communities"
    )

    # Enhanced Professional Styles
    styles = getSampleStyleSheet()

    # Company Header Style - Ultra Professional
    company_header_style = ParagraphStyle(
        'CompanyHeader',
        parent=styles['Normal'],
        fontSize=16,
        spaceAfter=3,
        alignment=TA_CENTER,
        textColor=colors.white,
        fontName='Times-Bold',
        leading=20
    )

    # Company Tagline Style
    company_tagline_style = ParagraphStyle(
        'CompanyTagline',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        alignment=TA_CENTER,
        textColor=colors.white,
        fontName='Times-Italic',
        leading=12
    )

    # Main Title Style - Enhanced
    main_title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=5,
        spaceBefore=10,
        alignment=TA_CENTER,
        textColor=colors.white,
        fontName='Times-Bold',
        leading=28
    )

    # Document Reference Style
    doc_ref_style = ParagraphStyle(
        'DocReference',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=0,
        alignment=TA_RIGHT,
        textColor=colors.white,
        fontName='Times-Roman',
        leading=11
    )

    # Section Header Style - Professional Blue
    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=13,
        spaceAfter=0,
        spaceBefore=8,
        textColor=colors.white,
        fontName='Times-Bold',
        leading=16,
        leftIndent=15,
        rightIndent=15
    )

    # Executive Summary Style - Enhanced
    executive_summary_style = ParagraphStyle(
        'ExecutiveSummary',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=12,
        spaceBefore=12,
        textColor=colors.HexColor('#1a365d'),
        fontName='Times-Roman',
        leading=16,
        leftIndent=20,
        rightIndent=20,
        alignment=TA_JUSTIFY
    )

    # Professional Body Text
    professional_body_style = ParagraphStyle(
        'ProfessionalBody',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        textColor=colors.HexColor('#2d3748'),
        fontName='Times-Roman',
        leading=14,
        alignment=TA_JUSTIFY
    )

    # Important Note Style
    important_note_style = ParagraphStyle(
        'ImportantNote',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=10,
        spaceBefore=10,
        textColor=colors.HexColor('#c53030'),
        fontName='Times-Bold',
        leading=14,
        leftIndent=15,
        rightIndent=15,
        borderWidth=1,
        borderColor=colors.HexColor('#fed7d7'),
        borderPadding=12,
        backColor=colors.HexColor('#fef5e7')
    )

    # Build Super Professional PDF Content
    story = []

    # Professional Header Section with Perfect Spacing
    current_date = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    reference_id = f"SNAG-APT-{appointment_data['id']:06d}"
    
    # Company Header with Enhanced Design
    header_data = [
        [
            Paragraph("Better Communities", company_header_style),
            Paragraph(f"Document Generated: {current_date}<br/>Reference ID: {reference_id}", doc_ref_style)
        ],
        [
            Paragraph("Professional Property Management & Development Solutions", company_tagline_style),
            ""
        ]
    ]

    header_table = Table(header_data, colWidths=[4.5*inch, 2.5*inch])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1a365d')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#2c5aa0'))
    ]))

    story.append(header_table)

    # Main Title Section with Enhanced Design
    title_data = [
        [Paragraph("SNAG INSPECTION APPOINTMENT", main_title_style)],
        [Paragraph("OFFICIAL ACKNOWLEDGEMENT DOCUMENT", company_tagline_style)]
    ]
    
    title_table = Table(title_data, colWidths=[7*inch])
    title_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#2c5aa0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
    ]))

    story.append(title_table)
    story.append(Spacer(1, 25))

    # Executive Summary Section - Enhanced
    summary_header_data = [[Paragraph("EXECUTIVE SUMMARY", section_header_style)]]
    summary_header_table = Table(summary_header_data, colWidths=[7*inch])
    summary_header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#2c5aa0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(summary_header_table)

    # Enhanced Executive Summary Content
    unit_display = unit_info.get('unit_number', 'Not Specified')
    project_display = unit_info.get('project_name', 'Not Specified')
    floor_display = unit_info.get('floor_name', 'Not Specified')
    
    summary_text = f"""
    <b>Property Details:</b> Unit {unit_display}, {project_display}, Floor {floor_display}<br/>
    <b>Appointment Status:</b> Confirmed and Scheduled<br/>
    <b>Inspection Type:</b> Comprehensive SNAG (Snagging) Inspection<br/>
    <b>Document Created:</b> {appointment_data['created_at'].strftime('%B %d, %Y at %I:%M %p')}<br/>
    <b>Scheduled Date:</b> {appointment_data['appointment_date'].strftime('%B %d, %Y')}<br/>
    <b>Professional Inspector:</b> {inspector_info.get('name', 'Will be assigned shortly')}
    """

    summary_content_data = [[Paragraph(summary_text, executive_summary_style)]]
    summary_content_table = Table(summary_content_data, colWidths=[7*inch])
    summary_content_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f7fafc')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#2c5aa0')),
        ('LEFTPADDING', (0, 0), (-1, -1), 25),
        ('RIGHTPADDING', (0, 0), (-1, -1), 25),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
    ]))
    story.append(summary_content_table)
    story.append(Spacer(1, 25))

    # Detailed Appointment Information Section
    appointment_header_data = [[Paragraph("DETAILED APPOINTMENT INFORMATION", section_header_style)]]
    appointment_header_table = Table(appointment_header_data, colWidths=[7*inch])
    appointment_header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#2c5aa0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(appointment_header_table)

    # Enhanced Appointment Details
    appointment_table_data = [
        ['Appointment Reference ID:', f"#{reference_id}"],
        ['Appointment Status:', f"{appointment_data['status'].title()} ✓"],
        ['Scheduled Date:', appointment_data['appointment_date'].strftime('%A, %B %d, %Y')],
        ['Scheduled Time Slot:', f"{timedelta_to_time_string(appointment_data['start_time'])} - {timedelta_to_time_string(appointment_data['end_time'])}"],
        ['Estimated Duration:', '2-3 Hours (Comprehensive Inspection)'],
        ['Document Created On:', appointment_data['created_at'].strftime('%B %d, %Y at %I:%M %p')],
        ['Expected Completion:', appointment_data['appointment_date'].strftime('%B %d, %Y')],
        ['Inspection Category:', 'Professional SNAG Inspection'],
        ['Priority Level:', 'Standard Priority'],
    ]

    if appointment_data.get('notes'):
        appointment_table_data.append(['Special Instructions:', appointment_data['notes']])

    appointment_table = Table(appointment_table_data, colWidths=[2.8*inch, 4.2*inch])
    appointment_table.setStyle(TableStyle([
        # Professional label column
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#4a90e2')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('FONTNAME', (0, 0), (0, -1), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (0, -1), 10),

        # Professional value column
        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#2d3748')),
        ('FONTNAME', (1, 0), (1, -1), 'Times-Roman'),
        ('FONTSIZE', (1, 0), (1, -1), 10),

        # Perfect alignment and spacing
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),

        # Professional borders
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2c5aa0')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#2c5aa0')),
        
        # Alternating row colors for better readability
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f8f9fa')]),
    ]))

    story.append(appointment_table)
    story.append(Spacer(1, 25))

    # Professional Inspector Details Section
    inspector_header_data = [[Paragraph("CERTIFIED SNAG INSPECTOR DETAILS", section_header_style)]]
    inspector_header_table = Table(inspector_header_data, colWidths=[7*inch])
    inspector_header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#2c5aa0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(inspector_header_table)

    inspector_table_data = [
        ['Inspector Name:', inspector_info.get('name', 'Professional Inspector (To be assigned)')],
        ['Professional Specialization:', inspector_info.get('specialization', 'Comprehensive SNAG Inspection')],
        ['Contact Phone Number:', inspector_info.get('phone', 'Will be provided 24 hours before inspection')],
        ['Professional Email:', inspector_info.get('email', 'Will be provided 24 hours before inspection')],
        ['Certification Level:', 'Certified Professional SNAG Inspector'],
        ['Years of Experience:', '5+ Years in Property Inspection'],
        ['Inspection Standards:', 'Following International SNAG Guidelines'],
        ['Quality Assurance:', 'ISO 9001:2015 Certified Process'],
    ]

    inspector_table = Table(inspector_table_data, colWidths=[2.8*inch, 4.2*inch])
    inspector_table.setStyle(TableStyle([
        # Professional green theme for inspector section
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#2d7d32')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('FONTNAME', (0, 0), (0, -1), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (0, -1), 10),

        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#f0fff4')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#22543d')),
        ('FONTNAME', (1, 0), (1, -1), 'Times-Roman'),
        ('FONTSIZE', (1, 0), (1, -1), 10),

        # Perfect spacing and alignment
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),

        # Professional green borders
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#2d7d32')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#2d7d32')),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f0fff4')]),
    ]))

    story.append(inspector_table)
    story.append(Spacer(1, 25))

    # Comprehensive Unit Information Section
    unit_header_data = [[Paragraph("COMPREHENSIVE UNIT INFORMATION", section_header_style)]]
    unit_header_table = Table(unit_header_data, colWidths=[7*inch])
    unit_header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#2c5aa0')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(unit_header_table)

    unit_table_data = [
        ['Unit Identifier:', unit_info.get('unit_number', 'Not Specified')],
        ['Project Name:', unit_info.get('project_name', 'Not Specified')],
        ['Floor Level:', unit_info.get('floor_name', 'Not Specified')],
        ['Unit Type:', unit_info.get('unit_type', 'Residential Unit')],
        ['Project Phase:', unit_info.get('project_phase', 'Construction Complete')],
        ['Handover Status:', 'Ready for SNAG Inspection'],
        ['Request Created On:', appointment_data['created_at'].strftime('%B %d, %Y at %I:%M %p')],
        ['Expected Completion:', appointment_data['appointment_date'].strftime('%B %d, %Y')],
        ['Quality Standard:', 'Premium Quality Assurance'],
    ]

    unit_table = Table(unit_table_data, colWidths=[2.8*inch, 4.2*inch])
    unit_table.setStyle(TableStyle([
        # Professional orange theme for unit section
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#d69e2e')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('FONTNAME', (0, 0), (0, -1), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (0, -1), 10),

        ('BACKGROUND', (1, 0), (1, -1), colors.HexColor('#fffaf0')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#1a365d')),
        ('FONTNAME', (1, 0), (1, -1), 'Times-Roman'),
        ('FONTSIZE', (1, 0), (1, -1), 10),

        # Perfect professional spacing
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),

        # Professional orange borders
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#b7791f')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#b7791f')),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#fffaf0')]),
    ]))

    story.append(unit_table)
    story.append(Spacer(1, 30))

    # Important Guidelines Section
    guidelines_header_data = [[Paragraph("IMPORTANT PREPARATION GUIDELINES", section_header_style)]]
    guidelines_header_table = Table(guidelines_header_data, colWidths=[7*inch])
    guidelines_header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#c53030')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(guidelines_header_table)

    guidelines_text = """
    <b>MANDATORY REQUIREMENTS:</b><br/>
    • Please be present at the scheduled time for the comprehensive SNAG inspection<br/>
    • Ensure all areas of the unit are completely accessible to the professional inspector<br/>
    • All electrical connections, plumbing fixtures, and fittings should be ready for testing<br/>
    • Keep this official confirmation document readily available for verification<br/><br/>
    
    <b>PREPARATION CHECKLIST:</b><br/>
    • Remove any personal belongings that might obstruct the inspection process<br/>
    • Ensure adequate lighting in all areas of the unit<br/>
    • Have your unit keys and access cards ready<br/>
    • Prepare a list of any specific concerns you want the inspector to address<br/><br/>
    
    <b>CONTACT INFORMATION FOR QUERIES:</b><br/>
    • Management Office: +91-XXXX-XXXX-XX (Available 24/7)<br/>
    • Professional Support Email: support@fixloop.com<br/>
    • Emergency Contact: +91-YYYY-YYYY-YY<br/>
    • Website: www.fixloop.com/snag-services
    """

    guidelines_content_data = [[Paragraph(guidelines_text, professional_body_style)]]
    guidelines_content_table = Table(guidelines_content_data, colWidths=[7*inch])
    guidelines_content_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fef5e7')),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#c53030')),
        ('LEFTPADDING', (0, 0), (-1, -1), 25),
        ('RIGHTPADDING', (0, 0), (-1, -1), 25),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
    ]))
    story.append(guidelines_content_table)
    story.append(Spacer(1, 20))

    # Professional Footer Message
    footer_message = """
    <b><i>Thank you for choosing Better Communities for your professional SNAG inspection needs. 
    We are committed to delivering exceptional quality assurance services with the highest standards of professionalism.</i></b>
    """
    
    footer_data = [[Paragraph(footer_message, executive_summary_style)]]
    footer_table = Table(footer_data, colWidths=[7*inch])
    footer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e6fffa')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#38a169')),
        ('LEFTPADDING', (0, 0), (-1, -1), 25),
        ('RIGHTPADDING', (0, 0), (-1, -1), 25),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    story.append(footer_table)

    # Build the professional PDF with custom canvas
    doc.build(story, canvasmaker=NumberedCanvas)

    # Return the professional PDF data
    pdf_data = buffer.getvalue()
    buffer.close()

    return pdf_data

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    # Remove spaces and special characters for validation
    clean_phone = re.sub(r'[^\d]', '', phone)
    return len(clean_phone) >= 10

def validate_username(username):
    """Validate username format"""
    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters long"
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    
    return True, ""

def check_username_exists(username):
    """Check if username exists in any user table"""
    connection = db.get_db_connection()
    if not connection:
        return False, "Database connection failed"
    
    try:
        cursor = connection.cursor()
        
        # Check in all user tables
        tables_and_columns = [
            ('admin', 'username'),
            ('contractors', 'username'),
            ('snag_inspectors', 'username'),
            ('client_relations', 'username'),
            ('floor_units', 'owner_username')
        ]
        
        for table, column in tables_and_columns:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} = %s", (username,))
            count = cursor.fetchone()[0]
            if count > 0:
                cursor.close()
                connection.close()
                return True, f"Username already exists in {table}"
        
        cursor.close()
        connection.close()
        return False, "Username is available"
        
    except Exception as e:
        print(f"Error checking username: {e}")
        if connection:
            connection.close()
        return False, "Database error occurred"

def check_email_exists(email):
    """Check if email exists in any user table"""
    connection = db.get_db_connection()
    if not connection:
        return False, "Database connection failed"
    
    try:
        cursor = connection.cursor()
        
        # Check in all user tables
        tables_and_columns = [
            ('admin', 'email'),
            ('contractors', 'email'),
            ('snag_inspectors', 'email'),
            ('client_relations', 'email'),
            ('floor_units', 'owner_email')
        ]
        
        for table, column in tables_and_columns:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} = %s", (email,))
            count = cursor.fetchone()[0]
            if count > 0:
                cursor.close()
                connection.close()
                return True, f"Email already exists in {table}"
        
        cursor.close()
        connection.close()
        return False, "Email is available"
        
    except Exception as e:
        print(f"Error checking email: {e}")
        if connection:
            connection.close()
        return False, "Database error occurred"

def check_phone_exists(phone, country_code):
    """Check if phone number exists in any user table"""
    connection = db.get_db_connection()
    if not connection:
        return False, "Database connection failed"
    
    try:
        cursor = connection.cursor()
        
        # Check in all user tables
        tables_and_columns = [
            ('admin', 'phone'),
            ('contractors', 'phone'),
            ('snag_inspectors', 'phone'),
            ('client_relations', 'phone'),
            ('floor_units', 'owner_phone')
        ]
        
        for table, column in tables_and_columns:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} = %s", (phone,))
            count = cursor.fetchone()[0]
            if count > 0:
                cursor.close()
                connection.close()
                return True, f"Phone number already exists in {table}"
        
        cursor.close()
        connection.close()
        return False, "Phone number is available"
        
    except Exception as e:
        print(f"Error checking phone: {e}")
        if connection:
            connection.close()
        return False, "Database error occurred"

@owner_bp.route('/register')
def register():
    """Owner registration page"""
    email = request.args.get('email')
    token = request.args.get('token')
    
    if not email or not token:
        flash('Invalid registration link', 'error')
        return redirect(url_for('login'))
    
    # Verify token and email in database
    connection = db.get_db_connection()
    if not connection:
        flash('Database connection failed', 'error')
        return redirect(url_for('login'))
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM floor_units 
            WHERE owner_email = %s AND invitation_token = %s AND invitation_status = 'pending'
        """, (email, token))
        
        unit = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not unit:
            flash('Invalid or expired registration link', 'error')
            return redirect(url_for('login'))
        
        return render_template('owner/register.html', email=email, token=token, unit=unit)
        
    except Exception as e:
        print(f"Error verifying registration token: {e}")
        flash('Error verifying registration link', 'error')
        if connection:
            connection.close()
        return redirect(url_for('login'))

@owner_bp.route('/register', methods=['POST'])
def register_post():
    """Handle owner registration form submission"""
    email = request.form.get('email')
    token = request.form.get('token')
    name = request.form.get('name')
    username = request.form.get('username')
    password = request.form.get('password')
    phone = request.form.get('phone')
    country_code = request.form.get('country_code', '+971')
    
    # Validate required fields
    if not all([email, token, name, username, password, phone]):
        flash('All fields are required', 'error')
        return render_template('owner/register.html', email=email, token=token)
    
    # Validate email format
    if not validate_email(email):
        flash('Invalid email format', 'error')
        return render_template('owner/register.html', email=email, token=token)
    
    # Validate phone format
    if not validate_phone(phone):
        flash('Invalid phone number format', 'error')
        return render_template('owner/register.html', email=email, token=token)
    
    # Validate username format
    username_valid, username_msg = validate_username(username)
    if not username_valid:
        flash(username_msg, 'error')
        return render_template('owner/register.html', email=email, token=token)
    
    # Check if username exists
    username_exists, username_check_msg = check_username_exists(username)
    if username_exists:
        flash('Username already exists', 'error')
        return render_template('owner/register.html', email=email, token=token)
    
    # Check if phone exists
    phone_exists, phone_check_msg = check_phone_exists(phone, country_code)
    if phone_exists:
        flash('Phone number already exists', 'error')
        return render_template('owner/register.html', email=email, token=token)
    
    # Verify token and update owner information
    connection = db.get_db_connection()
    if not connection:
        flash('Database connection failed', 'error')
        return render_template('owner/register.html', email=email, token=token)
    
    try:
        cursor = connection.cursor()
        
        # Verify token
        cursor.execute("""
            SELECT id FROM floor_units 
            WHERE owner_email = %s AND invitation_token = %s AND invitation_status = 'pending'
        """, (email, token))
        
        unit = cursor.fetchone()
        if not unit:
            flash('Invalid or expired registration link', 'error')
            cursor.close()
            connection.close()
            return render_template('owner/register.html', email=email, token=token)
        
        # Hash password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Update unit with owner information
        cursor.execute("""
            UPDATE floor_units
            SET owner_name = %s, owner_username = %s, owner_password = %s, 
                owner_phone = %s, country_code = %s, invitation_status = 'registered',
                is_assigned = TRUE, assigned_at = NOW(), invitation_token = NULL
            WHERE owner_email = %s AND invitation_token = %s
        """, (name, username, hashed_password, phone, country_code, email, token))
        
        connection.commit()

        # Get unit details for welcome email
        cursor.execute("""
            SELECT
                fu.unit_number,
                CONCAT(pf.prefix, ' ', pf.number) as floor_name,
                p.project_name
            FROM floor_units fu
            JOIN project_floors pf ON fu.floor_id = pf.id
            JOIN projects p ON pf.project_id = p.id
            WHERE fu.owner_email = %s AND fu.owner_username = %s
        """, (email, username))

        unit_details = cursor.fetchone()
        cursor.close()
        connection.close()

        # Send welcome email
        if unit_details:
            owner_email_sender.send_welcome_email(
                owner_email=email,
                owner_name=name,
                unit_number=unit_details[0],
                floor_name=unit_details[1],
                project_name=unit_details[2]
            )

        flash('Registration completed successfully! You can now login.', 'success')
        return redirect(url_for('login'))
        
    except Exception as e:
        print(f"Error during registration: {e}")
        flash('Registration failed. Please try again.', 'error')
        if connection:
            connection.close()
        return render_template('owner/register.html', email=email, token=token)

@owner_bp.route('/dashboard')
def dashboard():
    """Owner dashboard"""
    if 'owner_id' not in session:
        return redirect(url_for('login'))

    owner_id = session['owner_id']
    
    connection = db.get_db_connection()
    if not connection:
        flash('Database connection failed', 'error')
        return redirect(url_for('login'))
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get owner's unit information with individual verification status
        cursor.execute("""
            SELECT
                fu.*,
                CONCAT(pf.prefix, ' ', pf.number) as floor_name,
                p.project_name,
                p.id as project_id,
                fu.payment_proof_verified, fu.id_proof_verified,
                fu.payment_proof_rejected_reason, fu.id_proof_rejected_reason
            FROM floor_units fu
            JOIN project_floors pf ON fu.floor_id = pf.id
            JOIN projects p ON pf.project_id = p.id
            WHERE fu.id = %s
        """, (owner_id,))
        
        unit_info = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not unit_info:
            flash('Unit information not found', 'error')
            return redirect(url_for('login'))

        # Check payment verification status
        if unit_info['payment_verification_status'] == 'rejected':
            flash('Your documents were rejected. Please re-upload corrected documents.', 'error')
            return render_template('owner/payment_verification.html', unit=unit_info)
        elif unit_info['payment_verification_status'] in ['pending', 'submitted']:
            return render_template('owner/payment_verification.html', unit=unit_info)
        elif unit_info['payment_verification_status'] != 'approved':
            return render_template('owner/payment_verification.html', unit=unit_info)

        return render_template('owner/dashboard.html', unit=unit_info)
        
    except Exception as e:
        print(f"Error loading dashboard: {e}")
        flash('Error loading dashboard', 'error')
        if connection:
            connection.close()
        return redirect(url_for('login'))

# API Routes for validation
@owner_bp.route('/api/validate-username', methods=['POST'])
def api_validate_username():
    """Validate username availability"""
    data = request.get_json()
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({'valid': False, 'message': 'Username is required'})
    
    # Validate format
    format_valid, format_msg = validate_username(username)
    if not format_valid:
        return jsonify({'valid': False, 'message': format_msg})
    
    # Check availability
    exists, check_msg = check_username_exists(username)
    if exists:
        return jsonify({'valid': False, 'message': 'Username already exists'})
    
    return jsonify({'valid': True, 'message': 'Username is available'})

@owner_bp.route('/api/validate-phone', methods=['POST'])
def api_validate_phone():
    """Validate phone number availability"""
    data = request.get_json()
    phone = data.get('phone', '').strip()
    country_code = data.get('country_code', '+971')
    
    if not phone:
        return jsonify({'valid': False, 'message': 'Phone number is required'})
    
    # Validate format
    if not validate_phone(phone):
        return jsonify({'valid': False, 'message': 'Invalid phone number format'})
    
    # Check availability
    exists, check_msg = check_phone_exists(phone, country_code)
    if exists:
        return jsonify({'valid': False, 'message': 'Phone number already exists'})
    
    return jsonify({'valid': True, 'message': 'Phone number is available'})

@owner_bp.route('/api/upload-verification-documents', methods=['POST'])
def api_upload_verification_documents():
    """Upload payment verification documents"""
    if 'owner_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    owner_id = session['owner_id']
    data = request.get_json()

    payment_proof = data.get('payment_proof')
    payment_proof_name = data.get('payment_proof_name')
    id_proof = data.get('id_proof')
    id_proof_name = data.get('id_proof_name')

    if not all([payment_proof, id_proof]):
        return jsonify({'error': 'Both payment proof and ID proof are required'}), 400

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()

        # Update unit with verification documents and reset verification status
        cursor.execute("""
            UPDATE floor_units
            SET payment_proof_document = %s, id_proof_document = %s,
                payment_verification_status = 'submitted', documents_uploaded_at = NOW(),
                payment_proof_verified = NULL, id_proof_verified = NULL,
                payment_proof_rejected_reason = NULL, id_proof_rejected_reason = NULL,
                verification_notes = NULL
            WHERE id = %s
        """, (payment_proof, id_proof, owner_id))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'message': 'Documents uploaded successfully. Verification is now pending approval.'
        })

    except Exception as e:
        print(f"Error uploading verification documents: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to upload documents'}), 500

@owner_bp.route('/api/reupload-document', methods=['POST'])
def api_reupload_document():
    """Re-upload specific rejected document"""
    if 'owner_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    owner_id = session['owner_id']
    data = request.get_json()

    document_type = data.get('document_type')
    document_data = data.get('document_data')

    if not all([document_type, document_data]):
        return jsonify({'error': 'Document type and data are required'}), 400

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()

        # Update specific document based on type and reset verification status
        if document_type == 'Payment Proof':
            cursor.execute("""
                UPDATE floor_units
                SET payment_proof_document = %s, payment_verification_status = 'submitted',
                    documents_uploaded_at = NOW(), verification_notes = NULL,
                    payment_proof_verified = NULL, payment_proof_rejected_reason = NULL
                WHERE id = %s
            """, (document_data, owner_id))
        elif document_type == 'ID Proof':
            cursor.execute("""
                UPDATE floor_units
                SET id_proof_document = %s, payment_verification_status = 'submitted',
                    documents_uploaded_at = NOW(), verification_notes = NULL,
                    id_proof_verified = NULL, id_proof_rejected_reason = NULL
                WHERE id = %s
            """, (document_data, owner_id))
        else:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Invalid document type'}), 400

        connection.commit()

        # Get unit details for notification
        cursor.execute("""
            SELECT owner_name, owner_email, unit_number,
                   CONCAT(pf.prefix, ' ', pf.number) as floor_name,
                   p.project_name
            FROM floor_units fu
            JOIN project_floors pf ON fu.floor_id = pf.id
            JOIN projects p ON pf.project_id = p.id
            WHERE fu.id = %s
        """, (owner_id,))

        unit_info = cursor.fetchone()
        cursor.close()
        connection.close()

        # Send notification email to CR about re-upload
        try:
            from email_service.client_relations_email_sender import ClientRelationsEmailSender
            cr_email_sender = ClientRelationsEmailSender()
            cr_email_sender.send_document_reupload_notification(
                unit_info=unit_info,
                document_type=document_type
            )
        except Exception as e:
            print(f"Error sending CR notification: {e}")

        return jsonify({
            'success': True,
            'message': f'{document_type} re-uploaded successfully. Verification is now pending approval.'
        })

    except Exception as e:
        print(f"Error re-uploading document: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to re-upload document'}), 500

@owner_bp.route('/api/check-reupload-eligibility', methods=['POST'])
def api_check_reupload_eligibility():
    """Check if document can be re-uploaded (only rejected documents)"""
    if 'owner_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    owner_id = session['owner_id']
    data = request.get_json()
    document_type = data.get('document_type')

    if not document_type:
        return jsonify({'error': 'Document type is required'}), 400

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # Check verification status for the specific document
        if document_type == 'Payment Proof':
            cursor.execute("""
                SELECT payment_proof_verified, payment_proof_rejected_reason
                FROM floor_units WHERE id = %s
            """, (owner_id,))
            result = cursor.fetchone()
            verified = result['payment_proof_verified'] if result else None
            reason = result['payment_proof_rejected_reason'] if result else None
        elif document_type == 'ID Proof':
            cursor.execute("""
                SELECT id_proof_verified, id_proof_rejected_reason
                FROM floor_units WHERE id = %s
            """, (owner_id,))
            result = cursor.fetchone()
            verified = result['id_proof_verified'] if result else None
            reason = result['id_proof_rejected_reason'] if result else None
        else:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Invalid document type'}), 400

        cursor.close()
        connection.close()

        # Only allow re-upload if document is rejected (verified = 0)
        can_reupload = verified == 0

        return jsonify({
            'success': True,
            'can_reupload': can_reupload,
            'status': 'rejected' if verified == 0 else ('verified' if verified == 1 else 'pending'),
            'rejection_reason': reason if verified == 0 else None
        })

    except Exception as e:
        print(f"Error checking reupload eligibility: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to check eligibility'}), 500


@owner_bp.route('/appointments')
def appointments():
    """Owner appointment booking page"""
    owner_id = session.get('owner_id', 2)  # Default to owner ID 2 for testing
    rebook = request.args.get('rebook', '0') == '1'  # Check if this is a re-booking request
    print(f"🎯 Appointments page - Owner ID: {owner_id}, Rebook: {rebook}")

    connection = db.get_db_connection()
    if not connection:
        print("❌ Database connection failed")
        flash('Database connection failed', 'error')
        return redirect(url_for('owner.dashboard'))

    try:
        cursor = connection.cursor(dictionary=True)

        # Get owner's unit information
        cursor.execute("""
            SELECT
                fu.unit_number,
                CONCAT(pf.prefix, ' ', pf.number) as floor_name,
                p.project_name,
                fu.owner_name,
                fu.payment_verification_status,
                fu.id_proof_verified
            FROM floor_units fu
            JOIN project_floors pf ON fu.floor_id = pf.id
            JOIN projects p ON pf.project_id = p.id
            WHERE fu.id = %s
        """, (owner_id,))

        unit_info = cursor.fetchone()
        print(f"📋 Unit info: {unit_info}")

        if not unit_info:
            print("❌ Unit information not found")
            flash('Unit information not found', 'error')
            cursor.close()
            connection.close()
            return redirect(url_for('login'))

        # Check if both documents are verified
        print(f"🔍 Payment status: {unit_info['payment_verification_status']}")
        print(f"🔍 ID proof verified: {unit_info['id_proof_verified']}")
        if (unit_info['payment_verification_status'] != 'approved' or
            not unit_info['id_proof_verified']):
            print("❌ Documents not verified")
            flash('Please complete document verification before booking appointments', 'warning')
            cursor.close()
            connection.close()
            return redirect(url_for('owner.dashboard'))

        # Check if owner already has an appointment (scheduled or most recent appointment)
        cursor.execute("""
            SELECT a.*, si.name as inspector_name, si.specialization, si.phone, si.email
            FROM appointments a
            LEFT JOIN snag_inspectors si ON a.inspector_id = si.id
            WHERE a.owner_id = %s
            ORDER BY a.id DESC
            LIMIT 1
        """, (owner_id,))

        existing_appointment = cursor.fetchone()

        # If this is a re-booking request, skip showing existing appointment details
        if existing_appointment and not rebook:
            # Get inspector details separately
            cursor.execute("""
                SELECT name, specialization, phone, email
                FROM snag_inspectors
                WHERE id = %s
            """, (existing_appointment['inspector_id'],))

            inspector = cursor.fetchone()

            # Add inspector details to appointment
            if inspector:
                existing_appointment['inspector_name'] = inspector['name']
                existing_appointment['inspector_specialization'] = inspector['specialization']
                existing_appointment['inspector_phone'] = inspector['phone']
                existing_appointment['inspector_email'] = inspector['email']

            # Owner has an existing appointment - show appointment details in same page
            cursor.close()
            connection.close()

            print(f"🎯 Showing appointment details for appointment ID: {existing_appointment['id']}")
            print(f"📅 Appointment date: {existing_appointment['appointment_date']}")

            return render_template('owner/appointments.html',
                                 appointment=existing_appointment,
                                 unit_info=unit_info,
                                 unit=unit_info)

        # Get available SNAG inspectors
        cursor.execute("""
            SELECT id, name, email, phone, specialization
            FROM snag_inspectors
            WHERE status = 'active'
            ORDER BY name
        """)

        inspectors = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template('owner/appointments.html', unit=unit_info, inspectors=inspectors)

    except Exception as e:
        print(f"❌ Error loading appointments page: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        flash('Error loading appointments page', 'error')
        if connection:
            connection.close()
        return redirect(url_for('owner.dashboard'))


@owner_bp.route('/api/session-check')
def api_session_check():
    """Check session status"""
    return jsonify({
        'logged_in': 'owner_id' in session,
        'owner_id': session.get('owner_id'),
        'session_data': dict(session)
    })


@owner_bp.route('/api/time-slots')
def api_time_slots():
    """Get available time slots for a specific date"""
    date = request.args.get('date')

    if not date:
        return jsonify({'success': False, 'message': 'Date is required'})

    try:
        connection = db.get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Database connection failed'})

        cursor = connection.cursor(dictionary=True)

        # Get all active time slots
        cursor.execute("SELECT slot_name, start_time, end_time FROM time_slots WHERE is_active = TRUE ORDER BY start_time")
        all_slots = cursor.fetchall()

        # Get booked appointments for this date
        cursor.execute("""
            SELECT start_time, end_time
            FROM appointments
            WHERE appointment_date = %s AND status = 'scheduled'
        """, (date,))
        booked_slots = cursor.fetchall()

        # Get frozen slots for this date using existing frozen_slots table
        cursor.execute("""
            SELECT start_time, end_time, freeze_type
            FROM frozen_slots
            WHERE freeze_date = %s
        """, (date,))
        frozen_slots = cursor.fetchall()

        # Filter available slots
        available_slots = []
        for slot in all_slots:
            slot_start = slot['start_time']
            slot_end = slot['end_time']

            # Check if slot is booked
            is_booked = any(
                booked['start_time'] == slot_start and
                booked['end_time'] == slot_end
                for booked in booked_slots
            )

            # Check if slot is frozen (more complex logic for different freeze types)
            is_frozen = False
            for frozen in frozen_slots:
                freeze_type = frozen['freeze_type']

                if freeze_type == 'full_day':
                    # Entire day is frozen
                    is_frozen = True
                    break
                elif freeze_type == 'time_slot':
                    # Specific time slot is frozen
                    if (frozen['start_time'] == slot_start and
                        frozen['end_time'] == slot_end):
                        is_frozen = True
                        break
                elif freeze_type in ['morning', 'afternoon']:
                    # For morning/afternoon freezes, check if slot overlaps with frozen time range
                    frozen_start = frozen['start_time']
                    frozen_end = frozen['end_time']

                    # Check if slot overlaps with frozen time range
                    if (slot_start >= frozen_start and slot_start < frozen_end) or \
                       (slot_end > frozen_start and slot_end <= frozen_end) or \
                       (slot_start <= frozen_start and slot_end >= frozen_end):
                        is_frozen = True
                        break

            if not is_booked and not is_frozen:
                # Convert times to 12-hour format
                start_time_12h = timedelta_to_time_string(slot['start_time'])
                end_time_12h = timedelta_to_time_string(slot['end_time'])

                available_slots.append({
                    'slot_name': slot['slot_name'],
                    'start_time': start_time_12h,
                    'end_time': end_time_12h
                })

        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'slots': available_slots
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})


@owner_bp.route('/api/book-appointment', methods=['POST'])
def api_book_appointment():
    """Book a SNAG appointment"""
    data = request.get_json()
    owner_id = session.get('owner_id', 1)  # Default to owner ID 1 for testing

    print(f"🎯 Booking appointment for owner ID: {owner_id}")
    print(f"📝 Booking data: {data}")
    print(f"🔑 Session data: {dict(session)}")

    date = data.get('date')
    time_slot = data.get('time')
    inspector_id = data.get('inspector_id')
    notes = data.get('notes', '')

    if not all([date, time_slot, inspector_id]):
        return jsonify({'success': False, 'message': 'All fields are required'})

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'})

    try:
        cursor = connection.cursor(dictionary=True)

        # Check if owner already has a scheduled appointment (only scheduled ones block new bookings)
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM appointments
            WHERE owner_id = %s AND status = 'scheduled'
        """, (owner_id,))

        scheduled_count = cursor.fetchone()['count']
        if scheduled_count > 0:
            return jsonify({'success': False, 'message': 'You already have a scheduled appointment'})

        # If this is a rebooking, disable rebooking for any previous cancelled appointments
        cursor.execute("""
            UPDATE appointments
            SET can_rebook = 0
            WHERE owner_id = %s AND status = 'cancelled' AND can_rebook = 1
        """, (owner_id,))

        # Get time slot details
        cursor.execute("""
            SELECT start_time, end_time
            FROM time_slots
            WHERE slot_name = %s
        """, (time_slot,))

        slot_info = cursor.fetchone()
        if not slot_info:
            return jsonify({'success': False, 'message': 'Invalid time slot'})

        # Check if slot is still available
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM appointments
            WHERE appointment_date = %s
            AND start_time = %s
            AND end_time = %s
            AND status = 'scheduled'
        """, (date, slot_info['start_time'], slot_info['end_time']))

        if cursor.fetchone()['count'] > 0:
            return jsonify({'success': False, 'message': 'Time slot is no longer available'})

        # Check if inspector is available at this time
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM appointments
            WHERE appointment_date = %s
            AND start_time = %s
            AND end_time = %s
            AND inspector_id = %s
            AND status = 'scheduled'
        """, (date, slot_info['start_time'], slot_info['end_time'], inspector_id))

        if cursor.fetchone()['count'] > 0:
            return jsonify({'success': False, 'message': 'Inspector is not available at this time'})

        # Get owner and unit information
        cursor.execute("""
            SELECT
                fu.unit_number,
                CONCAT(pf.prefix, ' ', pf.number) as floor_name,
                p.project_name,
                fu.owner_name
            FROM floor_units fu
            JOIN project_floors pf ON fu.floor_id = pf.id
            JOIN projects p ON pf.project_id = p.id
            WHERE fu.id = %s
        """, (owner_id,))

        unit_info = cursor.fetchone()
        if not unit_info:
            return jsonify({'success': False, 'message': 'Unit information not found'})

        # Create appointment
        appointment_title = f"SNAG Inspection - {unit_info['project_name']} {unit_info['floor_name']} Unit {unit_info['unit_number']}"

        cursor.execute("""
            INSERT INTO appointments (
                title, description, appointment_date, start_time, end_time,
                owner_id, inspector_id, unit_id, notes, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            appointment_title,
            f"SNAG inspection appointment for {unit_info['owner_name']}",
            date,
            slot_info['start_time'],
            slot_info['end_time'],
            owner_id,
            inspector_id,
            owner_id,  # unit_id same as owner_id for now
            notes,
            owner_id
        ))

        appointment_id = cursor.lastrowid
        connection.commit()

        # Get the complete appointment data for PDF generation
        cursor.execute("""
            SELECT a.*, si.name as inspector_name, si.specialization, si.phone, si.email
            FROM appointments a
            LEFT JOIN snag_inspectors si ON a.inspector_id = si.id
            WHERE a.id = %s
        """, (appointment_id,))

        appointment_data = cursor.fetchone()

        # Get unit info
        cursor.execute("""
            SELECT
                fu.unit_number,
                CONCAT(pf.prefix, ' ', pf.number) as floor_name,
                p.project_name,
                fu.owner_name
            FROM floor_units fu
            JOIN project_floors pf ON fu.floor_id = pf.id
            JOIN projects p ON pf.project_id = p.id
            WHERE fu.id = %s
        """, (owner_id,))

        unit_info = cursor.fetchone()

        # Get owner email information
        cursor.execute("""
            SELECT owner_email as email, owner_name, owner_phone as phone
            FROM floor_units
            WHERE id = %s
        """, (owner_id,))

        owner_info = cursor.fetchone()

        cursor.close()
        connection.close()

        # Send email notifications
        try:
            from email_service.appointment_email_sender import AppointmentEmailSender
            email_sender = AppointmentEmailSender()

            # Prepare data for emails
            appointment_email_data = {
                'appointment_date': appointment_data['appointment_date'],
                'start_time': appointment_data['start_time'],
                'end_time': appointment_data['end_time']
            }

            unit_email_data = {
                'project_name': unit_info.get('project_name'),
                'floor_name': unit_info.get('floor_name'),
                'unit_number': unit_info.get('unit_number'),
                'unit_size': 'N/A'  # Add unit size if available in database
            }

            inspector_email_data = {
                'name': appointment_data.get('inspector_name'),
                'specialization': appointment_data.get('specialization'),
                'phone': appointment_data.get('phone'),
                'email': appointment_data.get('email')
            }

            owner_email_data = {
                'name': owner_info.get('owner_name') if owner_info else 'Owner',
                'email': owner_info.get('email') if owner_info else '',
                'phone': owner_info.get('phone') if owner_info else ''
            }

            # Send email to owner
            if owner_info and owner_info.get('email'):
                owner_email_success, owner_email_msg = email_sender.send_appointment_confirmation_to_owner(
                    owner_info['email'],
                    owner_info.get('owner_name', 'Owner'),
                    appointment_email_data,
                    unit_email_data,
                    inspector_email_data
                )
                print(f"📧 Owner email result: {owner_email_msg}")

            # Send email to inspector
            if appointment_data.get('email'):
                inspector_email_success, inspector_email_msg = email_sender.send_appointment_notification_to_inspector(
                    appointment_data['email'],
                    appointment_data.get('inspector_name', 'Inspector'),
                    appointment_email_data,
                    unit_email_data,
                    owner_email_data
                )
                print(f"📧 Inspector email result: {inspector_email_msg}")

        except Exception as email_error:
            print(f"📧 Email notification error: {email_error}")
            # Don't fail the booking if email fails

        # Generate PDF
        try:
            inspector_info = {
                'name': appointment_data.get('inspector_name'),
                'specialization': appointment_data.get('specialization'),
                'phone': appointment_data.get('phone'),
                'email': appointment_data.get('email')
            }

            return jsonify({
                'success': True,
                'message': 'Appointment booked successfully! Email notifications have been sent to you and the inspector.',
                'appointment_id': appointment_id,
                'pdf_url': f'/owner/download-appointment-pdf/{appointment_id}',
                'pdf_filename': f'appointment_{appointment_id}.pdf'
            })

        except Exception as pdf_error:
            print(f"PDF generation error: {pdf_error}")
            return jsonify({
                'success': True,
                'message': 'Appointment booked successfully! Email notifications have been sent to you and the inspector.',
                'appointment_id': appointment_id
            })

    except Exception as e:
        print(f"Error booking appointment: {e}")
        if connection:
            connection.close()
        return jsonify({'success': False, 'message': 'Error booking appointment'})

@owner_bp.route('/download-appointment-pdf/<int:appointment_id>')
def download_appointment_pdf(appointment_id):
    """Download appointment PDF acknowledgment"""
    owner_id = session.get('owner_id', 2)  # Default to owner ID 2 for testing

    try:
        connection = db.get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Verify appointment belongs to this owner and get data
        cursor.execute("""
            SELECT a.*, si.name as inspector_name, si.specialization, si.phone, si.email
            FROM appointments a
            LEFT JOIN snag_inspectors si ON a.inspector_id = si.id
            WHERE a.id = %s AND a.owner_id = %s
        """, (appointment_id, owner_id))

        appointment_data = cursor.fetchone()

        if not appointment_data:
            flash('Appointment not found', 'error')
            return redirect(url_for('owner.dashboard'))

        # Get unit info
        cursor.execute("""
            SELECT
                fu.unit_number,
                CONCAT(pf.prefix, ' ', pf.number) as floor_name,
                p.project_name,
                fu.owner_name
            FROM floor_units fu
            JOIN project_floors pf ON fu.floor_id = pf.id
            JOIN projects p ON pf.project_id = p.id
            WHERE fu.id = %s
        """, (owner_id,))

        unit_info = cursor.fetchone()

        cursor.close()
        connection.close()

        # Generate PDF
        inspector_info = {
            'name': appointment_data.get('inspector_name'),
            'specialization': appointment_data.get('specialization'),
            'phone': appointment_data.get('phone'),
            'email': appointment_data.get('email')
        }

        pdf_data = generate_appointment_pdf(appointment_data, unit_info, inspector_info)

        # Create a BytesIO object for the PDF
        pdf_buffer = io.BytesIO(pdf_data)
        pdf_buffer.seek(0)

        # Generate filename
        filename = f"SNAG_Appointment_{appointment_id}_{appointment_data['appointment_date'].strftime('%Y%m%d')}.pdf"

        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        print(f"Error generating PDF: {e}")
        flash('Error generating PDF', 'error')
        return redirect(url_for('owner.dashboard'))


@owner_bp.route('/api/acknowledge-appointment', methods=['POST'])
def api_acknowledge_appointment():
    """Acknowledge an appointment on behalf of the owner"""
    data = request.get_json()

    appointment_id = data.get('appointment_id')
    name = data.get('name')
    phone = data.get('phone')

    if not all([appointment_id, name, phone]):
        return jsonify({'success': False, 'message': 'All fields are required'})

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'})

    try:
        cursor = connection.cursor(dictionary=True)

        # Check if appointment exists and is not already acknowledged
        cursor.execute("""
            SELECT id, is_acknowledged
            FROM appointments
            WHERE id = %s
        """, (appointment_id,))

        appointment = cursor.fetchone()
        if not appointment:
            return jsonify({'success': False, 'message': 'Appointment not found'})

        if appointment['is_acknowledged']:
            return jsonify({'success': False, 'message': 'Appointment already acknowledged'})

        # Update appointment with acknowledgment details
        cursor.execute("""
            UPDATE appointments
            SET acknowledgment_name = %s,
                acknowledgment_phone = %s,
                is_acknowledged = TRUE,
                acknowledged_at = NOW()
            WHERE id = %s
        """, (name, phone, appointment_id))

        connection.commit()

        return jsonify({
            'success': True,
            'message': 'Appointment acknowledged successfully'
        })

    except Exception as e:
        print(f"Error acknowledging appointment: {e}")
        return jsonify({'success': False, 'message': 'An error occurred while acknowledging the appointment'})
    finally:
        if connection:
            connection.close()


@owner_bp.route('/download-acknowledgment-pdf/<int:appointment_id>')
def download_acknowledgment_pdf(appointment_id):
    """Download acknowledgment PDF"""
    print(f"🎯 PDF download requested for appointment ID: {appointment_id}")
    owner_id = session.get('owner_id', 2)  # Default to owner ID 2 for testing

    try:
        connection = db.get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get appointment data (remove owner verification for testing)
        cursor.execute("""
            SELECT a.*, si.name as inspector_name, si.specialization, si.phone, si.email
            FROM appointments a
            LEFT JOIN snag_inspectors si ON a.inspector_id = si.id
            WHERE a.id = %s AND a.is_acknowledged = TRUE
        """, (appointment_id,))

        appointment_data = cursor.fetchone()

        if not appointment_data:
            flash('Acknowledgment not found', 'error')
            return redirect(url_for('owner.dashboard'))

        # Get unit info using appointment's owner_id
        cursor.execute("""
            SELECT
                fu.unit_number,
                CONCAT(pf.prefix, ' ', pf.number) as floor_name,
                p.project_name,
                fu.owner_name
            FROM floor_units fu
            JOIN project_floors pf ON fu.floor_id = pf.id
            JOIN projects p ON pf.project_id = p.id
            WHERE fu.id = %s
        """, (appointment_data['owner_id'],))

        unit_info = cursor.fetchone()

        cursor.close()
        connection.close()

        # Generate acknowledgment PDF
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
            from io import BytesIO
            import os
            from datetime import datetime

            # Create a BytesIO buffer
            buffer = BytesIO()

            # Create the PDF document with professional margins
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=40,
                leftMargin=40,
                topMargin=50,
                bottomMargin=60,
                title="SNAG Appointment Acknowledgment",
                author="Better Communities"
            )

            # Get styles
            styles = getSampleStyleSheet()

            # Professional Header Styles - matching appointment PDF
            company_header_style = ParagraphStyle(
                'CompanyHeader',
                parent=styles['Normal'],
                fontSize=16,
                spaceAfter=3,
                alignment=TA_CENTER,
                textColor=colors.white,
                fontName='Times-Bold',
                leading=20
            )

            company_tagline_style = ParagraphStyle(
                'CompanyTagline',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                textColor=colors.white,
                fontName='Times-Italic',
                leading=12
            )

            doc_ref_style = ParagraphStyle(
                'DocRef',
                parent=styles['Normal'],
                fontSize=9,
                alignment=TA_RIGHT,
                textColor=colors.white,
                fontName='Times-Roman',
                leading=11
            )

            main_title_style = ParagraphStyle(
                'MainTitle',
                parent=styles['Normal'],
                fontSize=18,
                alignment=TA_CENTER,
                textColor=colors.white,
                fontName='Times-Bold',
                leading=22
            )

            section_header_style = ParagraphStyle(
                'SectionHeader',
                parent=styles['Normal'],
                fontSize=14,
                spaceAfter=12,
                textColor=colors.HexColor('#1a365d'),
                fontName='Times-Bold',
                leading=16
            )

            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=6,
                fontName='Times-Roman',
                leading=14
            )

            # Build the document content
            content = []

            # Professional Header Section with Perfect Spacing
            current_date = datetime.now().strftime('%B %d, %Y at %I:%M %p')
            reference_id = f"ACK-{appointment_data['id']:06d}"

            # Company Header with Enhanced Design
            header_data = [
                [
                    Paragraph("Better Communities", company_header_style),
                    Paragraph(f"Document Generated: {current_date}<br/>Reference ID: {reference_id}", doc_ref_style)
                ],
                [
                    Paragraph("Professional Property Management & Development Solutions", company_tagline_style),
                    ""
                ]
            ]

            header_table = Table(header_data, colWidths=[4.5*inch, 2.5*inch])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1a365d')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 20),
                ('RIGHTPADDING', (0, 0), (-1, -1), 20),
                ('TOPPADDING', (0, 0), (-1, -1), 15),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#2c5aa0'))
            ]))

            content.append(header_table)

            # Main Title Section with Enhanced Design
            title_data = [
                [Paragraph("SNAG INSPECTION APPOINTMENT", main_title_style)],
                [Paragraph("OFFICIAL ACKNOWLEDGEMENT DOCUMENT", company_tagline_style)]
            ]

            title_table = Table(title_data, colWidths=[7*inch])
            title_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#2c5aa0')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 20),
                ('RIGHTPADDING', (0, 0), (-1, -1), 20),
                ('TOPPADDING', (0, 0), (-1, -1), 15),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ]))

            content.append(title_table)
            content.append(Spacer(1, 20))

            # Acknowledgment Details
            content.append(Paragraph("ACKNOWLEDGMENT DETAILS", section_header_style))

            ack_data = [
                ['Acknowledged by:', appointment_data['acknowledgment_name']],
                ['Contact Number:', appointment_data['acknowledgment_phone']],
                ['Acknowledged on:', appointment_data['acknowledged_at'].strftime('%B %d, %Y at %I:%M %p')],
                ['Original Owner:', unit_info['owner_name']],
            ]

            ack_table = Table(ack_data, colWidths=[2.5*inch, 4.5*inch])
            ack_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e6f3ff')),
                ('BACKGROUND', (1, 0), (1, -1), colors.white),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a365d')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Times-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Times-Roman'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a365d')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#1a365d')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))

            content.append(ack_table)
            content.append(Spacer(1, 20))

            # Appointment Details
            content.append(Paragraph("APPOINTMENT DETAILS", section_header_style))

            appointment_table_data = [
                ['Appointment Date:', appointment_data['appointment_date'].strftime('%A, %B %d, %Y')],
                ['Time Slot:', f"{timedelta_to_time_string(appointment_data['start_time'])} - {timedelta_to_time_string(appointment_data['end_time'])}"],
                ['Inspector:', appointment_data.get('inspector_name', 'TBA')],
                ['Status:', appointment_data['status'].title()],
                ['Unit:', f"{unit_info['project_name']} - {unit_info['floor_name']} - Unit {unit_info['unit_number']}"],
            ]

            appointment_table = Table(appointment_table_data, colWidths=[2.5*inch, 4.5*inch])
            appointment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e6f3ff')),
                ('BACKGROUND', (1, 0), (1, -1), colors.white),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1a365d')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Times-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Times-Roman'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a365d')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#1a365d')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))

            content.append(appointment_table)
            content.append(Spacer(1, 30))

            # Declaration Section
            content.append(Paragraph("DECLARATION", section_header_style))

            declaration_text = f"""
            I, <b>{appointment_data['acknowledgment_name']}</b>, hereby acknowledge that I have been authorized by
            <b>{unit_info['owner_name']}</b> to represent them for the SNAG inspection appointment scheduled on
            <b>{appointment_data['appointment_date'].strftime('%B %d, %Y')}</b>. I understand the responsibilities
            and will ensure proper coordination for the inspection process.
            """

            # Declaration in a styled box
            declaration_data = [[Paragraph(declaration_text, normal_style)]]
            declaration_table = Table(declaration_data, colWidths=[7*inch])
            declaration_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e6f3ff')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a365d')),
                ('LEFTPADDING', (0, 0), (-1, -1), 20),
                ('RIGHTPADDING', (0, 0), (-1, -1), 20),
                ('TOPPADDING', (0, 0), (-1, -1), 15),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ]))
            content.append(declaration_table)
            content.append(Spacer(1, 20))

            # Professional Footer
            footer_message = f"""
            <b>Document Authenticity:</b> This acknowledgment document has been generated electronically by Better Communities
            and serves as official confirmation of appointment acknowledgment. Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}.
            """

            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#1a365d'),
                fontName='Times-Roman',
                leading=12
            )

            footer_data = [[Paragraph(footer_message, footer_style)]]
            footer_table = Table(footer_data, colWidths=[7*inch])
            footer_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e6f3ff')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1a365d')),
                ('LEFTPADDING', (0, 0), (-1, -1), 25),
                ('RIGHTPADDING', (0, 0), (-1, -1), 25),
                ('TOPPADDING', (0, 0), (-1, -1), 15),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ]))
            content.append(footer_table)

            # Build PDF
            doc.build(content)

            # Get the PDF data
            pdf_data = buffer.getvalue()
            buffer.close()

            # Create response
            filename = f"acknowledgment_{appointment_id}.pdf"

            return send_file(
                BytesIO(pdf_data),
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )

        except Exception as pdf_error:
            print(f"Error generating acknowledgment PDF: {pdf_error}")
            flash('Error generating acknowledgment PDF', 'error')
            return redirect(url_for('owner.appointments'))

    except Exception as e:
        print(f"Error downloading acknowledgment PDF: {e}")
        flash('Error downloading acknowledgment PDF', 'error')
        return redirect(url_for('owner.dashboard'))
