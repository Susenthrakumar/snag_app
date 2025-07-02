from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from database import Database
from datetime import datetime, date, timedelta
import json

appointments_bp = Blueprint('appointments', __name__, url_prefix='/admin/appointments')
db = Database()

@appointments_bp.route('/')
def appointments():
    """Main appointments page with calendar"""
    if 'admin_id' not in session:
        return redirect(url_for('login'))

    print("Appointments page accessed successfully")
    return render_template('admin/appointments.html')

@appointments_bp.route('/api/calendar-data')
def api_calendar_data():
    """Get calendar data for appointments and frozen slots"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Get appointments
        cursor.execute("""
            SELECT id, title, description, appointment_date, start_time, end_time, status
            FROM appointments
            WHERE appointment_date BETWEEN %s AND %s
            ORDER BY appointment_date, start_time
        """, (start_date, end_date))
        
        appointments = cursor.fetchall()

        # Get frozen slots
        cursor.execute("""
            SELECT id, freeze_date, start_time, end_time, freeze_type, reason
            FROM frozen_slots
            WHERE freeze_date BETWEEN %s AND %s
            ORDER BY freeze_date, start_time
        """, (start_date, end_date))
        
        frozen_slots = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        # Format data for FullCalendar
        events = []
        
        # Add appointments - invisible events for date highlighting only
        for appointment in appointments:
            appointment_event = {
                'id': f'appointment_{appointment["id"]}',
                'title': '',  # Empty title to make invisible
                'start': f"{appointment['appointment_date']}T{appointment['start_time']}",
                'end': f"{appointment['appointment_date']}T{appointment['end_time']}",
                'backgroundColor': 'transparent',  # Transparent to hide
                'borderColor': 'transparent',  # Transparent to hide
                'textColor': 'transparent',  # Transparent to hide
                'display': 'none',  # Hide the event
                'extendedProps': {
                    'type': 'appointment',
                    'description': appointment['description'],
                    'status': appointment['status']
                }
            }
            events.append(appointment_event)
        
        # Add frozen slots - red for full day, violet for sessions/slots
        for slot in frozen_slots:
            if slot['freeze_type'] == 'full_day':
                events.append({
                    'id': f'frozen_{slot["id"]}',
                    'title': '●',
                    'start': slot['freeze_date'].strftime('%Y-%m-%d'),
                    'allDay': True,
                    'backgroundColor': '#dc3545',  # Red for full day
                    'borderColor': '#dc3545',
                    'textColor': 'white',
                    'extendedProps': {
                        'type': 'frozen_day',
                        'reason': slot['reason'],
                        'slot_id': slot['id']
                    }
                })
            elif slot['freeze_type'] == 'morning':
                events.append({
                    'id': f'frozen_{slot["id"]}',
                    'title': '●',
                    'start': f"{slot['freeze_date']}T09:00:00",
                    'end': f"{slot['freeze_date']}T12:00:00",
                    'backgroundColor': '#6f42c1',  # Violet for half session
                    'borderColor': '#6f42c1',
                    'textColor': 'white',
                    'extendedProps': {
                        'type': 'frozen_session',
                        'reason': slot['reason'],
                        'slot_id': slot['id']
                    }
                })
            elif slot['freeze_type'] == 'afternoon':
                events.append({
                    'id': f'frozen_{slot["id"]}',
                    'title': '●',
                    'start': f"{slot['freeze_date']}T13:00:00",
                    'end': f"{slot['freeze_date']}T16:00:00",
                    'backgroundColor': '#6f42c1',  # Violet for half session
                    'borderColor': '#6f42c1',
                    'textColor': 'white',
                    'extendedProps': {
                        'type': 'frozen_session',
                        'reason': slot['reason'],
                        'slot_id': slot['id']
                    }
                })
            else:
                events.append({
                    'id': f'frozen_{slot["id"]}',
                    'title': '●',
                    'start': f"{slot['freeze_date']}T{slot['start_time']}",
                    'end': f"{slot['freeze_date']}T{slot['end_time']}",
                    'backgroundColor': '#6f42c1',  # Violet for individual slots
                    'borderColor': '#6f42c1',
                    'textColor': 'white',
                    'extendedProps': {
                        'type': 'frozen_slot',
                        'reason': slot['reason'],
                        'slot_id': slot['id']
                    }
                })
        
        return jsonify(events)
        
    except Exception as e:
        print(f"Error fetching calendar data: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to fetch calendar data'}), 500

@appointments_bp.route('/api/time-slots')
def api_time_slots():
    """Get available time slots"""
    if 'admin_id' not in session:
        print("Unauthorized access to time slots API")
        return jsonify({'error': 'Unauthorized'}), 401

    connection = db.get_db_connection()
    if not connection:
        print("Database connection failed for time slots API")
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, slot_name, start_time, end_time
            FROM time_slots
            WHERE is_active = TRUE
            ORDER BY start_time
        """)

        slots = cursor.fetchall()
        print(f"Retrieved {len(slots)} time slots from database")
        cursor.close()
        connection.close()
        
        # Format time slots
        formatted_slots = []
        for slot in slots:
            try:
                # Handle both datetime.time and string formats
                if hasattr(slot['start_time'], 'strftime'):
                    start_time_str = slot['start_time'].strftime('%I:%M %p')
                    end_time_str = slot['end_time'].strftime('%I:%M %p')
                else:
                    # Convert string time to 12-hour format
                    from datetime import datetime
                    # Handle different time string formats
                    start_time_str_raw = str(slot['start_time'])
                    end_time_str_raw = str(slot['end_time'])

                    # Extract HH:MM part (handle both HH:MM and HH:MM:SS formats)
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

                formatted_slots.append({
                    'id': slot['id'],
                    'name': slot['slot_name'],
                    'start_time': start_time_str,
                    'end_time': end_time_str,
                    'display': f"{start_time_str} - {end_time_str}"
                })
            except Exception as e:
                print(f"Error formatting slot {slot['id']}: {e}")
                # Fallback formatting
                formatted_slots.append({
                    'id': slot['id'],
                    'name': slot['slot_name'],
                    'start_time': str(slot['start_time']),
                    'end_time': str(slot['end_time']),
                    'display': f"{str(slot['start_time'])} - {str(slot['end_time'])}"
                })

        print(f"Returning {len(formatted_slots)} formatted time slots")
        return jsonify(formatted_slots)

    except Exception as e:
        print(f"Error fetching time slots: {e}")
        import traceback
        traceback.print_exc()
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to fetch time slots'}), 500

