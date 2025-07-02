from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
import hashlib
import time
import bcrypt
import os
from dotenv import load_dotenv
from database import Database
from contractors.routes import contractors_bp
from snag_inspectors.routes import snag_inspectors_bp
from client_relations.routes import client_relations_bp
from owner.routes import owner_bp
from admin.appointments_routes import appointments_bp
from admin.admin_appointment_booking import admin_appointment_bp

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key_here_change_this')

# Initialize database
db = Database()

# Register blueprints
app.register_blueprint(contractors_bp)
app.register_blueprint(snag_inspectors_bp)
app.register_blueprint(client_relations_bp)
app.register_blueprint(owner_bp)
app.register_blueprint(appointments_bp)
app.register_blueprint(admin_appointment_bp)

# Favicon routes
@app.route('/fav/<path:filename>')
def favicon(filename):
    """Serve favicon files"""
    return send_from_directory(os.path.join(app.root_path, 'fav'), filename)

@app.route('/favicon.ico')
def favicon_ico():
    """Serve main favicon.ico"""
    return send_from_directory(os.path.join(app.root_path, 'fav'), 'favicon.ico')

@app.route('/')
def index():
    """Redirect to login page"""
    if 'admin_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash('Please fill in all required fields!', 'error')
            return render_template('login.html')

        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Check credentials in both admin and contractor tables
        connection = db.get_db_connection()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)

                # First check admin table
                query = "SELECT * FROM admin WHERE (username = %s OR email = %s) AND password = %s"
                cursor.execute(query, (username, username, hashed_password))
                admin_user = cursor.fetchone()

                if admin_user:
                    session['admin_id'] = admin_user['id']
                    session['admin_name'] = admin_user['name']
                    session['admin_email'] = admin_user['email']
                    session['user_type'] = 'admin'
                    cursor.close()
                    connection.close()
                    return redirect(url_for('dashboard'))

                # If not admin, check contractors table
                query = "SELECT * FROM contractors WHERE (username = %s OR email = %s) AND password = %s AND status = 'active'"
                cursor.execute(query, (username, username, hashed_password))
                contractor_user = cursor.fetchone()

                if contractor_user:
                    session['contractor_id'] = contractor_user['id']
                    session['contractor_name'] = contractor_user['name']
                    session['contractor_email'] = contractor_user['email']
                    session['user_type'] = 'contractor'
                    cursor.close()
                    connection.close()
                    return redirect(url_for('contractors.dashboard'))

                # Check snag_inspectors table (uses bcrypt)
                query = "SELECT * FROM snag_inspectors WHERE (username = %s OR email = %s) AND status = 'active'"
                cursor.execute(query, (username, username))
                inspector_user = cursor.fetchone()

                if inspector_user and inspector_user['password']:
                    # Check bcrypt password for SNAG inspectors
                    if bcrypt.checkpw(password.encode('utf-8'), inspector_user['password'].encode('utf-8')):
                        session['snag_inspector_id'] = inspector_user['id']
                        session['snag_inspector_name'] = inspector_user['name']
                        session['snag_inspector_email'] = inspector_user['email']
                        session['user_type'] = 'snag_inspector'
                        cursor.close()
                        connection.close()
                        return redirect(url_for('snag_inspectors.dashboard'))

                # Check client_relations table (uses SHA256)
                query = "SELECT * FROM client_relations WHERE (username = %s OR email = %s) AND password = %s AND status = 'active'"
                cursor.execute(query, (username, username, hashed_password))
                client_user = cursor.fetchone()

                if client_user:
                    session['client_id'] = client_user['id']
                    session['client_name'] = client_user['name']
                    session['client_email'] = client_user['email']
                    session['user_type'] = 'client'
                    cursor.close()
                    connection.close()
                    return redirect(url_for('client_relations.dashboard'))

                # Check floor_units table for owners (uses SHA256)
                query = "SELECT * FROM floor_units WHERE (owner_username = %s OR owner_email = %s) AND owner_password = %s AND is_assigned = TRUE"
                cursor.execute(query, (username, username, hashed_password))
                owner_user = cursor.fetchone()

                if owner_user:
                    session['owner_id'] = owner_user['id']
                    session['owner_name'] = owner_user['owner_name']
                    session['owner_email'] = owner_user['owner_email']
                    session['user_type'] = 'owner'
                    cursor.close()
                    connection.close()
                    return redirect(url_for('owner.dashboard'))

                # If no user found
                flash('Invalid credentials!', 'error')

                cursor.close()
                connection.close()

            except Exception as e:
                flash('Database error occurred!', 'error')
                print(f"Login error: {e}")
                if connection:
                    connection.close()
        else:
            flash('Database connection failed!', 'error')

    return render_template('login.html')



