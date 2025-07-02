from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import hashlib
import csv
import io
import re
from database import Database
from email_service.email_sender import EmailSender

contractors_bp = Blueprint('contractors', __name__, url_prefix='/contractors')
db = Database()
email_sender = EmailSender()

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"

def validate_username(username):
    """Validate username - check both admin and contractor tables"""
    if len(username) < 3:
        return False, "Username must be at least 3 characters long"

    if len(username) > 20:
        return False, "Username must be less than 20 characters"

    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "Username can only contain letters, numbers, and underscores"

    # Check if username already exists in all tables
    connection = db.get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()

            # Check admin table
            cursor.execute("SELECT id FROM admin WHERE username = %s", (username,))
            if cursor.fetchone():
                return False, "Username already exists as admin"

            # Check snag_inspectors table
            cursor.execute("SELECT id FROM snag_inspectors WHERE username = %s", (username,))
            if cursor.fetchone():
                return False, "Username already exists as SNAG inspector"

            # Check contractors table
            cursor.execute("SELECT id FROM contractors WHERE username = %s", (username,))
            if cursor.fetchone():
                return False, "Username already exists as contractor"

            # Check client_relations table
            cursor.execute("SELECT id FROM client_relations WHERE username = %s", (username,))
            if cursor.fetchone():
                return False, "Username already exists as client"

            cursor.close()
            connection.close()
            return True, "Username is available"
        except Exception as e:
            if connection:
                connection.close()
            return False, "Error validating username"

    return True, "Username is valid"

def validate_phone(phone):
    """Validate phone number - check for duplicates"""
    if not phone or len(phone.strip()) == 0:
        return True, "Phone number is optional"

    phone = phone.strip()

    # Basic phone validation
    if len(phone) < 10:
        return False, "Phone number must be at least 10 digits"

    if not re.match(r"^[+]?[0-9\s\-\(\)]+$", phone):
        return False, "Invalid phone number format"

    # Check if phone already exists
    connection = db.get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()

            # Check admin table (both combined and separate storage)
            cursor.execute("SELECT id FROM admin WHERE phone = %s OR CONCAT(COALESCE(country_code, '+91'), phone) = %s", (phone, phone))
            if cursor.fetchone():
                return False, "Phone number already exists as admin"

            # Check snag_inspectors table (both combined and separate storage)
            cursor.execute("SELECT id FROM snag_inspectors WHERE phone = %s OR CONCAT(COALESCE(country_code, '+91'), phone) = %s", (phone, phone))
            if cursor.fetchone():
                return False, "Phone number already exists as SNAG inspector"

            # Check contractors table (both combined and separate storage)
            cursor.execute("SELECT id FROM contractors WHERE phone = %s OR CONCAT(COALESCE(country_code, '+91'), phone) = %s", (phone, phone))
            if cursor.fetchone():
                return False, "Phone number already exists as contractor"

            # Check client_relations table (both combined and separate storage)
            cursor.execute("SELECT id FROM client_relations WHERE phone = %s OR CONCAT(COALESCE(country_code, '+91'), phone) = %s", (phone, phone))
            if cursor.fetchone():
                return False, "Phone number already exists as client"

            cursor.close()
            connection.close()
            return True, "Phone number is available"
        except Exception as e:
            if connection:
                connection.close()
            return False, "Error validating phone number"

    return True, "Phone number is valid"

@contractors_bp.route('/')
def contractors_list():
    """Contractors management page"""
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    # Get all contractors from database
    connection = db.get_db_connection()
    contractors = []
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM contractors ORDER BY created_at DESC")
            contractors = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(f"Error fetching contractors: {e}")
            flash('Error loading contractors', 'error')
        finally:
            connection.close()
    
    return render_template('admin/contractors/list.html', contractors=contractors)

