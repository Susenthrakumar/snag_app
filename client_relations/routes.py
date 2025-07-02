from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import hashlib
import csv
import io
import re
from datetime import datetime
from database import Database
from email_service.client_relations_email_sender import ClientRelationsEmailSender
from email_service.owner_email_sender import OwnerEmailSender
from email_service.owner_email_sender import OwnerEmailSender


client_relations_bp = Blueprint('client_relations', __name__, url_prefix='/client_relations')
db = Database()
email_sender = ClientRelationsEmailSender()
owner_email_sender = OwnerEmailSender()
owner_email_sender = OwnerEmailSender()

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    # Remove any spaces, dashes, or parentheses
    cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)

    # Check if it's a valid phone number (10-15 digits, may start with +)
    pattern = r'^\+?[1-9]\d{9,14}$'
    return re.match(pattern, cleaned_phone) is not None

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    # Remove any spaces, dashes, or parentheses
    cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Check if it's a valid phone number (10-15 digits, may start with +)
    pattern = r'^\+?[1-9]\d{9,14}$'
    return re.match(pattern, cleaned_phone) is not None

def validate_username(username):
    """Validate username format"""
    if len(username) < 3 or len(username) > 50:
        return False
    # Allow letters, numbers, underscores, and hyphens
    pattern = r'^[a-zA-Z0-9_-]+$'
    return re.match(pattern, username) is not None

def check_username_availability(username):
    """Check if username is available across all tables"""
    if not validate_username(username):
        return False, "Username must be 3-50 characters and contain only letters, numbers, underscores, and hyphens"

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
            print(f"Error checking username: {e}")
            if connection:
                connection.close()
            return False, "Database error occurred"
    
    return False, "Database connection failed"

def check_phone_availability(phone):
    """Check if phone number is available across all tables"""
    if not validate_phone(phone):
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
            print(f"Error checking phone: {e}")
            if connection:
                connection.close()
            return False, "Database error occurred"
    
    return False, "Database connection failed"

@client_relations_bp.route('/')
def clients_list():
    """Client Relations management page"""
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    
    # Get all clients from database
    connection = db.get_db_connection()
    clients = []
    
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM client_relations ORDER BY created_at DESC")
            clients = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(f"Error fetching clients: {e}")
            flash('Error loading clients', 'error')
        finally:
            connection.close()
    
    return render_template('admin/client_relations/list.html', clients=clients)

@client_relations_bp.route('/register')
def register():
    """Client registration page"""
    email = request.args.get('email')
    token = request.args.get('token')
    
    if not email or not token:
        flash('Invalid registration link', 'error')
        return redirect(url_for('login'))
    
    # Verify token
    connection = db.get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM client_relations WHERE email = %s AND registration_token = %s AND status = 'pending'", (email, token))
            client = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if not client:
                flash('Invalid or expired registration link', 'error')
                return redirect(url_for('login'))
                
        except Exception as e:
            print(f"Error verifying token: {e}")
            if connection:
                connection.close()
            flash('Database error', 'error')
            return redirect(url_for('login'))
    else:
        flash('Database connection error', 'error')
        return redirect(url_for('login'))
    
    return render_template('client_relations/register.html', email=email, token=token)

@client_relations_bp.route('/register', methods=['POST'])
def register_post():
    """Handle client registration form submission"""
    email = request.form.get('email')
    token = request.form.get('token')
    name = request.form.get('name')
    username = request.form.get('username')
    password = request.form.get('password')
    phone = request.form.get('phone')
    country_code = request.form.get('country_code', '+91')
    company_name = request.form.get('company_name', '')
    
    # Validate required fields
    if not all([email, token, name, username, password, phone]):
        flash('All fields are required', 'error')
        return render_template('client_relations/register.html', email=email, token=token)
    
    # Validate formats
    if not validate_email(email):
        flash('Invalid email format', 'error')
        return render_template('client_relations/register.html', email=email, token=token)
    
    if not validate_phone(phone):
        flash('Invalid phone number format', 'error')
        return render_template('client_relations/register.html', email=email, token=token)
    
    # Check username availability
    username_available, username_message = check_username_availability(username)
    if not username_available:
        flash(username_message, 'error')
        return render_template('client_relations/register.html', email=email, token=token)
    
    # Check phone availability
    phone_available, phone_message = check_phone_availability(phone)
    if not phone_available:
        flash(phone_message, 'error')
        return render_template('client_relations/register.html', email=email, token=token)
    
    # Verify token and update client
    connection = db.get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Verify token
            cursor.execute("SELECT id FROM client_relations WHERE email = %s AND registration_token = %s AND status = 'pending'", (email, token))
            if not cursor.fetchone():
                flash('Invalid or expired registration link', 'error')
                cursor.close()
                connection.close()
                return render_template('client_relations/register.html', email=email, token=token)
            
            # Hash password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Update client
            cursor.execute("""
                UPDATE client_relations
                SET name = %s, username = %s, password = %s, phone = %s, country_code = %s,
                    company_name = %s, status = 'active', registered_at = NOW(),
                    registration_token = NULL
                WHERE email = %s AND registration_token = %s
            """, (name, username, hashed_password, phone, country_code, company_name, email, token))
            
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
            return render_template('client_relations/register.html', email=email, token=token)
    
    flash('Database connection error', 'error')
    return render_template('client_relations/register.html', email=email, token=token)

