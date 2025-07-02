from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
import mysql.connector
from database import Database
from email_service.admin_appointment_email import AdminAppointmentEmailSender
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
db = Database()

def get_db_connection():
    """Get database connection"""
    return db.get_db_connection()

admin_appointment_bp = Blueprint('admin_appointment', __name__, url_prefix='/admin/admin-appointment')

@admin_appointment_bp.route('/api/unit-owners', methods=['GET'])
def get_unit_owners():
    """Get all unit owners for admin appointment scheduling"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT DISTINCT
            fu.id as unit_id,
            fu.unit_number,
            fu.owner_name,
            fu.owner_email,
            fu.owner_phone,
            CONCAT(pf.prefix, ' ', pf.number) as floor_name,
            p.project_name
        FROM floor_units fu
        JOIN project_floors pf ON fu.floor_id = pf.id
        JOIN projects p ON pf.project_id = p.id
        WHERE fu.owner_name IS NOT NULL
        AND fu.owner_name != ''
        ORDER BY p.project_name, CONCAT(pf.prefix, ' ', pf.number), fu.unit_number
        """
        
        cursor.execute(query)
        unit_owners = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify(unit_owners)
        
    except Exception as e:
        logger.error(f"Error fetching unit owners: {str(e)}")
        return jsonify({'error': 'Failed to fetch unit owners'}), 500

@admin_appointment_bp.route('/api/inspectors', methods=['GET'])
def get_inspectors():
    """Get all available inspectors for admin appointment scheduling"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT 
            id as inspector_id,
            name as inspector_name,
            email as inspector_email,
            phone as inspector_phone
        FROM snag_inspectors
        WHERE status = 'active'
        ORDER BY name
        """
        
        cursor.execute(query)
        inspectors = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        return jsonify(inspectors)
        
    except Exception as e:
        logger.error(f"Error fetching inspectors: {str(e)}")
        return jsonify({'error': 'Failed to fetch inspectors'}), 500