@contractors_bp.route('/register')
def register():
    """Contractor registration page"""
    token = request.args.get('token')
    email = request.args.get('email')
    
    if not token or not email:
        flash('Invalid registration link', 'error')
        return redirect(url_for('login'))
    
    # Verify token and email
    connection = db.get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM contractors 
                WHERE email = %s AND registration_token = %s AND status = 'pending'
            """, (email, token))
            contractor = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if not contractor:
                flash('Invalid or expired registration link', 'error')
                return redirect(url_for('login'))
                
        except Exception as e:
            print(f"Error verifying registration: {e}")
            if connection:
                connection.close()
            flash('Error processing registration', 'error')
            return redirect(url_for('login'))
    
    return render_template('contractors/register.html', email=email, token=token)

@contractors_bp.route('/register', methods=['POST'])
def register_post():
    """Process contractor registration"""
    token = request.form.get('token')
    email = request.form.get('email')
    name = request.form.get('name', '').strip()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    confirm_password = request.form.get('confirm_password', '').strip()
    phone = request.form.get('phone', '').strip()
    country_code = request.form.get('country_code', '+91').strip()
    company_name = request.form.get('company_name', '').strip()
    category = request.form.get('category', '').strip()
    category_other = request.form.get('category_other', '').strip()
    
    # Validation
    if not all([token, email, name, username, password, confirm_password, category]):
        flash('Please fill in all required fields', 'error')
        return render_template('contractors/register.html', email=email, token=token)

    # Validate category_other if category is 'others'
    if category == 'others' and not category_other:
        flash('Please specify your category', 'error')
        return render_template('contractors/register.html', email=email, token=token)
    
    if password != confirm_password:
        flash('Passwords do not match', 'error')
        return render_template('contractors/register.html', email=email, token=token)
    
    # Validate username
    username_valid, username_msg = validate_username(username)
    if not username_valid:
        flash(username_msg, 'error')
        return render_template('contractors/register.html', email=email, token=token)
    
    # Validate password
    password_valid, password_msg = validate_password(password)
    if not password_valid:
        flash(password_msg, 'error')
        return render_template('contractors/register.html', email=email, token=token)

    # Validate phone number
    if phone:
        # Combine country code with phone for validation
        full_phone = country_code + phone
        phone_valid, phone_msg = validate_phone(full_phone)
        if not phone_valid:
            flash(phone_msg, 'error')
            return render_template('contractors/register.html', email=email, token=token)
    
    # Hash password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Update contractor record
    connection = db.get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Verify token again
            cursor.execute("""
                SELECT id FROM contractors 
                WHERE email = %s AND registration_token = %s AND status = 'pending'
            """, (email, token))
            
            if not cursor.fetchone():
                flash('Invalid or expired registration link', 'error')
                cursor.close()
                connection.close()
                return render_template('contractors/register.html', email=email, token=token)
            
            # Update contractor
            cursor.execute("""
                UPDATE contractors
                SET name = %s, username = %s, password = %s, phone = %s, country_code = %s,
                    company_name = %s, category = %s, category_other = %s,
                    status = 'active', registered_at = NOW(),
                    registration_token = NULL
                WHERE email = %s AND registration_token = %s
            """, (name, username, hashed_password, phone, country_code, company_name, category, category_other, email, token))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            # Send welcome email
            email_sender.send_welcome_email(email, name)
            
            flash('Registration completed successfully! You can now login.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            print(f"Error completing registration: {e}")
            if connection:
                connection.close()
            flash('Error completing registration', 'error')
            return render_template('contractors/register.html', email=email, token=token)
    
    flash('Database connection error', 'error')
    return render_template('contractors/register.html', email=email, token=token)

# Contractor login removed - using unified login in main app

@contractors_bp.route('/dashboard')
def dashboard():
    """Contractor dashboard"""
    if 'contractor_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('contractors/dashboard.html')

@contractors_bp.route('/logout')
def logout():
    """Contractor logout"""
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('login'))

# API Routes
@contractors_bp.route('/api/send-invitations', methods=['POST'])
def api_send_invitations():
    """Send email invitations to contractors"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    emails = data.get('emails', [])
    
    if not emails:
        return jsonify({'error': 'No email addresses provided'}), 400
    
    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        success_count = 0
        failed_emails = []
        
        for email in emails:
            try:
                # Check if email already exists in other tables
                email_exists = False
                existing_location = ""

                # Check admin table
                cursor.execute("SELECT id FROM admin WHERE email = %s", (email,))
                if cursor.fetchone():
                    email_exists = True
                    existing_location = "admin"

                # Check snag_inspectors table
                if not email_exists:
                    cursor.execute("SELECT id FROM snag_inspectors WHERE email = %s", (email,))
                    if cursor.fetchone():
                        email_exists = True
                        existing_location = "SNAG inspector"

                if email_exists and existing_location != "":
                    failed_emails.append(f"{email} - Email already exists as {existing_location}")
                    continue

                # Check if contractor already exists
                cursor.execute("SELECT id, status FROM contractors WHERE email = %s", (email,))
                existing = cursor.fetchone()

                if existing:
                    if existing[1] == 'active':
                        failed_emails.append(f"{email} (already registered)")
                        continue
                    # For pending status, allow resend and update status to 'resend'
                
                # Generate registration token
                registration_token = email_sender.generate_registration_token()
                
                # Insert or update contractor
                if existing:
                    # Set status to 'resend' for existing pending invitations
                    new_status = 'resend' if existing[1] == 'pending' else existing[1]
                    cursor.execute("""
                        UPDATE contractors
                        SET registration_token = %s, invitation_sent_at = NOW(), status = %s
                        WHERE email = %s
                    """, (registration_token, new_status, email))
                else:
                    cursor.execute("""
                        INSERT INTO contractors (email, registration_token, status, invitation_sent_at, created_at)
                        VALUES (%s, %s, 'pending', NOW(), NOW())
                    """, (email, registration_token))
                
                # Send email
                success, message = email_sender.send_contractor_invitation(email, registration_token)
                
                if success:
                    success_count += 1
                else:
                    failed_emails.append(f"{email} (email failed: {message})")
                    
            except Exception as e:
                failed_emails.append(f"{email} (error: {str(e)})")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        response_message = f'Successfully sent {success_count} invitations'
        if failed_emails:
            response_message += f'. Failed: {", ".join(failed_emails)}'
        
        return jsonify({
            'success': True,
            'message': response_message,
            'success_count': success_count,
            'failed_count': len(failed_emails)
        })
        
    except Exception as e:
        print(f"Error sending invitations: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to send invitations'}), 500

@contractors_bp.route('/api/upload-csv', methods=['POST'])
def api_upload_csv():
    """Upload and process contractor CSV file - only extract emails, don't send"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not file.filename.lower().endswith('.csv'):
        return jsonify({'error': 'Please upload a CSV file'}), 400

    try:
        # Read CSV file
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        emails = []

        # Skip header row if it exists
        first_row = next(csv_input, None)
        if first_row and '@' not in first_row[0]:
            # This is likely a header row, skip it
            pass
        else:
            # This is data, process it
            if first_row and len(first_row) > 0:
                email = first_row[0].strip()
                if '@' in email:
                    emails.append(email)

        # Process remaining rows
        for row in csv_input:
            if row and len(row) > 0:
                email = row[0].strip()
                if '@' in email and email not in emails:
                    emails.append(email)

        if not emails:
            return jsonify({'error': 'No valid email addresses found in CSV file'}), 400

        # Return emails for frontend to display
        return jsonify({
            'success': True,
            'message': f'Successfully extracted {len(emails)} email addresses from CSV',
            'emails': emails,
            'total_emails': len(emails)
        })

    except Exception as e:
        print(f"Error processing CSV: {e}")
        return jsonify({'error': 'Failed to process CSV file'}), 500

@contractors_bp.route('/api/validate-username', methods=['POST'])
def api_validate_username():
    """Validate username availability"""
    data = request.get_json()
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({'valid': False, 'message': 'Username is required'})
    
    valid, message = validate_username(username)
    return jsonify({'valid': valid, 'message': message})

@contractors_bp.route('/api/validate-password', methods=['POST'])
def api_validate_password():
    """Validate password strength"""
    data = request.get_json()
    password = data.get('password', '')

    if not password:
        return jsonify({'valid': False, 'message': 'Password is required'})

    valid, message = validate_password(password)
    return jsonify({'valid': valid, 'message': message})

@contractors_bp.route('/api/validate-phone', methods=['POST'])
def api_validate_phone():
    """Validate phone number availability"""
    data = request.get_json()
    phone = data.get('phone', '').strip()

    if not phone:
        return jsonify({'valid': True, 'message': 'Phone number is optional'})

    valid, message = validate_phone(phone)
    return jsonify({'valid': valid, 'message': message})

@contractors_bp.route('/api/validate-email', methods=['POST'])
def api_validate_email():
    """Validate email availability across all tables"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()

        if not email:
            return jsonify({'available': False, 'message': 'Email is required'})

        connection = db.get_db_connection()
        if not connection:
            return jsonify({'available': False, 'message': 'Database connection failed'})

        cursor = connection.cursor()

        # Check admin table
        cursor.execute("SELECT id FROM admin WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({'available': False, 'message': 'Email already exists as admin'})

        # Check snag_inspectors table
        cursor.execute("SELECT id FROM snag_inspectors WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({'available': False, 'message': 'Email already exists as SNAG inspector'})

        # Check client_relations table
        cursor.execute("SELECT id FROM client_relations WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({'available': False, 'message': 'Email already exists as client'})

        # Check contractors table
        cursor.execute("SELECT id, status FROM contractors WHERE email = %s", (email,))
        existing = cursor.fetchone()

        cursor.close()
        connection.close()

        if existing:
            return jsonify({'available': True, 'message': 'Will update existing contractor invitation'})

        return jsonify({'available': True, 'message': 'Email available'})

    except Exception as e:
        return jsonify({'available': False, 'message': 'Error validating email'})