@client_relations_bp.route('/dashboard')
def dashboard():
    """Client dashboard"""
    if 'client_id' not in session:
        return redirect(url_for('login'))

    return render_template('client_relations/dashboard.html')

@client_relations_bp.route('/projects')
def projects():
    """Client projects page"""
    if 'client_id' not in session:
        return redirect(url_for('login'))

    return render_template('client_relations/projects.html')

@client_relations_bp.route('/documents')
def documents():
    """Document approval management page"""
    if 'client_id' not in session:
        return redirect(url_for('login'))

    connection = db.get_db_connection()
    pending_docs = []
    verified_docs = []
    rejected_docs = []

    if connection:
        try:
            cursor = connection.cursor(dictionary=True)

            # Get all documents with unit and project information
            cursor.execute("""
                SELECT
                    fu.id, fu.unit_number, fu.owner_name, fu.owner_email,
                    fu.payment_verification_status, fu.documents_uploaded_at, fu.verification_notes,
                    fu.payment_proof_document, fu.id_proof_document,
                    fu.payment_proof_verified, fu.id_proof_verified,
                    fu.payment_proof_rejected_reason, fu.id_proof_rejected_reason,
                    CONCAT(pf.prefix, ' ', pf.number) as floor_name,
                    p.project_name
                FROM floor_units fu
                JOIN project_floors pf ON fu.floor_id = pf.id
                JOIN projects p ON pf.project_id = p.id
                WHERE (fu.payment_proof_document IS NOT NULL OR fu.id_proof_document IS NOT NULL)
                ORDER BY fu.documents_uploaded_at DESC
            """)

            all_docs = cursor.fetchall()

            # Separate documents by individual verification status
            for doc in all_docs:
                # Create document entries for payment proof
                if doc['payment_proof_document']:
                    doc_entry = dict(doc)
                    doc_entry['document_type'] = 'Payment Proof'

                    # Handle both bytes and string data
                    document_data = doc['payment_proof_document']
                    if isinstance(document_data, bytes):
                        try:
                            # Try to decode as UTF-8 string first
                            decoded_string = document_data.decode('utf-8')
                            if decoded_string.startswith('data:'):
                                document_data = decoded_string
                            else:
                                import base64
                                document_data = base64.b64encode(document_data).decode('utf-8')
                                document_data = f"data:image/jpeg;base64,{document_data}"
                        except UnicodeDecodeError:
                            import base64
                            document_data = base64.b64encode(document_data).decode('utf-8')
                            document_data = f"data:image/jpeg;base64,{document_data}"
                    elif isinstance(document_data, str):
                        if not document_data.startswith('data:'):
                            document_data = f"data:image/jpeg;base64,{document_data}"
                        elif document_data.startswith('data:application/octet-stream'):
                            document_data = document_data.replace('data:application/octet-stream', 'data:image/jpeg')

                    doc_entry['document_data'] = document_data
                    doc_entry['individual_verified'] = doc.get('payment_proof_verified')
                    doc_entry['rejection_reason'] = doc.get('payment_proof_rejected_reason')

                    # Check individual verification status for payment proof
                    payment_verified = doc.get('payment_proof_verified')
                    if payment_verified is None:
                        pending_docs.append(doc_entry)
                    elif payment_verified == 1:
                        verified_docs.append(doc_entry)
                    elif payment_verified == 0:
                        rejected_docs.append(doc_entry)

                # Create document entries for ID proof
                if doc['id_proof_document']:
                    doc_entry = dict(doc)
                    doc_entry['document_type'] = 'ID Proof'

                    # Handle both bytes and string data
                    document_data = doc['id_proof_document']
                    if isinstance(document_data, bytes):
                        try:
                            # Try to decode as UTF-8 string first
                            decoded_string = document_data.decode('utf-8')
                            if decoded_string.startswith('data:'):
                                document_data = decoded_string
                            else:
                                import base64
                                document_data = base64.b64encode(document_data).decode('utf-8')
                                document_data = f"data:image/jpeg;base64,{document_data}"
                        except UnicodeDecodeError:
                            import base64
                            document_data = base64.b64encode(document_data).decode('utf-8')
                            document_data = f"data:image/jpeg;base64,{document_data}"
                    elif isinstance(document_data, str):
                        if not document_data.startswith('data:'):
                            document_data = f"data:image/jpeg;base64,{document_data}"
                        elif document_data.startswith('data:application/octet-stream'):
                            document_data = document_data.replace('data:application/octet-stream', 'data:image/jpeg')

                    doc_entry['document_data'] = document_data
                    doc_entry['individual_verified'] = doc.get('id_proof_verified')
                    doc_entry['rejection_reason'] = doc.get('id_proof_rejected_reason')

                    # Check individual verification status for ID proof
                    id_verified = doc.get('id_proof_verified')
                    if id_verified is None:
                        pending_docs.append(doc_entry)
                    elif id_verified == 1:
                        verified_docs.append(doc_entry)
                    elif id_verified == 0:
                        rejected_docs.append(doc_entry)

            cursor.close()
        except Exception as e:
            print(f"Error fetching documents: {e}")
            flash('Error loading documents', 'error')
        finally:
            connection.close()

    return render_template('client_relations/documents.html',
                         pending_docs=pending_docs,
                         verified_docs=verified_docs,
                         rejected_docs=rejected_docs)