@admin_appointment_bp.route('/api/available-slots', methods=['GET'])
def get_available_slots():
    """Get available time slots for a specific date and optionally for a specific inspector"""
    try:
        date = request.args.get('date')
        inspector_id = request.args.get('inspector_id')

        if not date:
            return jsonify({'error': 'Date is required'}), 400
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Get all time slots
        time_slots_query = """
        SELECT id, slot_name, start_time, end_time
        FROM time_slots
        WHERE is_active = TRUE
        ORDER BY start_time
        """
        cursor.execute(time_slots_query)
        all_slots = cursor.fetchall()
        
        # Get booked slots for the date (and optionally for specific inspector)
        if inspector_id:
            booked_slots_query = """
            SELECT start_time, end_time
            FROM appointments
            WHERE appointment_date = %s
            AND inspector_id = %s
            AND status != 'cancelled'
            """
            cursor.execute(booked_slots_query, (date, inspector_id))
        else:
            # If no inspector specified, get all booked slots for the date
            booked_slots_query = """
            SELECT start_time, end_time
            FROM appointments
            WHERE appointment_date = %s
            AND status != 'cancelled'
            """
            cursor.execute(booked_slots_query, (date,))

        booked_appointments = cursor.fetchall()
        booked_slots = []
        for row in booked_appointments:
            try:
                if hasattr(row['start_time'], 'strftime'):
                    start_str = row['start_time'].strftime('%I:%M %p')
                    end_str = row['end_time'].strftime('%I:%M %p')
                else:
                    # Convert string time to 12-hour format
                    from datetime import datetime
                    # Handle different time string formats
                    start_time_str_raw = str(row['start_time'])
                    end_time_str_raw = str(row['end_time'])

                    # Extract time parts and format properly
                    if ':' in start_time_str_raw:
                        start_time_parts = start_time_str_raw.split(':')
                        start_time_formatted = f"{start_time_parts[0]}:{start_time_parts[1]}"
                    else:
                        start_time_formatted = start_time_str_raw[:5]

                    if ':' in end_time_str_raw:
                        end_time_parts = end_time_str_raw.split(':')
                        end_time_formatted = f"{end_time_parts[0]}:{end_time_parts[1]}"
                    else:
                        end_time_formatted = end_time_str_raw[:5]

                    start_time_obj = datetime.strptime(start_time_formatted, '%H:%M')
                    end_time_obj = datetime.strptime(end_time_formatted, '%H:%M')
                    start_str = start_time_obj.strftime('%I:%M %p')
                    end_str = end_time_obj.strftime('%I:%M %p')

                booked_slots.append(f"{start_str} - {end_str}")
            except Exception as e:
                print(f"Error formatting booked appointment time: {e}")
                booked_slots.append(f"{row['start_time']} - {row['end_time']}")
        
        # Get frozen slots for the date
        frozen_slots_query = """
        SELECT start_time, end_time, freeze_type
        FROM frozen_slots
        WHERE freeze_date = %s
        """
        cursor.execute(frozen_slots_query, (date,))
        frozen_slots = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        # Filter available slots
        available_slots = []
        for slot in all_slots:
            # Convert time objects to 12-hour format for display and comparison
            try:
                if hasattr(slot['start_time'], 'strftime'):
                    start_time_str = slot['start_time'].strftime('%I:%M %p')
                    end_time_str = slot['end_time'].strftime('%I:%M %p')
                else:
                    # Convert string time to 12-hour format
                    from datetime import datetime
                    # Handle different time string formats
                    start_time_str_raw = str(slot['start_time'])
                    end_time_str_raw = str(slot['end_time'])

                    # Extract time parts and format properly
                    if ':' in start_time_str_raw:
                        start_time_parts = start_time_str_raw.split(':')
                        start_time_formatted = f"{start_time_parts[0]}:{start_time_parts[1]}"
                    else:
                        start_time_formatted = start_time_str_raw[:5]

                    if ':' in end_time_str_raw:
                        end_time_parts = end_time_str_raw.split(':')
                        end_time_formatted = f"{end_time_parts[0]}:{end_time_parts[1]}"
                    else:
                        end_time_formatted = end_time_str_raw[:5]

                    start_time_obj = datetime.strptime(start_time_formatted, '%H:%M')
                    end_time_obj = datetime.strptime(end_time_formatted, '%H:%M')
                    start_time_str = start_time_obj.strftime('%I:%M %p')
                    end_time_str = end_time_obj.strftime('%I:%M %p')

                slot_time = f"{start_time_str} - {end_time_str}"
            except Exception as e:
                print(f"Error formatting time for slot {slot.get('id', 'unknown')}: {e}")
                # Fallback to original string format
                start_time_str = str(slot['start_time'])
                end_time_str = str(slot['end_time'])
                slot_time = f"{start_time_str} - {end_time_str}"

            # Check if slot is booked
            if slot_time in booked_slots:
                continue

            # Check if slot is frozen
            is_frozen = False
            for frozen in frozen_slots:
                if frozen['freeze_type'] == 'full_day':
                    is_frozen = True
                    break
                elif frozen['freeze_type'] in ['morning', 'afternoon']:
                    # Check if slot falls in frozen session
                    if frozen['freeze_type'] == 'morning' and slot['start_time'] < '12:00:00':
                        is_frozen = True
                        break
                    elif frozen['freeze_type'] == 'afternoon' and slot['start_time'] >= '13:00:00':
                        is_frozen = True
                        break
                elif frozen['freeze_type'] == 'time_slot':
                    if slot['start_time'] == frozen['start_time'] and slot['end_time'] == frozen['end_time']:
                        is_frozen = True
                        break

            if not is_frozen:
                available_slots.append({
                    'id': slot['id'],
                    'name': slot['slot_name'],
                    'start_time': start_time_str,
                    'end_time': end_time_str,
                    'time_slot': slot_time
                })
        
        return jsonify(available_slots)
        
    except Exception as e:
        logger.error(f"Error fetching available slots: {str(e)}")
        return jsonify({'error': 'Failed to fetch available slots'}), 500