@app.route('/dashboard')
def dashboard():
    """Admin dashboard"""
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    # Get project count
    connection = db.get_db_connection()
    stats = {'projects': 0}

    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM projects")
            stats['projects'] = cursor.fetchone()[0]
            cursor.close()
            connection.close()
        except Exception as e:
            print(f"Dashboard error: {e}")

    return render_template('dashboard.html', stats=stats)

@app.route('/payment-verifications')
def payment_verifications():
    """Admin page to view and manage payment verifications"""
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    connection = db.get_db_connection()
    verifications = []

    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT
                    fu.id, fu.unit_number, fu.owner_name, fu.owner_email, fu.owner_phone,
                    fu.payment_verification_status, fu.documents_uploaded_at, fu.verification_notes,
                    CONCAT(pf.prefix, ' ', pf.number) as floor_name,
                    p.project_name
                FROM floor_units fu
                JOIN project_floors pf ON fu.floor_id = pf.id
                JOIN projects p ON pf.project_id = p.id
                WHERE fu.payment_verification_status IN ('submitted', 'approved', 'rejected')
                ORDER BY fu.documents_uploaded_at DESC
            """)
            verifications = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print(f"Error fetching payment verifications: {e}")
            flash('Error loading payment verifications', 'error')
        finally:
            connection.close()

    return render_template('admin/payment_verifications.html', verifications=verifications)

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('You have been logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.route('/projects')
def projects():
    """Projects management page"""
    if 'admin_id' not in session:
        return redirect(url_for('login'))
    return render_template('projects.html')

# Contractors routes moved to contractors blueprint

# Contractor API routes moved to contractors blueprint

@app.route('/project/<int:project_id>')
def project_details(project_id):
    """Project details page"""
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    # Get project details
    connection = db.get_db_connection()
    project = None

    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM projects WHERE id = %s", (project_id,))
            project = cursor.fetchone()

            # Convert database status values to frontend values
            if project and project.get('status') == 'on_hold':
                project['status'] = 'on-hold'

            cursor.close()
            connection.close()
        except Exception as e:
            print(f"Error fetching project: {e}")

    if not project:
        flash('Project not found!', 'error')
        return redirect(url_for('projects'))

    return render_template('project_details.html', project=project, timestamp=int(time.time()))

@app.route('/floor/<int:floor_id>')
def floor_details(floor_id):
    """Floor details page"""
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    connection = db.get_db_connection()
    if not connection:
        flash('Database connection failed!', 'error')
        return redirect(url_for('projects'))

    try:
        cursor = connection.cursor(dictionary=True)

        # Get floor details
        cursor.execute("""
            SELECT f.*, p.project_name, p.id as project_id
            FROM project_floors f
            JOIN projects p ON f.project_id = p.id
            WHERE f.id = %s
        """, (floor_id,))
        floor = cursor.fetchone()

        if not floor:
            flash('Floor not found!', 'error')
            return redirect(url_for('projects'))

        # Get project details
        cursor.execute("SELECT * FROM projects WHERE id = %s", (floor['project_id'],))
        project = cursor.fetchone()

        return render_template('floor_details.html', floor=floor, project=project, timestamp=int(time.time()))

    except Exception as e:
        print(f"Error fetching floor details: {e}")
        flash('Error loading floor details!', 'error')
        return redirect(url_for('projects'))
    finally:
        if connection:
            connection.close()

@app.route('/unit/<int:unit_id>')
def unit_details(unit_id):
    """Unit details page"""
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    connection = db.get_db_connection()
    if not connection:
        flash('Database connection failed!', 'error')
        return redirect(url_for('projects'))

    try:
        cursor = connection.cursor(dictionary=True)

        # Get unit details with floor and project information
        cursor.execute("""
            SELECT u.*, f.number as floor_number, f.prefix as floor_prefix,
                   p.project_name, p.id as project_id, f.id as floor_id
            FROM floor_units u
            JOIN project_floors f ON u.floor_id = f.id
            JOIN projects p ON f.project_id = p.id
            WHERE u.id = %s
        """, (unit_id,))
        unit = cursor.fetchone()

        if not unit:
            flash('Unit not found!', 'error')
            return redirect(url_for('projects'))

        return render_template('unit_details.html', unit=unit)

    except Exception as e:
        print(f"Error fetching unit details: {e}")
        flash('Error loading unit details!', 'error')
        return redirect(url_for('projects'))
    finally:
        if connection:
            connection.close()

# API Routes for Projects
@app.route('/api/projects', methods=['GET'])
def api_get_projects():
    """Get all projects"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT id, project_name, description, location, start_date, end_date, status, created_at FROM projects ORDER BY created_at DESC")
        projects = cursor.fetchall()

        # Convert datetime objects to strings for JSON serialization
        for project in projects:
            if project.get('created_at'):
                project['created_at'] = project['created_at'].isoformat()

        cursor.close()
        connection.close()
        return jsonify({'projects': projects})
    except Exception as e:
        print(f"Error fetching projects: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to fetch projects'}), 500

@app.route('/api/projects', methods=['POST'])
def api_create_project():
    """Create a new project"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    project_name = data.get('projectName', '').strip()
    location = data.get('projectLocation', '').strip()
    description = data.get('projectDescription', '').strip()

    if not project_name or not location:
        return jsonify({'error': 'Project name and location are required'}), 400

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO projects (project_name, location, description, status, created_at)
            VALUES (%s, %s, %s, 'active', NOW())
        """
        cursor.execute(query, (project_name, location, description))
        connection.commit()

        project_id = cursor.lastrowid
        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'message': 'Project created successfully',
            'project_id': project_id
        })
    except Exception as e:
        print(f"Error creating project: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to create project'}), 500

# API Routes for Floors
@app.route('/api/projects/<int:project_id>/floors', methods=['GET'])
def api_get_project_floors(project_id):
    """Get all floors for a project"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM project_floors WHERE project_id = %s ORDER BY prefix, number", (project_id,))
        floors = cursor.fetchall()

        cursor.close()
        connection.close()
        return jsonify(floors)
    except Exception as e:
        print(f"Error fetching floors: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to fetch floors'}), 500

@app.route('/api/floors', methods=['POST'])
def api_create_floor():
    """Create a new floor"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    project_id = data.get('projectId')
    prefix = data.get('prefix', '').strip()
    number = data.get('number')

    if not project_id or not prefix or number is None:
        return jsonify({'error': 'Project ID, prefix, and number are required'}), 400

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()

        # Check if floor number already exists (number must be unique regardless of prefix)
        cursor.execute("SELECT id FROM project_floors WHERE project_id = %s AND number = %s",
                      (project_id, number))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({'error': f'Floor number {number} already exists! Numbers must be unique regardless of prefix.'}), 400

        # Insert new floor
        query = """
            INSERT INTO project_floors (project_id, prefix, number, created_at)
            VALUES (%s, %s, %s, NOW())
        """
        cursor.execute(query, (project_id, prefix, number))
        connection.commit()

        floor_id = cursor.lastrowid

        # Get the created floor
        cursor.execute("SELECT * FROM project_floors WHERE id = %s", (floor_id,))
        new_floor = cursor.fetchone()

        cursor.close()
        connection.close()

        return jsonify({
            'id': new_floor[0],
            'project_id': new_floor[1],
            'prefix': new_floor[2],
            'number': new_floor[3],
            'created_at': new_floor[4].isoformat() if new_floor[4] else None
        })
    except Exception as e:
        print(f"Error creating floor: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to create floor'}), 500

@app.route('/api/floors/bulk', methods=['POST'])
def api_create_floors_bulk():
    """Create multiple floors"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    if not data or 'floors' not in data:
        return jsonify({'error': 'No floors data provided'}), 400

    floors_data = data['floors']
    if not floors_data:
        return jsonify({'error': 'No floors to create'}), 400

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()
        created_floors = []

        for floor_data in floors_data:
            project_id = floor_data.get('projectId')
            prefix = floor_data.get('prefix', '').strip()
            number = floor_data.get('number')

            if not project_id or not prefix or number is None:
                continue

            # Check if floor number already exists (number must be unique regardless of prefix)
            cursor.execute("SELECT id FROM project_floors WHERE project_id = %s AND number = %s",
                          (project_id, number))
            if cursor.fetchone():
                continue

            # Insert new floor
            query = """
                INSERT INTO project_floors (project_id, prefix, number, created_at)
                VALUES (%s, %s, %s, NOW())
            """
            cursor.execute(query, (project_id, prefix, number))
            floor_id = cursor.lastrowid

            created_floors.append({
                'id': floor_id,
                'project_id': project_id,
                'prefix': prefix,
                'number': number
            })

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify(created_floors)
    except Exception as e:
        print(f"Error creating floors: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to create floors'}), 500

@app.route('/api/floors/<int:floor_id>', methods=['PUT'])
def api_update_floor(floor_id):
    """Update a floor"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    prefix = data.get('prefix', '').strip()
    number = data.get('number')

    if not prefix or number is None:
        return jsonify({'error': 'Prefix and number are required'}), 400

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()

        # Update floor
        query = "UPDATE project_floors SET prefix = %s, number = %s WHERE id = %s"
        cursor.execute(query, (prefix, number, floor_id))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({'success': True, 'message': 'Floor updated successfully'})
    except Exception as e:
        print(f"Error updating floor: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to update floor'}), 500

# API Routes for Units
@app.route('/api/floors/<int:floor_id>/units', methods=['GET'])
def api_get_floor_units(floor_id):
    """Get all units for a floor"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        # Select only the fields we need, excluding LONGTEXT fields that contain bytes
        cursor.execute("""
            SELECT id, floor_id, unit_number, owner_name, owner_username,
                   owner_email, owner_phone, country_code, is_assigned,
                   assigned_at, invitation_status, invitation_sent_at,
                   payment_verification_status, created_at
            FROM floor_units
            WHERE floor_id = %s
            ORDER BY unit_number
        """, (floor_id,))
        units = cursor.fetchall()

        # Convert datetime objects to strings for JSON serialization
        for unit in units:
            if unit.get('assigned_at'):
                unit['assigned_at'] = unit['assigned_at'].isoformat()
            if unit.get('invitation_sent_at'):
                unit['invitation_sent_at'] = unit['invitation_sent_at'].isoformat()
            if unit.get('created_at'):
                unit['created_at'] = unit['created_at'].isoformat()

        cursor.close()
        connection.close()
        return jsonify(units)
    except Exception as e:
        print(f"Error fetching units: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to fetch units'}), 500

@app.route('/api/units', methods=['POST'])
def api_create_unit():
    """Create a new unit"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    floor_id = data.get('floorId')
    unit_number = data.get('unitNumber')

    if not floor_id or unit_number is None:
        return jsonify({'error': 'Floor ID and unit number are required'}), 400

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()

        # Check if unit already exists
        cursor.execute("SELECT id FROM floor_units WHERE floor_id = %s AND unit_number = %s",
                      (floor_id, unit_number))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({'error': f'Unit {unit_number} already exists on this floor'}), 400

        # Insert new unit
        query = """
            INSERT INTO floor_units (floor_id, unit_number, created_at)
            VALUES (%s, %s, NOW())
        """
        cursor.execute(query, (floor_id, unit_number))
        connection.commit()

        unit_id = cursor.lastrowid

        # Get the created unit
        cursor.execute("SELECT * FROM floor_units WHERE id = %s", (unit_id,))
        new_unit = cursor.fetchone()

        cursor.close()
        connection.close()

        return jsonify({
            'id': new_unit[0],
            'floor_id': new_unit[1],
            'unit_number': new_unit[2],
            'created_at': new_unit[3].isoformat() if new_unit[3] else None
        })
    except Exception as e:
        print(f"Error creating unit: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to create unit'}), 500

@app.route('/api/add_unit', methods=['POST'])
def api_add_unit():
    """Create a new unit (alternative endpoint)"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    floor_id = data.get('floor_id')
    unit_number = data.get('unit_number')

    if not floor_id or unit_number is None:
        print(f"Missing required fields: floor_id={floor_id}, unit_number={unit_number}")
        return jsonify({
            'success': False,
            'message': 'Floor ID and unit number are required'
        }), 400

    connection = db.get_db_connection()
    if not connection:
        return jsonify({
            'success': False,
            'message': 'Database connection failed'
        }), 500

    try:
        cursor = connection.cursor()

        # Check if unit already exists
        cursor.execute("SELECT id FROM floor_units WHERE floor_id = %s AND unit_number = %s",
                      (floor_id, unit_number))
        existing_unit = cursor.fetchone()
        if existing_unit:
            cursor.close()
            connection.close()
            print(f"Duplicate unit detected: floor_id={floor_id}, unit_number={unit_number}")
            return jsonify({
                'success': False,
                'message': f'Unit {unit_number} already exists on this floor',
                'error_type': 'duplicate'
            }), 400

        # Insert new unit
        query = """
            INSERT INTO floor_units (floor_id, unit_number, created_at)
            VALUES (%s, %s, NOW())
        """
        cursor.execute(query, (floor_id, unit_number))
        connection.commit()

        unit_id = cursor.lastrowid

        # Get the created unit
        cursor.execute("SELECT * FROM floor_units WHERE id = %s", (unit_id,))
        new_unit = cursor.fetchone()

        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'message': f'Unit {unit_number} added successfully',
            'unit': {
                'id': new_unit[0],
                'floor_id': new_unit[1],
                'unit_number': new_unit[2],
                'created_at': new_unit[3].isoformat() if new_unit[3] else None
            }
        })
    except Exception as e:
        print(f"Error creating unit: {e}")
        if connection:
            connection.close()
        return jsonify({
            'success': False,
            'message': f'Failed to create unit: {str(e)}'
        }), 500

@app.route('/api/bulk_add_units', methods=['POST'])
def api_create_units_bulk():
    """Create multiple units"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    print(f"Bulk add units - received data: {data}")

    if not data:
        return jsonify({
            'success': False,
            'message': 'No data provided'
        }), 400

    floor_id = data.get('floor_id')
    prefix = data.get('prefix', '')
    start_unit = data.get('start_number')
    end_unit = data.get('end_number')

    print(f"Parsed values: floor_id={floor_id}, prefix={prefix}, start_unit={start_unit}, end_unit={end_unit}")

    if not floor_id or start_unit is None or end_unit is None:
        return jsonify({
            'success': False,
            'message': 'Floor ID, start unit, and end unit are required'
        }), 400

    if start_unit > end_unit:
        return jsonify({
            'success': False,
            'message': 'Start unit must be less than or equal to end unit'
        }), 400

    connection = db.get_db_connection()
    if not connection:
        return jsonify({
            'success': False,
            'message': 'Database connection failed'
        }), 500

    try:
        cursor = connection.cursor()
        created_units = []
        skipped_count = 0

        for unit_number in range(start_unit, end_unit + 1):
            # Create unit number with prefix
            unit_number_str = f"{prefix}{unit_number}" if prefix else str(unit_number)

            # Check if unit already exists
            cursor.execute("SELECT id FROM floor_units WHERE floor_id = %s AND unit_number = %s",
                          (floor_id, unit_number_str))
            if cursor.fetchone():
                skipped_count += 1
                continue

            # Insert new unit
            query = """
                INSERT INTO floor_units (floor_id, unit_number, created_at)
                VALUES (%s, %s, NOW())
            """
            cursor.execute(query, (floor_id, unit_number_str))
            unit_id = cursor.lastrowid

            created_units.append({
                'id': unit_id,
                'floor_id': floor_id,
                'unit_number': unit_number_str
            })

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'message': f'Successfully created {len(created_units)} units',
            'added_count': len(created_units),
            'skipped_count': skipped_count,
            'units': created_units
        })
    except Exception as e:
        print(f"Error creating units: {e}")
        if connection:
            connection.close()
        return jsonify({
            'success': False,
            'message': f'Failed to create units: {str(e)}'
        }), 500

# API Routes for Areas (Common Areas)
@app.route('/api/projects/<int:project_id>/areas', methods=['GET'])
def api_get_project_areas(project_id):
    """Get all common areas for a project"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM project_areas WHERE project_id = %s ORDER BY name", (project_id,))
        areas = cursor.fetchall()

        cursor.close()
        connection.close()
        return jsonify(areas)
    except Exception as e:
        print(f"Error fetching areas: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to fetch areas'}), 500

@app.route('/api/areas', methods=['POST'])
def api_create_area():
    """Create a new common area"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    project_id = data.get('projectId')
    name = data.get('name', '').strip()

    if not project_id or not name:
        return jsonify({'error': 'Project ID and name are required'}), 400

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()

        # Check if area already exists
        cursor.execute("SELECT id FROM project_areas WHERE project_id = %s AND LOWER(name) = LOWER(%s)",
                      (project_id, name))
        if cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({'error': 'Area already exists'}), 400

        # Insert new area
        query = """
            INSERT INTO project_areas (project_id, name, created_at)
            VALUES (%s, %s, NOW())
        """
        cursor.execute(query, (project_id, name))
        connection.commit()

        area_id = cursor.lastrowid

        # Get the created area
        cursor.execute("SELECT * FROM project_areas WHERE id = %s", (area_id,))
        new_area = cursor.fetchone()

        cursor.close()
        connection.close()

        return jsonify({
            'id': new_area[0],
            'project_id': new_area[1],
            'name': new_area[2],
            'created_at': new_area[3].isoformat() if new_area[3] else None
        })
    except Exception as e:
        print(f"Error creating area: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to create area'}), 500

@app.route('/api/areas/<int:area_id>', methods=['PUT'])
def api_update_area(area_id):
    """Update a common area"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    name = data.get('name', '').strip()

    if not name:
        return jsonify({'error': 'Name is required'}), 400

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()

        # Update area
        query = "UPDATE project_areas SET name = %s WHERE id = %s"
        cursor.execute(query, (name, area_id))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({'success': True, 'message': 'Area updated successfully'})
    except Exception as e:
        print(f"Error updating area: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to update area'}), 500

# API Routes for Project Updates
@app.route('/api/projects/<int:project_id>', methods=['PUT'])
def api_update_project(project_id):
    """Update a project"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    field = data.get('field')
    value = data.get('value')

    if not field or value is None:
        return jsonify({'error': 'Field and value are required'}), 400

    # Map field names to database columns
    field_mapping = {
        'project_name': 'project_name',
        'name': 'project_name',
        'location': 'location',
        'description': 'description',
        'status': 'status'
    }

    db_field = field_mapping.get(field)
    if not db_field:
        return jsonify({'error': 'Invalid field'}), 400

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()
        query = f"UPDATE projects SET {db_field} = %s WHERE id = %s"
        cursor.execute(query, (value, project_id))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({'success': True, 'message': 'Project updated successfully'})
    except Exception as e:
        print(f"Error updating project: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to update project'}), 500

@app.route('/api/projects/<int:project_id>/image', methods=['POST'])
def api_update_project_image(project_id):
    """Update project image - store directly in database"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image file selected'}), 400

    # Check if file is an image
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        return jsonify({'error': 'Invalid file type. Please upload an image.'}), 400

    # Check file size (max 5MB)
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning

    if file_size > 5 * 1024 * 1024:  # 5MB
        return jsonify({'error': 'File too large. Maximum size is 5MB.'}), 400

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()

        # Read the image data
        image_data = file.read()
        image_type = file.content_type

        # Update project with image data
        query = "UPDATE projects SET image_data = %s, image_type = %s WHERE id = %s"
        cursor.execute(query, (image_data, image_type, project_id))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'message': 'Image uploaded successfully',
            'imageUrl': f'/api/projects/{project_id}/image/view'
        })
    except Exception as e:
        print(f"Error uploading image: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to upload image'}), 500

@app.route('/api/projects/<int:project_id>/image/view', methods=['GET'])
def api_get_project_image(project_id):
    """Get project image from database"""
    connection = db.get_db_connection()
    if not connection:
        return "Database connection failed", 500

    try:
        cursor = connection.cursor()
        cursor.execute("SELECT image_data, image_type FROM projects WHERE id = %s", (project_id,))
        result = cursor.fetchone()

        cursor.close()
        connection.close()

        if result and result[0]:
            image_data, image_type = result
            response = app.response_class(
                image_data,
                mimetype=image_type,
                headers={"Content-Disposition": "inline"}
            )
            return response
        else:
            # Return a default placeholder image or 404
            return "No image found", 404

    except Exception as e:
        print(f"Error retrieving image: {e}")
        if connection:
            connection.close()
        return "Error retrieving image", 500

@app.route('/api/unit/<int:unit_id>', methods=['DELETE'])
def api_delete_unit(unit_id):
    """Delete a unit"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()

        # Check if unit exists
        cursor.execute("SELECT id FROM floor_units WHERE id = %s", (unit_id,))
        unit = cursor.fetchone()

        if not unit:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Unit not found'}), 404

        # Delete the unit
        cursor.execute("DELETE FROM floor_units WHERE id = %s", (unit_id,))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({'success': True, 'message': 'Unit deleted successfully'})

    except Exception as e:
        print(f"Error deleting unit: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to delete unit'}), 500

if __name__ == '__main__':
    app.run(debug=True)