@client_relations_bp.route('/logout')
def logout():
    """Client logout"""
    session.clear()
    flash('You have been logged out successfully', 'success')
    return redirect(url_for('login'))

# API Routes
@client_relations_bp.route('/api/upload-csv', methods=['POST'])
def api_upload_csv():
    """Upload and process client CSV file - only extract emails, don't send"""
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
        import io
        import csv

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

        return jsonify({
            'success': True,
            'emails': emails,
            'message': f'Successfully extracted {len(emails)} email addresses from CSV'
        })

    except Exception as e:
        print(f"Error processing CSV file: {e}")
        return jsonify({'error': 'Failed to process CSV file'}), 500

@client_relations_bp.route('/api/send-invitations', methods=['POST'])
def api_send_invitations():
    """Send email invitations to clients"""
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
                # Check if email already exists
                cursor.execute("SELECT id, status FROM client_relations WHERE email = %s", (email,))
                existing = cursor.fetchone()

                # Generate registration token
                registration_token = email_sender.generate_registration_token()

                # Insert or update client
                if existing:
                    # Set status to 'resend' for existing pending invitations
                    new_status = 'resend' if existing[1] == 'pending' else existing[1]
                    cursor.execute("""
                        UPDATE client_relations
                        SET registration_token = %s, invitation_sent_at = NOW(), status = %s
                        WHERE email = %s
                    """, (registration_token, new_status, email))
                else:
                    cursor.execute("""
                        INSERT INTO client_relations (email, registration_token, status, invitation_sent_at, created_at)
                        VALUES (%s, %s, 'pending', NOW(), NOW())
                    """, (email, registration_token))

                # Send invitation email
                if email_sender.send_client_invitation(email, registration_token):
                    success_count += 1
                else:
                    failed_emails.append(email)

            except Exception as e:
                print(f"Error processing email {email}: {e}")
                failed_emails.append(email)

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'message': f'Invitations sent successfully to {success_count} clients',
            'success_count': success_count,
            'failed_emails': failed_emails
        })

    except Exception as e:
        print(f"Error sending invitations: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to send invitations'}), 500

@client_relations_bp.route('/api/validate-username', methods=['POST'])
def api_validate_username():
    """Validate username availability across all tables"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()

        if not username:
            return jsonify({'available': False, 'message': 'Username is required'})

        available, message = check_username_availability(username)
        return jsonify({'available': available, 'message': message})

    except Exception as e:
        print(f"Error validating username: {e}")
        return jsonify({'available': False, 'message': 'Validation error occurred'})

@client_relations_bp.route('/api/validate-phone', methods=['POST'])
def api_validate_phone():
    """Validate phone number availability across all tables"""
    try:
        data = request.get_json()
        phone = data.get('phone', '').strip()

        if not phone:
            return jsonify({'available': False, 'message': 'Phone number is required'})

        available, message = check_phone_availability(phone)
        return jsonify({'available': available, 'message': message})

    except Exception as e:
        print(f"Error validating phone: {e}")
        return jsonify({'available': False, 'message': 'Validation error occurred'})

@client_relations_bp.route('/api/validate-email', methods=['POST'])
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

        # Check contractors table
        cursor.execute("SELECT id FROM contractors WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({'available': False, 'message': 'Email already exists as contractor'})

        # Check client_relations table
        cursor.execute("SELECT id, status FROM client_relations WHERE email = %s", (email,))
        existing_client = cursor.fetchone()

        cursor.close()
        connection.close()

        if existing_client:
            if existing_client[1] == 'pending':
                return jsonify({'available': True, 'message': 'Email will update existing pending invitation'})
            else:
                return jsonify({'available': False, 'message': 'Email already exists as active client'})

        return jsonify({'available': True, 'message': 'Email is available'})

    except Exception as e:
        print(f"Error validating email: {e}")
        return jsonify({'available': False, 'message': 'Validation error occurred'})

@client_relations_bp.route('/api/projects', methods=['GET'])
def api_get_projects():
    """Get all projects for client dashboard"""
    if 'client_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        connection = db.get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = connection.cursor(dictionary=True)

        # Get all projects with floor and unit counts
        cursor.execute("""
            SELECT
                p.id,
                p.project_name,
                p.description as project_description,
                p.location,
                p.created_at,
                COUNT(DISTINCT pf.id) as floor_count,
                COUNT(DISTINCT fu.id) as unit_count,
                COUNT(DISTINCT CASE WHEN fu.is_assigned = TRUE THEN fu.id END) as assigned_units
            FROM projects p
            LEFT JOIN project_floors pf ON p.id = pf.project_id
            LEFT JOIN floor_units fu ON pf.id = fu.floor_id
            GROUP BY p.id, p.project_name, p.description, p.location, p.created_at
            ORDER BY p.created_at DESC
        """)

        projects = cursor.fetchall()
        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'projects': projects
        })

    except Exception as e:
        print(f"Error fetching projects: {e}")
        return jsonify({'error': 'Failed to fetch projects'}), 500

@client_relations_bp.route('/api/project/<int:project_id>/available-units', methods=['GET'])
def api_get_available_units(project_id):
    """Get available units for a project"""
    if 'client_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    try:
        connection = db.get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500

        cursor = connection.cursor(dictionary=True)

        # Get available units (not assigned)
        cursor.execute("""
            SELECT fu.id, fu.unit_number, CONCAT(pf.prefix, ' ', pf.number) as floor_name
            FROM floor_units fu
            JOIN project_floors pf ON fu.floor_id = pf.id
            WHERE pf.project_id = %s AND fu.is_assigned = FALSE
            ORDER BY pf.number, fu.unit_number
        """, (project_id,))

        units = cursor.fetchall()
        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'units': units
        })

    except Exception as e:
        print(f"Error fetching available units: {e}")
        return jsonify({'error': 'Failed to fetch units'}), 500



@client_relations_bp.route('/project/<int:project_id>')
def project_details(project_id):
    """View project details with floors and units"""
    if 'client_id' not in session:
        return redirect(url_for('login'))

    connection = db.get_db_connection()
    project = None
    floors = []

    if connection:
        try:
            cursor = connection.cursor(dictionary=True)

            # Get project details
            cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
            project = cursor.fetchone()

            if project:
                # Get floors with unit counts
                cursor.execute("""
                    SELECT
                        pf.*,
                        CONCAT(pf.prefix, ' ', pf.number) as floor_name,
                        COUNT(fu.id) as unit_count,
                        COUNT(CASE WHEN fu.is_assigned = TRUE THEN fu.id END) as assigned_units
                    FROM project_floors pf
                    LEFT JOIN floor_units fu ON pf.id = fu.floor_id
                    WHERE pf.project_id = %s
                    GROUP BY pf.id
                    ORDER BY pf.number
                """, (project_id,))
                floors = cursor.fetchall()

            cursor.close()
        except Exception as e:
            print(f"Error fetching project details: {e}")
            flash('Error loading project details', 'error')
        finally:
            connection.close()

    if not project:
        flash('Project not found', 'error')
        return redirect(url_for('client_relations.dashboard'))

    return render_template('client_relations/project_details.html', project=project, floors=floors)

@client_relations_bp.route('/project/<int:project_id>/floor/<int:floor_id>')
def floor_details(project_id, floor_id):
    """View floor details with units and owner assignment interface"""
    if 'client_id' not in session:
        return redirect(url_for('login'))

    connection = db.get_db_connection()
    project = None
    floor = None
    units = []

    if connection:
        try:
            cursor = connection.cursor(dictionary=True)

            # Get project and floor details
            cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
            project = cursor.fetchone()

            cursor.execute("SELECT *, CONCAT(prefix, ' ', number) as floor_name FROM project_floors WHERE id = %s AND project_id = %s", (floor_id, project_id))
            floor = cursor.fetchone()

            if project and floor:
                # Get units with owner details
                cursor.execute("""
                    SELECT * FROM floor_units
                    WHERE floor_id = %s
                    ORDER BY unit_number
                """, (floor_id,))
                units = cursor.fetchall()

            cursor.close()
        except Exception as e:
            print(f"Error fetching floor details: {e}")
            flash('Error loading floor details', 'error')
        finally:
            connection.close()

    if not project or not floor:
        flash('Floor not found', 'error')
        return redirect(url_for('client_relations.dashboard'))

    return render_template('client_relations/floor_details.html', project=project, floor=floor, units=units)

@client_relations_bp.route('/unit/<int:unit_id>')
def unit_details(unit_id):
    """View unit details with owner information and quick actions"""
    if 'client_id' not in session:
        return redirect(url_for('login'))

    connection = db.get_db_connection()
    unit = None
    floor = None
    project = None

    if connection:
        try:
            cursor = connection.cursor(dictionary=True)

            # Get unit details with floor and project information
            cursor.execute("""
                SELECT
                    fu.*,
                    CONCAT(pf.prefix, ' ', pf.number) as floor_name,
                    pf.id as floor_id,
                    p.project_name,
                    p.id as project_id,
                    p.created_at as project_created_at
                FROM floor_units fu
                JOIN project_floors pf ON fu.floor_id = pf.id
                JOIN projects p ON pf.project_id = p.id
                WHERE fu.id = %s
            """, (unit_id,))

            result = cursor.fetchone()

            if result:
                unit = {
                    'id': result['id'],
                    'unit_number': result['unit_number'],
                    'owner_name': result.get('owner_name'),
                    'owner_username': result.get('owner_username'),
                    'owner_phone': result.get('owner_phone'),
                    'owner_email': result.get('owner_email'),
                    'country_code': result.get('country_code'),
                    'is_assigned': result.get('is_assigned'),
                    'assigned_at': result.get('assigned_at'),
                    'invitation_status': result.get('invitation_status'),
                    'invitation_sent_at': result.get('invitation_sent_at'),
                    'created_at': result['created_at'],
                    'has_owner': result.get('owner_email') is not None,
                    'invitation_sent': result.get('invitation_status') is not None,
                    'is_registered': result.get('invitation_status') == 'registered'
                }

                floor = {
                    'id': result['floor_id'],
                    'floor_name': result['floor_name']
                }

                project = {
                    'id': result['project_id'],
                    'project_name': result['project_name'],
                    'created_at': result['project_created_at']
                }

            cursor.close()
        except Exception as e:
            print(f"Error fetching unit details: {e}")
            flash('Error loading unit details', 'error')
        finally:
            connection.close()

    if not unit:
        flash('Unit not found', 'error')
        return redirect(url_for('client_relations.dashboard'))

    return render_template('client_relations/unit_details.html', unit=unit, floor=floor, project=project)

# API Routes for Owner Assignment
@client_relations_bp.route('/api/assign-owner', methods=['POST'])
def api_assign_owner():
    """Assign owner to unit with email verification and invitation sending"""
    if 'client_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    unit_id = data.get('unit_id')
    owner_name = data.get('owner_name', '').strip()
    owner_email = data.get('owner_email', '').strip()

    # Validate required fields
    if not all([unit_id, owner_name, owner_email]):
        return jsonify({'error': 'Unit ID, owner name, and email are required'}), 400

    # Validate email format
    if not validate_email(owner_email):
        return jsonify({'error': 'Invalid email format'}), 400

    # Check if email already exists in database
    email_exists, email_msg = check_email_exists_in_all_tables(owner_email)
    if email_exists:
        return jsonify({'error': 'Email already exists in the system'}), 400

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # Get unit details for email
        cursor.execute("""
            SELECT
                fu.id, fu.unit_number, fu.is_assigned,
                CONCAT(pf.prefix, ' ', pf.number) as floor_name,
                p.project_name, p.id as project_id
            FROM floor_units fu
            JOIN project_floors pf ON fu.floor_id = pf.id
            JOIN projects p ON pf.project_id = p.id
            WHERE fu.id = %s
        """, (unit_id,))

        unit = cursor.fetchone()
        if not unit:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Unit not found'}), 404

        if unit['is_assigned']:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Unit is already assigned'}), 400

        # Generate invitation token
        invitation_token = owner_email_sender.generate_invitation_token()

        # Update unit with owner information and invitation status
        cursor.execute("""
            UPDATE floor_units
            SET owner_name = %s, owner_email = %s, invitation_token = %s,
                invitation_status = 'pending', invitation_sent_at = NOW()
            WHERE id = %s
        """, (owner_name, owner_email, invitation_token, unit_id))

        connection.commit()

        # Send invitation email
        email_sent = owner_email_sender.send_unit_assignment_invitation(
            owner_email=owner_email,
            owner_name=owner_name,
            unit_number=unit['unit_number'],
            floor_name=unit['floor_name'],
            project_name=unit['project_name'],
            invitation_token=invitation_token
        )

        if email_sent:
            cursor.close()
            connection.close()
            return jsonify({
                'success': True,
                'message': f'Invitation sent to {owner_email} for unit {unit["unit_number"]}'
            })
        else:
            # Rollback the database changes if email failed
            cursor.execute("""
                UPDATE floor_units
                SET owner_name = NULL, owner_email = NULL, invitation_token = NULL,
                    invitation_status = NULL, invitation_sent_at = NULL
                WHERE id = %s
            """, (unit_id,))
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify({'error': 'Failed to send invitation email'}), 500

    except Exception as e:
        print(f"Error assigning owner: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to assign owner'}), 500

def check_email_exists_in_all_tables(email):
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

@client_relations_bp.route('/api/resend-invitation', methods=['POST'])
def api_resend_invitation():
    """Resend invitation email to unit owner"""
    if 'client_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    unit_id = data.get('unit_id')

    if not unit_id:
        return jsonify({'error': 'Unit ID is required'}), 400

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # Get unit details
        cursor.execute("""
            SELECT
                fu.id, fu.unit_number, fu.owner_name, fu.owner_email, fu.invitation_status,
                CONCAT(pf.prefix, ' ', pf.number) as floor_name,
                p.project_name
            FROM floor_units fu
            JOIN project_floors pf ON fu.floor_id = pf.id
            JOIN projects p ON pf.project_id = p.id
            WHERE fu.id = %s AND fu.owner_email IS NOT NULL
        """, (unit_id,))

        unit = cursor.fetchone()
        if not unit:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Unit not found or no owner assigned'}), 404

        # Generate new invitation token
        invitation_token = owner_email_sender.generate_invitation_token()

        # Update invitation token and status
        cursor.execute("""
            UPDATE floor_units
            SET invitation_token = %s, invitation_status = 'pending', invitation_sent_at = NOW()
            WHERE id = %s
        """, (invitation_token, unit_id))

        connection.commit()

        # Send invitation email
        email_sent = owner_email_sender.send_unit_assignment_invitation(
            owner_email=unit['owner_email'],
            owner_name=unit['owner_name'],
            unit_number=unit['unit_number'],
            floor_name=unit['floor_name'],
            project_name=unit['project_name'],
            invitation_token=invitation_token
        )

        if email_sent:
            cursor.close()
            connection.close()
            return jsonify({
                'success': True,
                'message': f'Invitation resent to {unit["owner_email"]}'
            })
        else:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Failed to send invitation email'}), 500

    except Exception as e:
        print(f"Error resending invitation: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to resend invitation'}), 500

@client_relations_bp.route('/api/remove-owner', methods=['POST'])
def api_remove_owner():
    """Remove owner assignment from unit"""
    if 'client_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    unit_id = data.get('unit_id')

    if not unit_id:
        return jsonify({'error': 'Unit ID is required'}), 400

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()

        # Remove owner assignment and all uploaded documents
        cursor.execute("""
            UPDATE floor_units
            SET owner_name = NULL, owner_username = NULL, owner_password = NULL,
                owner_email = NULL, owner_phone = NULL, owner_documents = NULL,
                is_assigned = FALSE, assigned_at = NULL, invitation_token = NULL,
                invitation_status = NULL, invitation_sent_at = NULL,
                payment_verification_status = 'pending',
                payment_proof_document = NULL, id_proof_document = NULL,
                documents_uploaded_at = NULL, verification_notes = NULL,
                payment_proof_verified = NULL, id_proof_verified = NULL,
                payment_proof_rejected_reason = NULL, id_proof_rejected_reason = NULL
            WHERE id = %s
        """, (unit_id,))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'message': 'Owner removed successfully'
        })

    except Exception as e:
        print(f"Error removing owner: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to remove owner'}), 500

@client_relations_bp.route('/api/view-document/<int:unit_id>/<document_type>')
def api_view_document(unit_id, document_type):
    """View document content"""
    if 'client_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # Get document based on type
        if document_type == 'Payment Proof':
            cursor.execute("SELECT payment_proof_document FROM floor_units WHERE id = %s", (unit_id,))
            result = cursor.fetchone()
            document_data = result['payment_proof_document'] if result else None
        elif document_type == 'ID Proof':
            cursor.execute("SELECT id_proof_document FROM floor_units WHERE id = %s", (unit_id,))
            result = cursor.fetchone()
            document_data = result['id_proof_document'] if result else None
        else:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Invalid document type'}), 400

        cursor.close()
        connection.close()

        if not document_data:
            return jsonify({'error': 'Document not found'}), 404



        # Handle both bytes (LONGBLOB) and string (LONGTEXT) data
        if isinstance(document_data, bytes):
            # Check if bytes contain a data URL string
            try:
                # Try to decode as UTF-8 string first
                decoded_string = document_data.decode('utf-8')
                if decoded_string.startswith('data:'):
                    # It's a data URL stored as bytes
                    document_data = decoded_string
                else:
                    # It's actual binary data, convert to base64
                    import base64
                    document_data = base64.b64encode(document_data).decode('utf-8')
                    document_data = f"data:image/jpeg;base64,{document_data}"
            except UnicodeDecodeError:
                # It's binary data, convert to base64
                import base64
                document_data = base64.b64encode(document_data).decode('utf-8')
                document_data = f"data:image/jpeg;base64,{document_data}"
        elif isinstance(document_data, str):
            # Ensure proper data URL format
            if not document_data.startswith('data:'):
                # Assume it's base64 encoded image data
                document_data = f"data:image/jpeg;base64,{document_data}"
            elif document_data.startswith('data:application/octet-stream'):
                # Replace generic MIME type with image type for better preview
                document_data = document_data.replace('data:application/octet-stream', 'data:image/jpeg')

        return jsonify({
            'success': True,
            'document_data': document_data
        })

    except Exception as e:
        print(f"Error viewing document: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to load document'}), 500



@client_relations_bp.route('/api/verify-document', methods=['POST'])
def api_verify_document():
    """Verify an individual document"""
    if 'client_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    unit_id = data.get('unit_id')
    document_type = data.get('document_type')

    if not all([unit_id, document_type]):
        return jsonify({'error': 'Unit ID and document type are required'}), 400

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # Get unit details for email
        cursor.execute("""
            SELECT owner_email, owner_name, unit_number,
                   CONCAT(pf.prefix, ' ', pf.number) as floor_name,
                   p.project_name,
                   payment_proof_verified, id_proof_verified
            FROM floor_units fu
            JOIN project_floors pf ON fu.floor_id = pf.id
            JOIN projects p ON pf.project_id = p.id
            WHERE fu.id = %s
        """, (unit_id,))

        unit = cursor.fetchone()
        if not unit:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Unit not found'}), 404

        # Update individual document verification status
        if document_type == 'Payment Proof':
            cursor.execute("""
                UPDATE floor_units
                SET payment_proof_verified = 1, payment_proof_rejected_reason = NULL
                WHERE id = %s
            """, (unit_id,))
        elif document_type == 'ID Proof':
            cursor.execute("""
                UPDATE floor_units
                SET id_proof_verified = 1, id_proof_rejected_reason = NULL
                WHERE id = %s
            """, (unit_id,))
        else:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Invalid document type'}), 400

        # Check if both documents exist and are verified
        cursor.execute("""
            SELECT payment_proof_verified, id_proof_verified,
                   payment_proof_document, id_proof_document
            FROM floor_units WHERE id = %s
        """, (unit_id,))

        verification_status = cursor.fetchone()

        # If both documents exist and are verified, update overall status to approved and send success email
        if (verification_status['payment_proof_verified'] == 1 and
            verification_status['id_proof_verified'] == 1 and
            verification_status['payment_proof_document'] is not None and
            verification_status['id_proof_document'] is not None):
            cursor.execute("""
                UPDATE floor_units
                SET payment_verification_status = 'approved',
                    verification_notes = 'All documents verified and approved'
                WHERE id = %s
            """, (unit_id,))

            connection.commit()
            cursor.close()
            connection.close()

            # Send success email only when both documents are verified
            try:
                owner_email_sender.send_all_documents_verified_email(
                    owner_email=unit['owner_email'],
                    owner_name=unit['owner_name'],
                    unit_number=unit['unit_number'],
                    floor_name=unit['floor_name'],
                    project_name=unit['project_name']
                )
            except Exception as e:
                print(f"Error sending success email: {e}")

            return jsonify({
                'success': True,
                'message': 'All documents verified successfully! Owner has been notified.'
            })
        else:
            connection.commit()
            cursor.close()
            connection.close()

            return jsonify({
                'success': True,
                'message': f'{document_type} verified successfully. Waiting for other document verification.'
            })

    except Exception as e:
        print(f"Error verifying document: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to verify document'}), 500

@client_relations_bp.route('/api/reject-document', methods=['POST'])
def api_reject_document():
    """Reject a document with reason"""
    if 'client_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    unit_id = data.get('unit_id')
    document_type = data.get('document_type')
    reason = data.get('reason', '').strip()

    if not all([unit_id, document_type, reason]):
        return jsonify({'error': 'Unit ID, document type, and reason are required'}), 400

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # Get unit details for email
        cursor.execute("""
            SELECT owner_email, owner_name, unit_number,
                   CONCAT(pf.prefix, ' ', pf.number) as floor_name,
                   p.project_name
            FROM floor_units fu
            JOIN project_floors pf ON fu.floor_id = pf.id
            JOIN projects p ON pf.project_id = p.id
            WHERE fu.id = %s
        """, (unit_id,))

        unit = cursor.fetchone()
        if not unit:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Unit not found'}), 404

        # Update individual document rejection status
        if document_type == 'Payment Proof':
            cursor.execute("""
                UPDATE floor_units
                SET payment_proof_verified = 0,
                    payment_proof_rejected_reason = %s
                WHERE id = %s
            """, (reason, unit_id))
        elif document_type == 'ID Proof':
            cursor.execute("""
                UPDATE floor_units
                SET id_proof_verified = 0,
                    id_proof_rejected_reason = %s
                WHERE id = %s
            """, (reason, unit_id))
        else:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Invalid document type'}), 400

        # Update overall status to rejected if any document is rejected
        cursor.execute("""
            UPDATE floor_units
            SET payment_verification_status = 'rejected',
                verification_notes = %s
            WHERE id = %s
        """, (f'{document_type} rejected: {reason}', unit_id))

        connection.commit()
        cursor.close()
        connection.close()

        # Send rejection email
        try:
            owner_email_sender.send_document_rejection_email(
                owner_email=unit['owner_email'],
                owner_name=unit['owner_name'],
                unit_number=unit['unit_number'],
                floor_name=unit['floor_name'],
                project_name=unit['project_name'],
                document_type=document_type,
                rejection_reason=reason
            )
        except Exception as e:
            print(f"Error sending rejection email: {e}")

        return jsonify({
            'success': True,
            'message': 'Document rejected and notification sent to owner'
        })

    except Exception as e:
        print(f"Error rejecting document: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to reject document'}), 500