@admin_appointment_bp.route('/api/schedule', methods=['POST'])
def schedule_appointment():
    """Schedule appointment by admin"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['appointment_date', 'time_slot', 'unit_id', 'inspector_id', 'title']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400

        appointment_date = data['appointment_date']
        time_slot = data['time_slot']
        unit_id = data['unit_id']
        inspector_id = data['inspector_id']
        title = data['title']
        notes = data.get('notes', '')

        # Get admin info from session
        admin_name = session.get('admin_name', 'Admin')

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Get unit owner details
        unit_query = """
        SELECT
            fu.id as unit_id,
            fu.unit_number,
            fu.owner_name,
            fu.owner_email,
            fu.owner_phone,
            CONCAT(pf.prefix, ' ', pf.number) as floor_name,
            p.project_name
        FROM floor_units fu
        JOIN project_floors pf ON fu.floor_id = pf.id
        JOIN projects p ON pf.project_id = p.id
        WHERE fu.id = %s
        """
        cursor.execute(unit_query, (unit_id,))
        unit_details = cursor.fetchone()

        if not unit_details:
            return jsonify({'error': 'Unit not found'}), 404

        # Get inspector details
        inspector_query = """
        SELECT id, name, email, phone
        FROM snag_inspectors
        WHERE id = %s
        """
        cursor.execute(inspector_query, (inspector_id,))
        inspector_details = cursor.fetchone()

        if not inspector_details:
            return jsonify({'error': 'Inspector not found'}), 404

        # Parse time slot to get start and end times (convert from 12-hour to 24-hour for database)
        start_time_12h, end_time_12h = time_slot.split(' - ')

        try:
            from datetime import datetime
            start_time_obj = datetime.strptime(start_time_12h, '%I:%M %p')
            end_time_obj = datetime.strptime(end_time_12h, '%I:%M %p')
            start_time_str = start_time_obj.strftime('%H:%M:%S')
            end_time_str = end_time_obj.strftime('%H:%M:%S')
        except Exception as e:
            print(f"Error parsing time slot: {e}")
            return jsonify({'error': 'Invalid time slot format'}), 400

        # Check if slot is still available
        check_query = """
        SELECT COUNT(*) as count
        FROM appointments
        WHERE appointment_date = %s
        AND start_time = %s
        AND end_time = %s
        AND inspector_id = %s
        AND status != 'cancelled'
        """
        cursor.execute(check_query, (appointment_date, start_time_str, end_time_str, inspector_id))
        if cursor.fetchone()['count'] > 0:
            return jsonify({'error': 'Time slot is no longer available'}), 400

        # Insert appointment
        insert_query = """
        INSERT INTO appointments (
            owner_id, appointment_date, start_time, end_time, title, description,
            inspector_id, status, created_by, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'scheduled', %s, NOW())
        """

        cursor.execute(insert_query, (
            unit_id, appointment_date, start_time_str, end_time_str, title, notes,
            inspector_id, admin_name
        ))

        appointment_id = cursor.lastrowid
        connection.commit()

        cursor.close()
        connection.close()

        # Send emails
        try:
            email_sender = AdminAppointmentEmailSender()

            # Send email to unit owner
            email_sender.send_owner_notification(
                unit_details, inspector_details,
                appointment_date, time_slot, title, notes, admin_name
            )

            # Send email to inspector
            email_sender.send_inspector_notification(
                unit_details, inspector_details,
                appointment_date, time_slot, title, notes, admin_name
            )

        except Exception as email_error:
            logger.error(f"Error sending emails: {str(email_error)}")
            # Don't fail the appointment creation if email fails

        return jsonify({
            'success': True,
            'message': 'Appointment scheduled successfully',
            'appointment_id': appointment_id
        })

    except Exception as e:
        logger.error(f"Error scheduling appointment: {str(e)}")
        return jsonify({'error': 'Failed to schedule appointment'}), 500

@admin_appointment_bp.route('/api/cancel-appointment/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    """Cancel an appointment by admin"""
    print(f"🔄 Cancel appointment request received for ID: {appointment_id}")

    if 'admin_id' not in session:
        print("❌ Unauthorized - no admin_id in session")
        return jsonify({'error': 'Unauthorized'}), 401

    print("✅ Admin authorized, connecting to database...")

    data = request.get_json()
    cancellation_reason = data.get('reason', '') if data else ''

    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # Get appointment details before cancelling
        cursor.execute("""
            SELECT
                a.id, a.title, a.appointment_date, a.start_time, a.end_time,
                fu.owner_name, fu.owner_email, fu.unit_number,
                CONCAT(pf.prefix, ' ', pf.number) as floor_name,
                p.project_name,
                si.name as inspector_name, si.email as inspector_email
            FROM appointments a
            LEFT JOIN floor_units fu ON a.owner_id = fu.id
            LEFT JOIN project_floors pf ON fu.floor_id = pf.id
            LEFT JOIN projects p ON pf.project_id = p.id
            LEFT JOIN snag_inspectors si ON a.inspector_id = si.id
            WHERE a.id = %s AND a.status = 'scheduled'
        """, (appointment_id,))

        appointment = cursor.fetchone()

        if not appointment:
            cursor.close()
            connection.close()
            return jsonify({'error': 'Appointment not found or already cancelled'}), 404

        # Update appointment status
        cursor.execute("""
            UPDATE appointments
            SET status = 'cancelled',
                cancelled_by = 'admin',
                cancelled_at = NOW(),
                cancellation_reason = %s,
                can_rebook = 1
            WHERE id = %s
        """, (cancellation_reason, appointment_id))

        connection.commit()
        cursor.close()
        connection.close()

        # Send cancellation emails to both owner and inspector
        try:
            from email_service.appointment_email_sender import send_cancellation_email
            from email_service.appointment_email_sender import AppointmentEmailSender

            print(f"📧 Appointment data for emails: {appointment}")
            print(f"📧 Owner email: {appointment.get('owner_email')}")
            print(f"📧 Inspector email: {appointment.get('inspector_email')}")

            # Send to owner
            if appointment.get('owner_email'):
                try:
                    owner_success, owner_msg = send_cancellation_email(appointment, cancellation_reason)
                    if owner_success:
                        print(f"✅ Cancellation email sent to owner: {appointment['owner_email']}")
                    else:
                        print(f"❌ Failed to send cancellation email to owner: {owner_msg}")
                except Exception as owner_email_error:
                    print(f"❌ Error sending cancellation email to owner: {owner_email_error}")
            else:
                print("❌ No owner email found")

            # Send to inspector
            if appointment.get('inspector_email'):
                try:
                    email_sender = AppointmentEmailSender()
                    inspector_success, inspector_msg = email_sender.send_cancellation_email_to_inspector(
                        appointment, cancellation_reason
                    )
                    if inspector_success:
                        print(f"✅ Cancellation email sent to inspector: {appointment['inspector_email']}")
                    else:
                        print(f"❌ Failed to send cancellation email to inspector: {inspector_msg}")
                except Exception as inspector_email_error:
                    print(f"❌ Error sending cancellation email to inspector: {inspector_email_error}")
            else:
                print("❌ No inspector email found")

        except Exception as email_error:
            print(f"❌ General error sending cancellation emails: {email_error}")
            import traceback
            print(f"❌ Full traceback: {traceback.format_exc()}")
            # Don't fail the cancellation if email fails

        return jsonify({
            'success': True,
            'message': 'Appointment cancelled successfully',
            'appointment': {
                'id': appointment_id,
                'status': 'cancelled',
                'cancelled_by': 'admin',
                'cancellation_reason': cancellation_reason
            }
        })

    except Exception as e:
        logger.error(f"Error cancelling appointment: {str(e)}")
        if connection:
            connection.rollback()
            connection.close()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
