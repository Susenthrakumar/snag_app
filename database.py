import mysql.connector
from mysql.connector import Error
import hashlib
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Database:
    def __init__(self):
        # Load from environment variables
        self.host = os.getenv('DB_HOST')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.database = os.getenv('DB_NAME')
        self.port = int(os.getenv('DB_PORT', 3306))

def create_connection(self):
    """Create database connection"""
    try:
        connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            port=self.port
        )
        print("✅ MySQL connection successful!")
        return connection
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        print(f"Host: {self.host}, User: {self.user}, Database: {self.database}, Port: {self.port}")
        return None

    
    def create_database(self):
        """Create the snag_management database"""
        connection = self.create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("CREATE DATABASE IF NOT EXISTS snag_management")
                print("Database 'snag_management' created successfully!")
                cursor.close()
                connection.close()
            except Error as e:
                print(f"Error creating database: {e}")
    
    def get_db_connection(self):
        """Get connection to the snag_management database"""
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            return connection
        except Error as e:
            print(f"Error connecting to database: {e}")
            return None
    
    def create_tables(self):
        """Create all required tables"""
        connection = self.get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()
                
                # Admin table
                admin_table = """
                CREATE TABLE IF NOT EXISTS admin (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    phone VARCHAR(15) NOT NULL,
                    country_code VARCHAR(10) DEFAULT '+91',
                    email VARCHAR(100) UNIQUE NOT NULL,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
                
                # Projects table
                projects_table = """
                CREATE TABLE IF NOT EXISTS projects (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    project_name VARCHAR(200) NOT NULL,
                    description TEXT,
                    location VARCHAR(255) NOT NULL,
                    image_data LONGBLOB,
                    image_type VARCHAR(50),
                    start_date DATE,
                    end_date DATE,
                    status ENUM('active', 'completed', 'on-hold', 'cancelled') DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """

                # Project floors table
                project_floors_table = """
                CREATE TABLE IF NOT EXISTS project_floors (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    project_id INT NOT NULL,
                    prefix VARCHAR(50) NOT NULL,
                    number INT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_floor (project_id, prefix, number)
                )
                """

                # Project areas table
                project_areas_table = """
                CREATE TABLE IF NOT EXISTS project_areas (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    project_id INT NOT NULL,
                    name VARCHAR(200) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
                )
                """

                # Floor units table
                floor_units_table = """
                CREATE TABLE IF NOT EXISTS floor_units (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    floor_id INT NOT NULL,
                    unit_number VARCHAR(50) NOT NULL,
                    owner_name VARCHAR(100),
                    owner_username VARCHAR(50) UNIQUE,
                    owner_password VARCHAR(255),
                    owner_email VARCHAR(100),
                    owner_phone VARCHAR(20),
                    country_code VARCHAR(10) DEFAULT '+971',
                    owner_documents LONGTEXT,
                    is_assigned BOOLEAN DEFAULT FALSE,
                    assigned_at TIMESTAMP NULL,
                    invitation_token VARCHAR(255),
                    invitation_status ENUM('pending', 'registered', 'expired') DEFAULT NULL,
                    invitation_sent_at TIMESTAMP NULL,
                    payment_verification_status ENUM('pending', 'submitted', 'approved', 'rejected') DEFAULT 'pending',
                    payment_proof_document LONGTEXT,
                    id_proof_document LONGTEXT,
                    documents_uploaded_at TIMESTAMP NULL,
                    verification_notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (floor_id) REFERENCES project_floors(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_unit (floor_id, unit_number)
                )
                """

                # Contractors table
                contractors_table = """
                CREATE TABLE IF NOT EXISTS contractors (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100),
                    username VARCHAR(50) UNIQUE,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255),
                    phone VARCHAR(20),
                    country_code VARCHAR(10) DEFAULT '+91',
                    company_name VARCHAR(100),
                    category ENUM('electrical', 'plumbing', 'construction', 'painting', 'carpentry', 'masonry', 'roofing', 'hvac', 'landscaping', 'others') DEFAULT 'others',
                    category_other VARCHAR(100),
                    status ENUM('pending', 'active', 'inactive', 'resend') DEFAULT 'pending',
                    registration_token VARCHAR(100),
                    invitation_sent_at TIMESTAMP NULL,
                    registered_at TIMESTAMP NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
                """

                # SNAG Inspectors table
                snag_inspectors_table = """
                CREATE TABLE IF NOT EXISTS snag_inspectors (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100),
                    username VARCHAR(50) UNIQUE,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255),
                    phone VARCHAR(20),
                    country_code VARCHAR(10) DEFAULT '+91',
                    company_name VARCHAR(100),
                    status ENUM('pending', 'active', 'inactive', 'resend') DEFAULT 'pending',
                    registration_token VARCHAR(100),
                    invitation_sent_at TIMESTAMP NULL,
                    registered_at TIMESTAMP NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
                """

                # Client Relations table
                client_relations_table = """
                CREATE TABLE IF NOT EXISTS client_relations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100),
                    username VARCHAR(50) UNIQUE,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255),
                    phone VARCHAR(20),
                    country_code VARCHAR(10) DEFAULT '+91',
                    company_name VARCHAR(100),
                    status ENUM('pending', 'active', 'inactive', 'resend') DEFAULT 'pending',
                    registration_token VARCHAR(100),
                    invitation_sent_at TIMESTAMP NULL,
                    registered_at TIMESTAMP NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
                """
                                                
              
                # Execute table creation
                cursor.execute(admin_table)
                cursor.execute(projects_table)
                cursor.execute(project_floors_table)
                cursor.execute(project_areas_table)
                cursor.execute(floor_units_table)
                cursor.execute(contractors_table)
                cursor.execute(snag_inspectors_table)
                cursor.execute(client_relations_table)
                
                print("All tables created successfully!")
                
                # Create default admin user
                self.create_default_admin(cursor)
                
                connection.commit()
                cursor.close()
                connection.close()
                
            except Error as e:
                print(f"Error creating tables: {e}")
    
    def create_default_admin(self, cursor):
        """Create a default admin user"""
        try:
            # Check if admin already exists
            cursor.execute("SELECT COUNT(*) FROM admin WHERE username = 'admin'")
            count = cursor.fetchone()[0]

            if count == 0:
                # Hash the default password
                password = hashlib.sha256('admin123'.encode()).hexdigest()

                insert_admin = """
                INSERT INTO admin (name, phone, email, username, password)
                VALUES (%s, %s, %s, %s, %s)
                """
                admin_data = ('Administrator', '9876543210', 'admin@snagmanagement.com', 'admin', password)
                cursor.execute(insert_admin, admin_data)
                print("Default admin user created successfully!")
                print("Username: admin, Password: admin123")
            else:
                print("Admin user already exists!")
        except Error as e:
            print(f"Error creating default admin: {e}")
    
    def update_database_schema(self):
        """Update existing database schema for image storage"""
        connection = self.get_db_connection()
        if connection:
            try:
                cursor = connection.cursor()

                # Add image columns to projects table if they don't exist
                try:
                    cursor.execute("ALTER TABLE projects ADD COLUMN image_data LONGBLOB")
                    print("Added image_data column")
                except mysql.connector.Error:
                    print("image_data column already exists")

                try:
                    cursor.execute("ALTER TABLE projects ADD COLUMN image_type VARCHAR(50)")
                    print("Added image_type column")
                except mysql.connector.Error:
                    print("image_type column already exists")

                connection.commit()
                print("Database schema updated successfully!")

            except mysql.connector.Error as err:
                print(f"Error updating database schema: {err}")
            finally:
                if connection:
                    connection.close()

    def update_project_status_enum(self):
        """Update the project status ENUM to include new values"""
        connection = self.get_db_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()

            # Update the ENUM to include new status values
            cursor.execute("""
                ALTER TABLE projects
                MODIFY COLUMN status ENUM('active', 'completed', 'on-hold', 'cancelled') DEFAULT 'active'
            """)

            connection.commit()
            cursor.close()
            connection.close()
            print("Project status ENUM updated successfully")
            return True

        except Exception as e:
            print(f"Error updating project status ENUM: {e}")
            if connection:
                connection.close()
            return False

    def add_unit_type_column(self):
        """Add unit_type column to floor_units table"""
        connection = self.get_db_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()

            # Check if column already exists
            cursor.execute("""
                SELECT COUNT(*)
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s
                AND TABLE_NAME = 'floor_units'
                AND COLUMN_NAME = 'unit_type'
            """, (self.database,))

            column_exists = cursor.fetchone()[0] > 0

            if not column_exists:
                # Add the unit_type column
                cursor.execute("""
                    ALTER TABLE floor_units
                    ADD COLUMN unit_type VARCHAR(50) DEFAULT 'Residential'
                    AFTER unit_number
                """)
                print("unit_type column added to floor_units table successfully")
            else:
                print("unit_type column already exists in floor_units table")

            connection.commit()
            cursor.close()
            connection.close()
            return True

        except Exception as e:
            print(f"Error adding unit_type column: {e}")
            if connection:
                connection.close()
            return False

    def update_floor_units_schema(self):
        """Update floor_units table schema for unit owner management"""
        connection = self.get_db_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()

            # Check if new columns exist
            cursor.execute("""
                SELECT COLUMN_NAME
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s
                AND TABLE_NAME = 'floor_units'
            """, (self.database,))

            existing_columns = [row[0] for row in cursor.fetchall()]

            # Add new columns if they don't exist
            if 'owner_username' not in existing_columns:
                cursor.execute("ALTER TABLE floor_units ADD COLUMN owner_username VARCHAR(50) UNIQUE AFTER owner_name")
                print("Added owner_username column")

            if 'owner_password' not in existing_columns:
                cursor.execute("ALTER TABLE floor_units ADD COLUMN owner_password VARCHAR(255) AFTER owner_username")
                print("Added owner_password column")

            if 'country_code' not in existing_columns:
                cursor.execute("ALTER TABLE floor_units ADD COLUMN country_code VARCHAR(10) DEFAULT '+971' AFTER owner_phone")
                print("Added country_code column")
            else:
                # Update existing country_code default and existing records
                cursor.execute("ALTER TABLE floor_units ALTER COLUMN country_code SET DEFAULT '+971'")
                cursor.execute("UPDATE floor_units SET country_code = '+971' WHERE country_code = '+91' OR country_code IS NULL")
                print("Updated country_code to Dubai default")

            if 'is_assigned' not in existing_columns:
                cursor.execute("ALTER TABLE floor_units ADD COLUMN is_assigned BOOLEAN DEFAULT FALSE AFTER owner_documents")
                print("Added is_assigned column")

            if 'assigned_at' not in existing_columns:
                cursor.execute("ALTER TABLE floor_units ADD COLUMN assigned_at TIMESTAMP NULL AFTER is_assigned")
                print("Added assigned_at column")

            if 'invitation_token' not in existing_columns:
                cursor.execute("ALTER TABLE floor_units ADD COLUMN invitation_token VARCHAR(255) AFTER assigned_at")
                print("Added invitation_token column")

            if 'invitation_status' not in existing_columns:
                cursor.execute("ALTER TABLE floor_units ADD COLUMN invitation_status ENUM('pending', 'registered', 'expired') DEFAULT NULL AFTER invitation_token")
                print("Added invitation_status column")

            if 'invitation_sent_at' not in existing_columns:
                cursor.execute("ALTER TABLE floor_units ADD COLUMN invitation_sent_at TIMESTAMP NULL AFTER invitation_status")
                print("Added invitation_sent_at column")

            if 'payment_verification_status' not in existing_columns:
                cursor.execute("ALTER TABLE floor_units ADD COLUMN payment_verification_status ENUM('pending', 'submitted', 'approved', 'rejected') DEFAULT 'pending' AFTER invitation_sent_at")
                print("Added payment_verification_status column")

            if 'payment_proof_document' not in existing_columns:
                cursor.execute("ALTER TABLE floor_units ADD COLUMN payment_proof_document LONGBLOB AFTER payment_verification_status")
                print("Added payment_proof_document column")
            else:
                # Update existing column to LONGBLOB for direct binary storage
                cursor.execute("ALTER TABLE floor_units MODIFY COLUMN payment_proof_document LONGBLOB")
                print("Updated payment_proof_document to LONGBLOB")

            if 'id_proof_document' not in existing_columns:
                cursor.execute("ALTER TABLE floor_units ADD COLUMN id_proof_document LONGBLOB AFTER payment_proof_document")
                print("Added id_proof_document column")
            else:
                # Update existing column to LONGBLOB for direct binary storage
                cursor.execute("ALTER TABLE floor_units MODIFY COLUMN id_proof_document LONGBLOB")
                print("Updated id_proof_document to LONGBLOB")

            if 'documents_uploaded_at' not in existing_columns:
                cursor.execute("ALTER TABLE floor_units ADD COLUMN documents_uploaded_at TIMESTAMP NULL AFTER id_proof_document")
                print("Added documents_uploaded_at column")

            if 'verification_notes' not in existing_columns:
                cursor.execute("ALTER TABLE floor_units ADD COLUMN verification_notes TEXT AFTER documents_uploaded_at")
                print("Added verification_notes column")

            # Add individual document verification columns
            if 'payment_proof_verified' not in existing_columns:
                cursor.execute("ALTER TABLE floor_units ADD COLUMN payment_proof_verified BOOLEAN DEFAULT NULL AFTER verification_notes")
                print("Added payment_proof_verified column")

            if 'id_proof_verified' not in existing_columns:
                cursor.execute("ALTER TABLE floor_units ADD COLUMN id_proof_verified BOOLEAN DEFAULT NULL AFTER payment_proof_verified")
                print("Added id_proof_verified column")

            if 'payment_proof_rejected_reason' not in existing_columns:
                cursor.execute("ALTER TABLE floor_units ADD COLUMN payment_proof_rejected_reason TEXT AFTER id_proof_verified")
                print("Added payment_proof_rejected_reason column")

            if 'id_proof_rejected_reason' not in existing_columns:
                cursor.execute("ALTER TABLE floor_units ADD COLUMN id_proof_rejected_reason TEXT AFTER payment_proof_rejected_reason")
                print("Added id_proof_rejected_reason column")

            # Remove old columns if they exist
            if 'unit_type' in existing_columns:
                cursor.execute("ALTER TABLE floor_units DROP COLUMN unit_type")
                print("Removed unit_type column")

            if 'status' in existing_columns:
                cursor.execute("ALTER TABLE floor_units DROP COLUMN status")
                print("Removed status column")

            # Modify owner_documents to LONGTEXT for direct database storage
            cursor.execute("ALTER TABLE floor_units MODIFY COLUMN owner_documents LONGTEXT")
            print("Updated owner_documents to LONGTEXT")

            connection.commit()
            cursor.close()
            connection.close()
            print("Floor units schema updated successfully!")
            return True

        except Exception as e:
            print(f"Error updating floor_units schema: {e}")
            if connection:
                connection.close()
            return False

    def add_country_code_columns(self):
        """Add country_code column to admin, contractors, and snag_inspectors tables"""
        connection = self.get_db_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()
            tables = ['admin', 'contractors', 'snag_inspectors']

            for table in tables:
                # Check if column already exists
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_SCHEMA = %s
                    AND TABLE_NAME = %s
                    AND COLUMN_NAME = 'country_code'
                """, (self.database, table))

                column_exists = cursor.fetchone()[0] > 0

                if not column_exists:
                    # Add the country_code column after phone column
                    cursor.execute(f"""
                        ALTER TABLE {table}
                        ADD COLUMN country_code VARCHAR(10) DEFAULT '+91'
                        AFTER phone
                    """)
                    print(f"country_code column added to {table} table successfully")
                else:
                    print(f"country_code column already exists in {table} table")

            connection.commit()
            cursor.close()
            connection.close()
            return True

        except Exception as e:
            print(f"Error adding country_code columns: {e}")
            if connection:
                connection.close()
            return False

    def initialize_database(self):
        """Initialize the complete database setup"""
        print("Initializing database...")
        self.create_database()
        self.create_tables()
        self.update_database_schema()
        self.update_project_status_enum()
        self.add_unit_type_column()
        self.update_floor_units_schema()
        self.add_country_code_columns()
        self.update_appointments_schema()
        self.update_appointments_table_structure()
        print("Database initialization completed!")

    def update_appointments_schema(self):
        """Create appointments and frozen slots tables"""
        connection = self.get_db_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()

            # Create appointments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS appointments (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    appointment_date DATE NOT NULL,
                    start_time TIME NOT NULL,
                    end_time TIME NOT NULL,
                    status ENUM('scheduled', 'completed', 'cancelled') DEFAULT 'scheduled',
                    created_by INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_appointment_date (appointment_date),
                    INDEX idx_status (status)
                )
            """)
            print("Appointments table created/verified")

            # Create frozen_slots table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS frozen_slots (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    freeze_date DATE NOT NULL,
                    start_time TIME,
                    end_time TIME,
                    freeze_type ENUM('full_day', 'time_slot', 'morning', 'afternoon') DEFAULT 'full_day',
                    reason VARCHAR(255),
                    created_by INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_slot (freeze_date, start_time, end_time),
                    INDEX idx_freeze_date (freeze_date),
                    INDEX idx_freeze_type (freeze_type)
                )
            """)
            print("Frozen slots table created/verified")

            # Create time_slots table for predefined time slots
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS time_slots (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    slot_name VARCHAR(100) NOT NULL,
                    start_time TIME NOT NULL,
                    end_time TIME NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_time_slot (start_time, end_time)
                )
            """)
            print("Time slots table created/verified")

            # Insert default time slots if table is empty
            cursor.execute("SELECT COUNT(*) FROM time_slots")
            count = cursor.fetchone()[0]

            if count == 0:
                default_slots = [
                    ('9:00-9:30', '09:00:00', '09:30:00'),
                    ('9:30-10:00', '09:30:00', '10:00:00'),
                    ('10:00-10:30', '10:00:00', '10:30:00'),
                    ('10:30-11:00', '10:30:00', '11:00:00'),
                    ('11:00-11:30', '11:00:00', '11:30:00'),
                    ('11:30-12:00', '11:30:00', '12:00:00'),
                    ('12:00-12:30', '12:00:00', '12:30:00'),
                    ('12:30-13:00', '12:30:00', '13:00:00'),
                    ('13:00-13:30', '13:00:00', '13:30:00'),
                    ('13:30-14:00', '13:30:00', '14:00:00'),
                    ('14:00-14:30', '14:00:00', '14:30:00'),
                    ('14:30-15:00', '14:30:00', '15:00:00'),
                    ('15:00-15:30', '15:00:00', '15:30:00'),
                    ('15:30-16:00', '15:30:00', '16:00:00')
                ]

                cursor.executemany("""
                    INSERT INTO time_slots (slot_name, start_time, end_time)
                    VALUES (%s, %s, %s)
                """, default_slots)
                print("Default time slots inserted")

            connection.commit()
            cursor.close()
            connection.close()
            return True

        except Exception as e:
            print(f"Error updating appointments schema: {e}")
            if connection:
                connection.close()
            return False

    def update_time_slots_to_30_minutes(self):
        """Update time slots to 30-minute intervals"""
        connection = self.get_db_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()

            # Clear existing time slots
            cursor.execute("DELETE FROM time_slots")
            print("Existing time slots cleared")

            # Insert new 30-minute time slots
            new_slots = [
                ('9:00-9:30', '09:00:00', '09:30:00'),
                ('9:30-10:00', '09:30:00', '10:00:00'),
                ('10:00-10:30', '10:00:00', '10:30:00'),
                ('10:30-11:00', '10:30:00', '11:00:00'),
                ('11:00-11:30', '11:00:00', '11:30:00'),
                ('11:30-12:00', '11:30:00', '12:00:00'),
                ('12:00-12:30', '12:00:00', '12:30:00'),
                ('12:30-13:00', '12:30:00', '13:00:00'),
                ('13:00-13:30', '13:00:00', '13:30:00'),
                ('13:30-14:00', '13:30:00', '14:00:00'),
                ('14:00-14:30', '14:00:00', '14:30:00'),
                ('14:30-15:00', '14:30:00', '15:00:00'),
                ('15:00-15:30', '15:00:00', '15:30:00'),
                ('15:30-16:00', '15:30:00', '16:00:00')
            ]

            cursor.executemany("""
                INSERT INTO time_slots (slot_name, start_time, end_time)
                VALUES (%s, %s, %s)
            """, new_slots)
            print("30-minute time slots inserted")

            connection.commit()
            cursor.close()
            connection.close()
            return True

        except Exception as e:
            print(f"Error updating time slots: {e}")
            if connection:
                connection.close()
            return False

    def update_frozen_slots_enum(self):
        """Update frozen_slots table to include morning and afternoon freeze types"""
        connection = self.get_db_connection()
        if not connection:
            print("Failed to connect to database")
            return False

        try:
            cursor = connection.cursor()

            # Update the freeze_type enum to include morning and afternoon
            cursor.execute("""
                ALTER TABLE frozen_slots
                MODIFY COLUMN freeze_type ENUM('full_day', 'time_slot', 'morning', 'afternoon') DEFAULT 'full_day'
            """)

            connection.commit()
            cursor.close()
            connection.close()
            print("Frozen slots table updated successfully with new freeze types")
            return True

        except Exception as e:
            print(f"Error updating frozen slots table: {e}")
            if connection:
                connection.close()
            return False

    def update_appointments_table_structure(self):
        """Update appointments table to add missing columns"""
        connection = self.get_db_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()

            # Add missing columns to appointments table
            columns_to_add = [
                "ADD COLUMN owner_id INT",
                "ADD COLUMN inspector_id INT",
                "ADD COLUMN unit_id INT",
                "ADD COLUMN notes TEXT",
                "ADD COLUMN acknowledgment_name VARCHAR(255)",
                "ADD COLUMN acknowledgment_phone VARCHAR(20)",
                "ADD COLUMN is_acknowledged BOOLEAN DEFAULT FALSE",
                "ADD COLUMN acknowledged_at TIMESTAMP NULL"
            ]

            for column in columns_to_add:
                try:
                    cursor.execute(f"ALTER TABLE appointments {column}")
                    print(f"Added column: {column}")
                except Exception as e:
                    if "Duplicate column name" not in str(e):
                        print(f"Error adding column {column}: {e}")



            # Add specialization column to snag_inspectors if not exists
            try:
                cursor.execute("ALTER TABLE snag_inspectors ADD COLUMN specialization VARCHAR(255)")
                print("Added specialization column to snag_inspectors")
            except Exception as e:
                if "Duplicate column name" not in str(e):
                    print(f"Error adding specialization column: {e}")

            connection.commit()
            cursor.close()
            connection.close()
            print("Appointments table structure updated successfully")
            return True

        except Exception as e:
            print(f"Error updating appointments table structure: {e}")
            if connection:
                connection.close()
            return False

# Run this file directly to initialize the database
if __name__ == "__main__":
    db = Database()
    conn = db.create_connection()
    if conn:
        print("✅ Connected to MySQL successfully!")
    else:
        print("❌ Database connection failed!")