@appointments_bp.route('/api/freeze-slot', methods=['POST'])
def api_freeze_slot():
    """Freeze a date or time slot"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    freeze_date = data.get('date')
    freeze_type = data.get('type', 'full_day')  # 'full_day', 'time_slot', 'morning', 'afternoon'
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    reason = data.get('reason', '')

    print(f"Freeze request received: date={freeze_date}, type={freeze_type}, start_time={start_time}, end_time={end_time}, reason={reason}")

    if not freeze_date:
        return jsonify({'error': 'Date is required'}), 400
    
    if freeze_type in ['time_slot', 'morning', 'afternoon'] and (not start_time or not end_time):
        return jsonify({'error': 'Start time and end time are required for this freeze type'}), 400
    
    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()

        # First, remove any existing freezes for this date to replace with new freeze
        cursor.execute("DELETE FROM frozen_slots WHERE freeze_date = %s", (freeze_date,))
        print(f"Removed existing freezes for date: {freeze_date}")

        # Insert the new freeze
        cursor.execute("""
            INSERT INTO frozen_slots (freeze_date, start_time, end_time, freeze_type, reason, created_by)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (freeze_date, start_time, end_time, freeze_type, reason, session['admin_id']))

        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({
            'success': True,
            'message': f'{"Date" if freeze_type == "full_day" else "Time slot"} frozen successfully'
        })
        
    except Exception as e:
        print(f"Error freezing slot: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to freeze slot'}), 500

@appointments_bp.route('/api/unfreeze-slot-old', methods=['POST'])
def api_unfreeze_slot_old():
    """Unfreeze a date or time slot"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    slot_id = data.get('slot_id')
    
    if not slot_id:
        return jsonify({'error': 'Slot ID is required'}), 400
    
    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    
    try:
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM frozen_slots WHERE id = %s", (slot_id,))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            'success': True,
            'message': 'Slot unfrozen successfully'
        })
        
    except Exception as e:
        print(f"Error unfreezing slot: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to unfreeze slot'}), 500

@appointments_bp.route('/api/check-frozen-slots')
def api_check_frozen_slots():
    """Check if specific date/time slots are frozen"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    date = request.args.get('date')
    if not date:
        return jsonify({'error': 'Date is required'}), 400

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, start_time, end_time, freeze_type, reason
            FROM frozen_slots
            WHERE freeze_date = %s
            ORDER BY start_time
        """, (date,))

        frozen_slots = cursor.fetchall()
        cursor.close()
        connection.close()

        # Format frozen slots
        formatted_slots = []
        for slot in frozen_slots:
            formatted_slots.append({
                'id': slot['id'],
                'start_time': str(slot['start_time']) if slot['start_time'] else None,
                'end_time': str(slot['end_time']) if slot['end_time'] else None,
                'freeze_type': slot['freeze_type'],
                'reason': slot['reason']
            })

        return jsonify(formatted_slots)

    except Exception as e:
        print(f"Error checking frozen slots: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to check frozen slots'}), 500

@appointments_bp.route('/api/date-details/<date>')
def get_date_details(date):
    """Get detailed information for a specific date"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # Get appointments for this date with unit owner and inspector details
        cursor.execute("""
            SELECT
                a.id, a.title, a.description, a.start_time, a.end_time, a.status,
                a.cancelled_by, a.cancelled_at, a.cancellation_reason, a.can_rebook,
                fu.owner_name, fu.owner_email, fu.owner_phone,
                CONCAT(pf.prefix, ' ', pf.number) as floor_name,
                p.project_name, fu.unit_number,
                si.name as inspector_name, si.specialization, si.phone as inspector_phone, si.email as inspector_email
            FROM appointments a
            LEFT JOIN floor_units fu ON a.owner_id = fu.id
            LEFT JOIN project_floors pf ON fu.floor_id = pf.id
            LEFT JOIN projects p ON pf.project_id = p.id
            LEFT JOIN snag_inspectors si ON a.inspector_id = si.id
            WHERE a.appointment_date = %s
            ORDER BY a.start_time
        """, (date,))

        appointments = cursor.fetchall()

        # Get frozen slots for this date
        cursor.execute("""
            SELECT id, start_time, end_time, freeze_type, reason
            FROM frozen_slots
            WHERE freeze_date = %s
            ORDER BY start_time
        """, (date,))

        frozen_slots = cursor.fetchall()

        cursor.close()
        connection.close()

        # Generate all possible time slots (9:00 AM to 4:00 PM, 30-minute intervals)
        all_slots = []
        from datetime import datetime, timedelta

        start_time = datetime.strptime('09:00', '%H:%M')
        end_time = datetime.strptime('16:00', '%H:%M')

        current_time = start_time
        while current_time < end_time:
            next_time = current_time + timedelta(minutes=30)
            slot_text = f"{current_time.strftime('%I:%M %p')} - {next_time.strftime('%I:%M %p')}"
            all_slots.append({
                'time': slot_text,
                'start_time': current_time.time(),
                'end_time': next_time.time()
            })
            current_time = next_time

        # Determine which slots are frozen
        frozen_times = set()
        frozen_slot_details = []

        for slot in frozen_slots:
            if slot['freeze_type'] == 'full_day':
                # All slots are frozen
                frozen_times.update([s['time'] for s in all_slots])
                frozen_slot_details.append({
                    'freeze_type': 'full_day',
                    'time_range': 'Full Day',
                    'reason': slot['reason'],
                    'start_time': '09:00',
                    'end_time': '16:00',
                    'slot_id': slot['id']
                })
            elif slot['freeze_type'] == 'morning':
                # Morning slots (9:00 AM - 12:00 PM)
                morning_slots = [s['time'] for s in all_slots if s['start_time'] < datetime.strptime('12:00', '%H:%M').time()]
                frozen_times.update(morning_slots)
                frozen_slot_details.append({
                    'freeze_type': 'morning',
                    'time_range': '9:00 AM - 12:00 PM',
                    'reason': slot['reason'],
                    'start_time': '09:00',
                    'end_time': '12:00',
                    'slot_id': slot['id']
                })
            elif slot['freeze_type'] == 'afternoon':
                # Afternoon slots (1:00 PM - 4:00 PM)
                afternoon_slots = [s['time'] for s in all_slots if s['start_time'] >= datetime.strptime('13:00', '%H:%M').time()]
                frozen_times.update(afternoon_slots)
                frozen_slot_details.append({
                    'freeze_type': 'afternoon',
                    'time_range': '1:00 PM - 4:00 PM',
                    'reason': slot['reason'],
                    'start_time': '13:00',
                    'end_time': '16:00',
                    'slot_id': slot['id']
                })
            else:
                # Individual time slot
                if slot['start_time'] and slot['end_time']:
                    try:
                        # Handle both datetime.time and string formats
                        if hasattr(slot['start_time'], 'strftime'):
                            start_str = slot['start_time'].strftime('%I:%M %p')
                            end_str = slot['end_time'].strftime('%I:%M %p')
                        else:
                            # Convert to string and handle different formats
                            start_time_str = str(slot['start_time'])
                            end_time_str = str(slot['end_time'])

                            # Remove microseconds if present
                            if '.' in start_time_str:
                                start_time_str = start_time_str.split('.')[0]
                            if '.' in end_time_str:
                                end_time_str = end_time_str.split('.')[0]

                            # Parse time strings
                            start_time_obj = datetime.strptime(start_time_str, '%H:%M:%S').time()
                            end_time_obj = datetime.strptime(end_time_str, '%H:%M:%S').time()

                            start_str = datetime.combine(datetime.today(), start_time_obj).strftime('%I:%M %p')
                            end_str = datetime.combine(datetime.today(), end_time_obj).strftime('%I:%M %p')

                        slot_text = f"{start_str} - {end_str}"
                        frozen_times.add(slot_text)
                        frozen_slot_details.append({
                            'freeze_type': 'slot',
                            'time_slot': slot_text,
                            'reason': slot['reason'],
                            'start_time': str(slot['start_time'])[:5] if slot['start_time'] else '',
                            'end_time': str(slot['end_time'])[:5] if slot['end_time'] else '',
                            'slot_id': slot['id']
                        })
                    except Exception as time_error:
                        print(f"Error parsing time for slot {slot['id']}: {time_error}")
                        # Skip this slot if time parsing fails
                        continue

        # Format appointments
        formatted_appointments = []
        for apt in appointments:
            if apt['start_time'] and apt['end_time']:
                try:
                    # Handle both datetime.time and string formats
                    if hasattr(apt['start_time'], 'strftime'):
                        start_str = apt['start_time'].strftime('%I:%M %p')
                        end_str = apt['end_time'].strftime('%I:%M %p')
                    else:
                        # Convert to string and handle different formats
                        start_time_str = str(apt['start_time'])
                        end_time_str = str(apt['end_time'])

                        # Remove microseconds if present
                        if '.' in start_time_str:
                            start_time_str = start_time_str.split('.')[0]
                        if '.' in end_time_str:
                            end_time_str = end_time_str.split('.')[0]

                        # Parse time strings
                        start_time_obj = datetime.strptime(start_time_str, '%H:%M:%S').time()
                        end_time_obj = datetime.strptime(end_time_str, '%H:%M:%S').time()

                        start_str = datetime.combine(datetime.today(), start_time_obj).strftime('%I:%M %p')
                        end_str = datetime.combine(datetime.today(), end_time_obj).strftime('%I:%M %p')

                    formatted_appointments.append({
                        'id': apt['id'],
                        'title': apt['title'],
                        'time_slot': f"{start_str} - {end_str}",
                        'description': apt['description'],
                        'status': apt['status'],
                        'client_name': apt.get('owner_name', 'Client'),
                        'owner_name': apt.get('owner_name'),
                        'owner_email': apt.get('owner_email'),
                        'owner_phone': apt.get('owner_phone'),
                        'unit_number': apt.get('unit_number'),
                        'floor_name': apt.get('floor_name'),
                        'project_name': apt.get('project_name'),
                        'inspector_name': apt.get('inspector_name'),
                        'inspector_specialization': apt.get('specialization'),
                        'inspector_phone': apt.get('inspector_phone'),
                        'inspector_email': apt.get('inspector_email'),
                        'cancelled_by': apt.get('cancelled_by'),
                        'cancelled_at': apt.get('cancelled_at'),
                        'cancellation_reason': apt.get('cancellation_reason'),
                        'can_rebook': apt.get('can_rebook', 0)
                    })
                except Exception as time_error:
                    print(f"Error parsing time for appointment {apt['id']}: {time_error}")
                    # Skip this appointment if time parsing fails
                    continue

        # Get available slots
        available_slots = [slot['time'] for slot in all_slots if slot['time'] not in frozen_times]

        return jsonify({
            'success': True,
            'data': {
                'date': date,
                'appointments': formatted_appointments,
                'frozen_slots': frozen_slot_details,
                'available_slots': available_slots,
                'total_slots': len(all_slots),
                'frozen_count': len(frozen_times),
                'available_count': len(available_slots)
            }
        })

    except Exception as e:
        print(f"Error fetching date details: {e}")
        if connection:
            connection.close()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@appointments_bp.route('/api/appointment-details/<int:appointment_id>')
def get_appointment_details(appointment_id):
    """Get detailed information for a specific appointment"""
    print(f"🎯 Appointment details requested for ID: {appointment_id}")
    print(f"🔐 Session admin_id: {session.get('admin_id')}")

    if 'admin_id' not in session:
        print("❌ Unauthorized access to appointment details")
        return jsonify({'error': 'Unauthorized'}), 401

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # Get appointment details with unit owner and inspector info
        cursor.execute("""
            SELECT
                a.id, a.title, a.description, a.appointment_date, a.start_time, a.end_time, a.status,
                a.cancelled_by, a.cancelled_at, a.cancellation_reason, a.can_rebook,
                a.is_acknowledged, a.acknowledgment_name, a.acknowledgment_phone, a.acknowledged_at,
                fu.owner_name, fu.owner_email, fu.owner_phone, fu.country_code,
                CONCAT(pf.prefix, ' ', pf.number) as floor_name,
                p.project_name, fu.unit_number,
                si.name as inspector_name, si.specialization, si.phone as inspector_phone, si.email as inspector_email
            FROM appointments a
            LEFT JOIN floor_units fu ON a.owner_id = fu.id
            LEFT JOIN project_floors pf ON fu.floor_id = pf.id
            LEFT JOIN projects p ON pf.project_id = p.id
            LEFT JOIN snag_inspectors si ON a.inspector_id = si.id
            WHERE a.id = %s
        """, (appointment_id,))

        appointment = cursor.fetchone()
        cursor.close()
        connection.close()

        if not appointment:
            return jsonify({'error': 'Appointment not found'}), 404

        # Format time display (handle timedelta objects from MySQL TIME columns)
        def format_time(time_obj):
            if not time_obj:
                return 'N/A'
            if isinstance(time_obj, timedelta):
                # Convert timedelta to hours and minutes
                total_seconds = int(time_obj.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                # Format as 12-hour time
                if hours == 0:
                    return f"12:{minutes:02d} AM"
                elif hours < 12:
                    return f"{hours}:{minutes:02d} AM"
                elif hours == 12:
                    return f"12:{minutes:02d} PM"
                else:
                    return f"{hours-12}:{minutes:02d} PM"
            else:
                return time_obj.strftime('%I:%M %p')

        start_str = format_time(appointment['start_time'])
        end_str = format_time(appointment['end_time'])

        formatted_appointment = {
            'id': appointment['id'],
            'title': appointment['title'],
            'description': appointment['description'],
            'appointment_date': appointment['appointment_date'].strftime('%Y-%m-%d') if appointment['appointment_date'] else None,
            'time_slot': f"{start_str} - {end_str}",
            'status': appointment['status'],
            'owner_name': appointment['owner_name'],
            'owner_email': appointment['owner_email'],
            'owner_phone': appointment['owner_phone'],
            'country_code': appointment['country_code'],
            'unit_number': appointment['unit_number'],
            'floor_name': appointment['floor_name'],
            'project_name': appointment['project_name'],
            'inspector_name': appointment['inspector_name'],
            'inspector_specialization': appointment['specialization'],
            'inspector_phone': appointment['inspector_phone'],
            'inspector_email': appointment['inspector_email'],
            'cancelled_by': appointment['cancelled_by'],
            'cancelled_at': appointment['cancelled_at'].strftime('%Y-%m-%d %H:%M:%S') if appointment['cancelled_at'] else None,
            'cancellation_reason': appointment['cancellation_reason'],
            'can_rebook': appointment['can_rebook'],
            'is_acknowledged': appointment['is_acknowledged'],
            'acknowledgment_name': appointment['acknowledgment_name'],
            'acknowledgment_phone': appointment['acknowledgment_phone'],
            'acknowledged_at': appointment['acknowledged_at'].strftime('%Y-%m-%d %H:%M:%S') if appointment['acknowledged_at'] else None
        }

        return jsonify({
            'success': True,
            'data': formatted_appointment
        })

    except Exception as e:
        print(f"Error fetching appointment details: {e}")
        if connection:
            connection.close()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@appointments_bp.route('/api/cancel-appointment', methods=['POST'])
def cancel_appointment():
    """Cancel an appointment by admin"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    appointment_id = data.get('appointment_id')
    cancellation_reason = data.get('reason', '')

    if not appointment_id:
        return jsonify({'error': 'Appointment ID is required'}), 400

    connection = db.get_db_connection()
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
            'message': 'Appointment cancelled successfully'
        })

    except Exception as e:
        print(f"Error cancelling appointment: {e}")
        if connection:
            connection.rollback()
            connection.close()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@appointments_bp.route('/api/unfreeze-slot', methods=['POST'])
def unfreeze_slot():
    """Unfreeze a specific slot"""
    try:
        if 'admin_id' not in session:
            print("Unauthorized access attempt")
            return jsonify({'error': 'Unauthorized'}), 401

        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data received'}), 400

        slot_id = data.get('slot_id')
        date = data.get('date')
        freeze_type = data.get('freeze_type')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        # If slot_id is provided, use it directly
        if slot_id:
            connection = db.get_db_connection()
            if not connection:
                return jsonify({'error': 'Database connection failed'}), 500

            try:
                cursor = connection.cursor()
                result = cursor.execute("DELETE FROM frozen_slots WHERE id = %s", (slot_id,))
                affected_rows = cursor.rowcount

                connection.commit()
                cursor.close()
                connection.close()

                if affected_rows > 0:
                    return jsonify({
                        'success': True,
                        'message': 'Slot unfrozen successfully'
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Slot not found'
                    }), 404

            except Exception as e:
                if connection:
                    connection.rollback()
                    connection.close()
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500

        # Fallback to date/time based deletion
        if not date or not freeze_type:
            return jsonify({'error': 'Missing required parameters'}), 400

        connection = db.get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection failed'}), 500

        try:
            cursor = connection.cursor()

            if freeze_type in ['full_day', 'morning', 'afternoon']:
                cursor.execute("""
                    DELETE FROM frozen_slots
                    WHERE freeze_date = %s AND freeze_type = %s
                """, (date, freeze_type))
            else:
                cursor.execute("""
                    DELETE FROM frozen_slots
                    WHERE freeze_date = %s AND start_time = %s AND end_time = %s
                """, (date, start_time, end_time))

            affected_rows = cursor.rowcount

            connection.commit()
            cursor.close()
            connection.close()

            if affected_rows > 0:
                return jsonify({
                    'success': True,
                    'message': 'Slot unfrozen successfully'
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'No matching slot found'
                }), 404

        except Exception as e:
            if connection:
                connection.rollback()
                connection.close()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@appointments_bp.route('/api/unit-bookings/<int:unit_id>')
def get_unit_bookings(unit_id):
    """Get all existing bookings for a specific unit owner"""
    if 'admin_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    connection = db.get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        # Get unit owner details
        cursor.execute("""
            SELECT fu.owner_name, fu.owner_email, fu.owner_phone, fu.unit_number,
                   CONCAT(pf.prefix, ' ', pf.number) as floor_name,
                   p.project_name
            FROM floor_units fu
            JOIN project_floors pf ON fu.floor_id = pf.id
            JOIN projects p ON pf.project_id = p.id
            WHERE fu.id = %s
        """, (unit_id,))

        unit_owner = cursor.fetchone()
        if not unit_owner:
            return jsonify({'error': 'Unit owner not found'}), 404

        # Get all appointments for this unit owner
        cursor.execute("""
            SELECT a.id, a.title, a.description, a.appointment_date,
                   a.start_time, a.end_time, a.status,
                   a.cancelled_by, a.cancelled_at, a.cancellation_reason,
                   i.name as inspector_name, i.email as inspector_email
            FROM appointments a
            LEFT JOIN snag_inspectors i ON a.inspector_id = i.id
            WHERE a.owner_id = %s
            ORDER BY a.appointment_date DESC, a.start_time DESC
        """, (unit_id,))

        appointments = cursor.fetchall()

        # Helper function to format time from timedelta
        def format_time_from_timedelta(td):
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

        # Helper function to format time string
        def format_time_string(time_str):
            try:
                # Handle both HH:MM and HH:MM:SS formats
                if len(time_str.split(':')) == 3:
                    time_obj = datetime.strptime(time_str, '%H:%M:%S')
                else:
                    time_obj = datetime.strptime(time_str, '%H:%M')
                return time_obj.strftime('%I:%M %p')
            except:
                return time_str

        # Format time fields for JSON serialization
        for appointment in appointments:
            if appointment['start_time']:
                if isinstance(appointment['start_time'], timedelta):
                    appointment['start_time'] = format_time_from_timedelta(appointment['start_time'])
                else:
                    appointment['start_time'] = format_time_string(str(appointment['start_time']))

            if appointment['end_time']:
                if isinstance(appointment['end_time'], timedelta):
                    appointment['end_time'] = format_time_from_timedelta(appointment['end_time'])
                else:
                    appointment['end_time'] = format_time_string(str(appointment['end_time']))

            if appointment['appointment_date']:
                appointment['appointment_date'] = appointment['appointment_date'].strftime('%Y-%m-%d')

        return jsonify({
            'success': True,
            'unit_owner': unit_owner,
            'appointments': appointments
        })

    except Exception as e:
        print(f"Error getting unit bookings: {e}")
        if connection:
            connection.close()
        return jsonify({'error': 'Failed to get unit bookings'}), 500
    finally:
        if connection:
            connection.close()
