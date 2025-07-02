from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
import mysql.connector
from database import Database
import secrets
import string
from email_service.inspector_email_sender import InspectorEmailSender
import bcrypt

# Initialize database manager
db_manager = Database()

def get_db_connection():
    return db_manager.get_db_connection()

snag_inspectors_bp = Blueprint('snag_inspectors', __name__, url_prefix='/snag-inspectors')

def validate_username_availability(username):
    """Check if username is available for SNAG inspectors"""
    try:
        connection = get_db_connection()
        if not connection:
            return False, "Database connection failed"
        
        cursor = connection.cursor()
        
        # Check admin table
        cursor.execute("SELECT id FROM admin WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return False, "Username already exists as admin"

        # Check contractors table
        cursor.execute("SELECT id FROM contractors WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return False, "Username already exists as contractor"

        # Check snag_inspectors table
        cursor.execute("SELECT id FROM snag_inspectors WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return False, "Username already exists as SNAG inspector"

        # Check client_relations table
        cursor.execute("SELECT id FROM client_relations WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return False, "Username already exists as client"

        cursor.close()
        connection.close()
        return True, "Username available"
        
    except Exception as e:
        if connection:
            connection.close()
        return False, "Error validating username"

def validate_phone_availability(phone):
    """Check if phone number is available for SNAG inspectors"""
    try:
        connection = get_db_connection()
        if not connection:
            return False, "Database connection failed"

        cursor = connection.cursor()

        # Check admin table (both combined and separate storage)
        cursor.execute("SELECT id FROM admin WHERE phone = %s OR CONCAT(COALESCE(country_code, '+91'), phone) = %s", (phone, phone))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return False, "Phone number already exists as admin"

        # Check contractors table (both combined and separate storage)
        cursor.execute("SELECT id FROM contractors WHERE phone = %s OR CONCAT(COALESCE(country_code, '+91'), phone) = %s", (phone, phone))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return False, "Phone number already exists as contractor"

        # Check snag_inspectors table (both combined and separate storage)
        cursor.execute("SELECT id FROM snag_inspectors WHERE phone = %s OR CONCAT(COALESCE(country_code, '+91'), phone) = %s", (phone, phone))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return False, "Phone number already exists as SNAG inspector"

        # Check client_relations table (both combined and separate storage)
        cursor.execute("SELECT id FROM client_relations WHERE phone = %s OR CONCAT(COALESCE(country_code, '+91'), phone) = %s", (phone, phone))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return False, "Phone number already exists as client"

        cursor.close()
        connection.close()
        return True, "Phone number available"

    except Exception as e:
        if connection:
            connection.close()
        return False, "Error validating phone number"

def validate_email_availability(email):
    """Check if email is available across all tables"""
    try:
        connection = get_db_connection()
        if not connection:
            return False, "Database connection failed", None

        cursor = connection.cursor()

        # Check admin table
        cursor.execute("SELECT id FROM admin WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return False, "Email already exists as admin", "admin"

        # Check contractors table
        cursor.execute("SELECT id FROM contractors WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return False, "Email already exists as contractor", "contractor"
        
        # Check client_relations table
        cursor.execute("SELECT id FROM client_relations WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return False, "Email already exists as client", "client"

        # Check snag_inspectors table
        cursor.execute("SELECT id, status FROM snag_inspectors WHERE email = %s", (email,))
        existing = cursor.fetchone()
        if existing:
            cursor.close()
            connection.close()
            return False, f"Email already exists as SNAG inspector (status: {existing[1]})", "snag_inspector"

        cursor.close()
        connection.close()
        return True, "Email available", None

    except Exception as e:
        if connection:
            connection.close()
        return False, "Error validating email", None

@snag_inspectors_bp.route('/')
def inspectors_list():
    """Display list of SNAG inspectors"""
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    try:
        connection = get_db_connection()
        if not connection:
            flash('Database connection failed', 'error')
            return render_template('admin/snag_inspectors/list.html', inspectors=[])
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, name, email, username, phone, company_name,
                   status, invitation_sent_at, registered_at, registration_token
            FROM snag_inspectors
            ORDER BY invitation_sent_at DESC
        """)
        
        inspectors = cursor.fetchall()
        cursor.close()
        connection.close()
        
        return render_template('admin/snag_inspectors/list.html', inspectors=inspectors)
        
    except Exception as e:
        flash('Error loading SNAG inspectors', 'error')
        return render_template('admin/snag_inspectors/list.html', inspectors=[])

@snag_inspectors_bp.route('/register')
def register():
    """SNAG inspector registration page"""
    token = request.args.get('token')
    email = request.args.get('email')
    
    if not token or not email:
        flash('Invalid registration link', 'error')
        return redirect(url_for('login'))
    
    # Verify token and email
    try:
        connection = get_db_connection()
        if not connection:
            flash('Database connection failed', 'error')
            return redirect(url_for('login'))
        
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, name, email FROM snag_inspectors 
            WHERE email = %s AND registration_token = %s AND status = 'pending'
        """, (email, token))
        
        inspector = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if not inspector:
            flash('Invalid or expired registration link', 'error')
            return redirect(url_for('login'))
        
        return render_template('snag_inspectors/register.html', 
                             email=email, token=token, inspector=inspector)
        
    except Exception as e:
        flash('Error validating registration link', 'error')
        return redirect(url_for('login'))

@snag_inspectors_bp.route('/register', methods=['POST'])
def register_post():
    """Handle SNAG inspector registration form submission"""
    token = request.args.get('token')
    email = request.args.get('email')
    
    # Get form data
    name = request.form.get('name', '').strip()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    phone = request.form.get('phone', '').strip()
    country_code = request.form.get('country_code', '+91').strip()
    company_name = request.form.get('company_name', '').strip()
    
    # Validation
    if not all([token, email, name, username, password, confirm_password]):
        flash('Please fill in all required fields', 'error')
        return render_template('snag_inspectors/register.html', email=email, token=token)
    
    if password != confirm_password:
        flash('Passwords do not match', 'error')
        return render_template('snag_inspectors/register.html', email=email, token=token)
    
    if len(password) < 8:
        flash('Password must be at least 8 characters long', 'error')
        return render_template('snag_inspectors/register.html', email=email, token=token)
    
    # Check username availability
    username_available, username_message = validate_username_availability(username)
    if not username_available:
        flash(username_message, 'error')
        return render_template('snag_inspectors/register.html', email=email, token=token)
    
    # Check phone availability if provided
    if phone:
        # Combine country code with phone for validation
        full_phone = country_code + phone
        phone_available, phone_message = validate_phone_availability(full_phone)
        if not phone_available:
            flash(phone_message, 'error')
            return render_template('snag_inspectors/register.html', email=email, token=token)
    
    try:
        connection = get_db_connection()
        if not connection:
            flash('Database connection failed', 'error')
            return render_template('snag_inspectors/register.html', email=email, token=token)
        
        cursor = connection.cursor()
        
        # Verify token and email again
        cursor.execute("""
            SELECT id FROM snag_inspectors 
            WHERE email = %s AND registration_token = %s AND status = 'pending'
        """, (email, token))
        
        if not cursor.fetchone():
            flash('Invalid or expired registration link', 'error')
            cursor.close()
            connection.close()
            return redirect(url_for('login'))
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update inspector
        cursor.execute("""
            UPDATE snag_inspectors
            SET name = %s, username = %s, password = %s, phone = %s, country_code = %s,
                company_name = %s, status = 'active', registered_at = NOW(),
                registration_token = NULL
            WHERE email = %s AND registration_token = %s
        """, (name, username, hashed_password, phone, country_code, company_name, email, token))
        
        connection.commit()
        cursor.close()
        connection.close()

        # Send welcome email
        email_sender = InspectorEmailSender()
        email_sender.send_welcome_email(email, name)

        flash('Registration completed successfully! You can now login.', 'success')
        return redirect(url_for('login'))
        
    except Exception as e:
        flash('Error completing registration', 'error')
        return render_template('snag_inspectors/register.html', email=email, token=token)

@snag_inspectors_bp.route('/dashboard')
def dashboard():
    """SNAG inspector dashboard"""
    if 'snag_inspector_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('snag_inspectors/dashboard.html')

@snag_inspectors_bp.route('/logout')
def logout():
    """SNAG inspector logout"""
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('login'))

# API Routes
@snag_inspectors_bp.route('/api/send-invitations', methods=['POST'])
def api_send_invitations():
    """Send email invitations to SNAG inspectors"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        emails = data.get('emails', [])
        
        if not emails:
            return jsonify({'error': 'No email addresses provided'}), 400
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor = connection.cursor()
        successful_invitations = []
        failed_invitations = []
        
        for email in emails:
            try:
                # Validate email availability across all tables
                is_available, message, existing_type = validate_email_availability(email)

                if not is_available and existing_type in ['admin', 'contractor']:
                    failed_invitations.append(f"{email} - {message}")
                    continue

                # Check if inspector already exists in snag_inspectors table
                cursor.execute("SELECT id, status FROM snag_inspectors WHERE email = %s", (email,))
                existing = cursor.fetchone()

                if existing:
                    if existing[1] == 'pending':
                        # Update existing pending invitation
                        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
                        cursor.execute("""
                            UPDATE snag_inspectors
                            SET registration_token = %s, invitation_sent_at = NOW(), status = 'pending'
                            WHERE email = %s
                        """, (token, email))
                    elif existing[1] == 'active':
                        failed_invitations.append(f"{email} - Already registered")
                        continue
                    else:
                        # Resend to inactive
                        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
                        cursor.execute("""
                            UPDATE snag_inspectors
                            SET registration_token = %s, invitation_sent_at = NOW(), status = 'resend'
                            WHERE email = %s
                        """, (token, email))
                else:
                    # Create new invitation
                    token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
                    cursor.execute("""
                        INSERT INTO snag_inspectors (email, registration_token, status, invitation_sent_at)
                        VALUES (%s, %s, 'pending', NOW())
                    """, (email, token))
                
                # Send email
                email_sender = InspectorEmailSender()
                success, message = email_sender.send_inspector_invitation(email, token, "http://127.0.0.1:5000")
                if success:
                    successful_invitations.append(email)
                else:
                    failed_invitations.append(f"{email} - Email sending failed")
                    
            except Exception as e:
                failed_invitations.append(f"{email} - {str(e)}")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        message = f"Sent {len(successful_invitations)} invitations successfully"
        if failed_invitations:
            message += f". {len(failed_invitations)} failed: {', '.join(failed_invitations)}"
        
        return jsonify({
            'success': True,
            'message': message,
            'successful': successful_invitations,
            'failed': failed_invitations
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@snag_inspectors_bp.route('/api/validate-username', methods=['POST'])
def api_validate_username():
    """Validate username availability for SNAG inspectors"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({'available': False, 'message': 'Username is required'})
        
        available, message = validate_username_availability(username)
        return jsonify({'available': available, 'message': message})
        
    except Exception as e:
        return jsonify({'available': False, 'message': 'Error validating username'})

@snag_inspectors_bp.route('/api/validate-phone', methods=['POST'])
def api_validate_phone():
    """Validate phone number availability for SNAG inspectors"""
    try:
        data = request.get_json()
        phone = data.get('phone', '').strip()

        if not phone:
            return jsonify({'available': True, 'message': 'Phone number is optional'})

        available, message = validate_phone_availability(phone)
        return jsonify({'available': available, 'message': message})

    except Exception as e:
        return jsonify({'available': False, 'message': 'Error validating phone number'})

@snag_inspectors_bp.route('/api/validate-email', methods=['POST'])
def api_validate_email():
    """Validate email availability across all tables"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()

        if not email:
            return jsonify({'available': False, 'message': 'Email is required'})

        available, message, existing_type = validate_email_availability(email)

        # For invitation purposes, we allow resending to existing SNAG inspectors
        if not available and existing_type == 'snag_inspector':
            return jsonify({'available': True, 'message': 'Will update existing SNAG inspector invitation'})

        return jsonify({'available': available, 'message': message})

    except Exception as e:
        return jsonify({'available': False, 'message': 'Error validating email'})

@snag_inspectors_bp.route('/api/upload-csv', methods=['POST'])
def api_upload_csv():
    """Handle CSV file upload for SNAG inspector emails"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith(('.csv', '.xlsx', '.xls')):
            return jsonify({'error': 'Please upload a CSV or Excel file'}), 400
        
        # Read file content
        content = file.read().decode('utf-8')
        
        # Parse emails from CSV
        emails = []
        lines = content.strip().split('\n')
        
        for line in lines:
            # Handle both comma and semicolon separators
            parts = line.replace(';', ',').split(',')
            for part in parts:
                email = part.strip().strip('"').strip("'")
                if email and '@' in email:
                    emails.append(email)
        
        # Remove duplicates while preserving order
        unique_emails = []
        seen = set()
        for email in emails:
            if email.lower() not in seen:
                unique_emails.append(email)
                seen.add(email.lower())
        
        return jsonify({
            'success': True,
            'emails': unique_emails,
            'count': len(unique_emails)
        })
        
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500
