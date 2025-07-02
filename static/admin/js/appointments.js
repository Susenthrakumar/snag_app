// Appointments Management JavaScript

let calendar;
let selectedTimeSlot = null;
let timeSlots = [];

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM Content Loaded - Initializing appointments page');
    initializeCalendar();
    loadTimeSlots();

    // Add event listener for date changes
    document.getElementById('freezeDate').addEventListener('change', function() {
        if (document.getElementById('freezeType').value === 'time_slot') {
            checkFrozenSlots();
        }
    });

    // Set minimum dates to today
    setMinimumDates();

    // Add real-time validation listeners
    addValidationListeners();

    // Add event listener for freeze form submission
    document.getElementById('freezeForm').addEventListener('submit', function(e) {
        e.preventDefault();

        // Comprehensive validation
        if (!validateFreezeForm()) {
            return;
        }

        const dateSelectionType = document.getElementById('dateSelectionType').value;
        const freezeType = document.getElementById('freezeType').value;
        const reason = document.getElementById('freezeReason').value;

        let dates = [];

        // Get dates based on selection type
        if (dateSelectionType === 'single') {
            const singleDate = document.getElementById('freezeDate').value;
            if (singleDate) dates.push(singleDate);
        } else if (dateSelectionType === 'multiple') {
            // Get all multiple date inputs
            const dateInputs = document.querySelectorAll('#multipleDatesContainer input[type="date"]');
            dateInputs.forEach(input => {
                if (input.value) dates.push(input.value);
            });
        } else if (dateSelectionType === 'range') {
            const startDate = document.getElementById('startDate').value;
            const endDate = document.getElementById('endDate').value;
            if (startDate && endDate) {
                dates = getDateRange(startDate, endDate);
            }
        }

        let startTime = null;
        let endTime = null;

        if (freezeType === 'time_slot') {
            if (selectedTimeSlot) {
                startTime = selectedTimeSlot.start_time;
                endTime = selectedTimeSlot.end_time;
                console.log('Selected time slot:', selectedTimeSlot);
            } else {
                console.error('No time slot selected for time_slot freeze type');
                showAlert('Please select a time slot to freeze', 'warning');
                return;
            }
        } else if (freezeType === 'morning') {
            startTime = '09:00';
            endTime = '12:00';
            console.log('Setting morning session times:', startTime, endTime);
        } else if (freezeType === 'afternoon') {
            startTime = '13:00';
            endTime = '16:00';
            console.log('Setting afternoon session times:', startTime, endTime);
        }

        console.log('Freeze request data:', {
            dates: dates,
            freezeType: freezeType,
            startTime: startTime,
            endTime: endTime,
            reason: reason
        });

        // Freeze all selected dates
        freezeMultipleDates(dates, freezeType, startTime, endTime, reason);
    });
});

// Initialize Bootstrap tooltips
function initializeTooltips() {
    // Initialize tooltips for legend items
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            trigger: 'hover',
            placement: 'top',
            html: true
        });
    });
}

// Comprehensive validation function for freeze form
function validateFreezeForm() {
    const dateSelectionType = document.getElementById('dateSelectionType').value;
    const freezeType = document.getElementById('freezeType').value;

    // Clear previous error indicators
    clearValidationErrors();

    let isValid = true;
    let errorMessages = [];

    // Validate date selection based on type
    if (dateSelectionType === 'single') {
        const singleDate = document.getElementById('freezeDate').value;
        if (!singleDate) {
            showFieldError('freezeDate', 'Please select a date');
            errorMessages.push('Please select a date');
            isValid = false;
        } else if (!isValidFutureDate(singleDate)) {
            showFieldError('freezeDate', 'Please select a future date');
            errorMessages.push('Please select a future date');
            isValid = false;
        }
    } else if (dateSelectionType === 'range') {
        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;

        if (!startDate) {
            showFieldError('startDate', 'Please select start date');
            errorMessages.push('Please select start date');
            isValid = false;
        }
        if (!endDate) {
            showFieldError('endDate', 'Please select end date');
            errorMessages.push('Please select end date');
            isValid = false;
        }

        if (startDate && endDate) {
            if (!isValidFutureDate(startDate)) {
                showFieldError('startDate', 'Start date must be today or future');
                errorMessages.push('Start date must be today or future');
                isValid = false;
            }
            if (new Date(endDate) < new Date(startDate)) {
                showFieldError('endDate', 'End date must be after start date');
                errorMessages.push('End date must be after start date');
                isValid = false;
            }
        }
    } else if (dateSelectionType === 'multiple') {
        const dateInputs = document.querySelectorAll('#multipleDatesContainer input[type="date"]');
        let hasValidDate = false;

        dateInputs.forEach((input) => {
            if (input.value) {
                if (isValidFutureDate(input.value)) {
                    hasValidDate = true;
                } else {
                    showFieldError(input.id, 'Must be today or future date');
                    isValid = false;
                }
            }
        });

        if (!hasValidDate) {
            errorMessages.push('Please select at least one valid date');
            isValid = false;
        }
    }

    // Validate time slot selection for specific time slot freeze
    if (freezeType === 'time_slot' && !selectedTimeSlot) {
        errorMessages.push('Please select a time slot to freeze');
        isValid = false;
    }

    // Show consolidated error message if validation fails
    if (!isValid) {
        showAlert(errorMessages[0], 'warning');
    }

    return isValid;
}

// Helper function to check if date is today or future
function isValidFutureDate(dateString) {
    const selectedDate = new Date(dateString);
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Reset time to start of day
    return selectedDate >= today;
}

// Show field-specific error
function showFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    if (field) {
        field.classList.add('is-invalid');

        // Remove existing error message
        const existingError = field.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }

        // Add new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        field.parentNode.appendChild(errorDiv);
    }
}

// Clear all validation errors
function clearValidationErrors() {
    // Remove error classes
    document.querySelectorAll('.is-invalid').forEach(field => {
        field.classList.remove('is-invalid');
    });

    // Remove error messages
    document.querySelectorAll('.invalid-feedback').forEach(error => {
        error.remove();
    });
}

// Add real-time validation listeners
function addValidationListeners() {
    // Clear errors when user starts typing/selecting
    const dateInputs = ['freezeDate', 'startDate', 'endDate'];
    dateInputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        if (input) {
            input.addEventListener('change', function() {
                if (this.classList.contains('is-invalid')) {
                    this.classList.remove('is-invalid');
                    const errorMsg = this.parentNode.querySelector('.invalid-feedback');
                    if (errorMsg) {
                        errorMsg.remove();
                    }
                }
            });
        }
    });

    // Clear errors for multiple date inputs (dynamically added)
    document.addEventListener('change', function(e) {
        if (e.target.type === 'date' && e.target.classList.contains('is-invalid')) {
            e.target.classList.remove('is-invalid');
            const errorMsg = e.target.parentNode.querySelector('.invalid-feedback');
            if (errorMsg) {
                errorMsg.remove();
            }
        }
    });
}

function initializeCalendar() {
    const calendarEl = document.getElementById('calendar');
    
    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        headerToolbar: {
            left: 'prev',
            center: 'title',
            right: 'next'
        },
        height: 'auto',
        events: '/admin/appointments/api/calendar-data',
        eventClick: function(info) {
            handleEventClick(info);
        },
        dateClick: function(info) {
            handleDateClick(info);
        },
        eventDidMount: function(info) {
            // Add tooltips to events
            if (info.event.extendedProps.description) {
                info.el.title = info.event.extendedProps.description;
            }
        },
        datesSet: function(info) {
            // Add light green highlighting to dates with appointments
            setTimeout(() => {
                highlightAppointmentDates();
            }, 200);
        },
        eventsSet: function(events) {
            // Store events for highlighting appointment dates
            window.calendarEvents = events;
            // Add a small delay to ensure DOM is ready
            setTimeout(() => {
                highlightAppointmentDates();
            }, 100);
        }
    });
    
    calendar.render();

    // Make calendar globally accessible
    window.calendar = calendar;

    // Initialize tooltips for legend items
    initializeTooltips();
}

function openFreezeModal() {
    console.log('Opening freeze modal...');

    try {
        // Reset form
        const freezeForm = document.getElementById('freezeForm');
        if (freezeForm) {
            freezeForm.reset();
        }

        // Reset date selection to single
        document.getElementById('dateSelectionType').value = 'single';
        toggleDateInputs();

        // Clear additional date inputs
        document.getElementById('additionalDates').innerHTML = '';

        const timeSlotsContainer = document.getElementById('timeSlotsContainer');
        if (timeSlotsContainer) {
            timeSlotsContainer.style.display = 'none';
        }

        selectedTimeSlot = null;

        // Clear any existing selections
        document.querySelectorAll('.time-slot-item').forEach(item => {
            item.classList.remove('selected');
        });

        console.log('Modal opened - selectedTimeSlot reset to null');

        // Set minimum dates
        setMinimumDates();

        // Show modal
        const modalElement = document.getElementById('freezeModal');
        if (modalElement) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
            console.log('Modal should be visible now');
        } else {
            console.error('Modal element not found');
        }
    } catch (error) {
        console.error('Error opening freeze modal:', error);
    }
}

function toggleDateSelection() {
    const freezeType = document.getElementById('freezeType').value;
    const container = document.getElementById('timeSlotsContainer');

    if (freezeType === 'time_slot') {
        container.style.display = 'block';
        loadTimeSlots();
        checkFrozenSlots();
    } else {
        container.style.display = 'none';
        selectedTimeSlot = null;
    }
}

function toggleDateInputs() {
    const dateSelectionType = document.getElementById('dateSelectionType').value;

    // Hide all containers
    document.getElementById('singleDateContainer').style.display = 'none';
    document.getElementById('multipleDatesContainer').style.display = 'none';
    document.getElementById('dateRangeContainer').style.display = 'none';

    // Show selected container
    if (dateSelectionType === 'single') {
        document.getElementById('singleDateContainer').style.display = 'block';
    } else if (dateSelectionType === 'multiple') {
        document.getElementById('multipleDatesContainer').style.display = 'block';
    } else if (dateSelectionType === 'range') {
        document.getElementById('dateRangeContainer').style.display = 'block';
    }
}

function addDateInput() {
    const container = document.getElementById('additionalDates');
    const dateCount = container.children.length + 2; // +2 for the first input and this new one

    const dateInputDiv = document.createElement('div');
    dateInputDiv.className = 'mb-2 d-flex gap-2';
    dateInputDiv.innerHTML = `
        <input type="date" class="form-control" id="multipleDate${dateCount}">
        <button type="button" class="btn btn-outline-danger btn-sm" onclick="removeDateInput(this)">
            <i class="fas fa-trash"></i>
        </button>
    `;

    container.appendChild(dateInputDiv);
    setMinimumDates();
}

function removeDateInput(button) {
    button.parentElement.remove();
}

function setMinimumDates() {
    const today = new Date().toISOString().split('T')[0];
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        input.min = today;
    });
}

function checkFrozenSlots() {
    const selectedDate = document.getElementById('freezeDate').value;
    if (!selectedDate) return;

    fetch(`/admin/appointments/api/check-frozen-slots?date=${selectedDate}`)
        .then(response => response.json())
        .then(frozenSlots => {
            updateTimeSlotsDisplay(frozenSlots);
        })
        .catch(error => {
            console.error('Error checking frozen slots:', error);
        });
}

function updateTimeSlotsDisplay(frozenSlots) {
    const container = document.getElementById('timeSlotsList');
    const slotItems = container.querySelectorAll('.time-slot-item');

    slotItems.forEach(item => {
        item.classList.remove('frozen');
        const frozenIndicator = item.querySelector('.frozen-indicator');
        if (frozenIndicator) {
            frozenIndicator.remove();
        }
    });

    // Mark frozen slots
    frozenSlots.forEach(frozenSlot => {
        if (frozenSlot.freeze_type === 'time_slot') {
            slotItems.forEach(item => {
                const slotData = timeSlots.find(slot =>
                    slot.start_time === frozenSlot.start_time &&
                    slot.end_time === frozenSlot.end_time
                );

                if (slotData) {
                    item.classList.add('frozen');
                    item.style.opacity = '0.5';
                    item.style.pointerEvents = 'none';

                    const frozenIndicator = document.createElement('div');
                    frozenIndicator.className = 'frozen-indicator';
                    frozenIndicator.innerHTML = '<i class="fas fa-snowflake text-danger"></i> Already Frozen';
                    item.appendChild(frozenIndicator);
                }
            });
        }
    });
}

function loadTimeSlots() {
    console.log('Loading time slots...');
    fetch('/admin/appointments/api/time-slots')
        .then(response => {
            console.log('Time slots response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Time slots data received:', data);
            if (Array.isArray(data)) {
                timeSlots = data;
                console.log('Time slots loaded successfully:', timeSlots.length, 'slots');
                renderTimeSlots();
            } else {
                console.error('Invalid time slots data:', data);
                showAlert(data.error || 'Error loading time slots', 'danger');
            }
        })
        .catch(error => {
            console.error('Error loading time slots:', error);
            showAlert('Error loading time slots', 'danger');
        });
}

function renderTimeSlots() {
    const container = document.getElementById('timeSlotsList');
    container.innerHTML = '';
    
    timeSlots.forEach(slot => {
        const slotDiv = document.createElement('div');
        slotDiv.className = 'time-slot-item';
        slotDiv.onclick = () => selectTimeSlot(slot, slotDiv);
        slotDiv.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <strong>${slot.name}</strong>
                    <div class="text-muted">${slot.start_time} - ${slot.end_time}</div>
                </div>
                <i class="fas fa-clock"></i>
            </div>
        `;
        container.appendChild(slotDiv);
    });
}

function selectTimeSlot(slot, element) {
    // Remove previous selection
    document.querySelectorAll('.time-slot-item').forEach(item => {
        item.classList.remove('selected');
    });
    
    // Add selection to clicked item
    element.classList.add('selected');
    selectedTimeSlot = slot;

    console.log('Time slot selected:', selectedTimeSlot);
}

function getDateRange(startDate, endDate) {
    const dates = [];
    const start = new Date(startDate);
    const end = new Date(endDate);

    for (let date = new Date(start); date <= end; date.setDate(date.getDate() + 1)) {
        dates.push(date.toISOString().split('T')[0]);
    }

    return dates;
}

function freezeMultipleDates(dates, type, startTime, endTime, reason) {
    let completedRequests = 0;
    let failedRequests = 0;

    dates.forEach(date => {
        freezeSlot(date, type, startTime, endTime, reason, false)
            .then(success => {
                completedRequests++;
                if (!success) failedRequests++;

                // Check if all requests completed
                if (completedRequests === dates.length) {
                    // Refresh calendar
                    if (typeof calendar !== 'undefined' && calendar && calendar.refetchEvents) {
                        calendar.refetchEvents();
                    } else if (window.calendar && window.calendar.refetchEvents) {
                        window.calendar.refetchEvents();
                    }

                    // Close modal
                    bootstrap.Modal.getInstance(document.getElementById('freezeModal'))?.hide();

                    if (failedRequests > 0) {
                        showAlert(`${dates.length - failedRequests} dates frozen successfully, ${failedRequests} failed`, 'warning');
                    } else {
                        showAlert(`${dates.length} date(s) frozen successfully`, 'success');
                    }
                }
            });
    });
}

function freezeSlot(date, type, startTime, endTime, reason, showErrors = true) {
    const data = {
        date: date,
        type: type,
        start_time: startTime,
        end_time: endTime,
        reason: reason
    };

    return fetch('/admin/appointments/api/freeze-slot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            return true;
        } else {
            if (showErrors) {
                showAlert(data.error || 'Failed to freeze slot', 'danger');
            }
            return false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (showErrors) {
            showAlert('Failed to freeze slot', 'danger');
        }
        return false;
    });
}

function handleEventClick(info) {
    // Prevent event propagation to avoid double popup
    info.jsEvent.stopPropagation();

    const event = info.event;
    const props = event.extendedProps;

    // For frozen events, show date details popup
    if (props.type === 'frozen_day' || props.type === 'frozen_slot' || props.type === 'frozen_session') {
        const clickedDate = event.start.toISOString().split('T')[0];
        handleDateClick({ dateStr: clickedDate });
    }
}

// Handle date click to show date details popup
function handleDateClick(info) {
    const clickedDate = info.dateStr;
    console.log('Date clicked:', clickedDate);

    // Fetch date details directly without loading state
    fetch(`/admin/appointments/api/date-details/${clickedDate}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            showDateDetailsPopup(clickedDate, data);
        })
        .catch(error => {
            console.error('Error fetching date details:', error);
            // Show popup with error information
            showDateDetailsPopup(clickedDate, {
                success: false,
                error: 'Failed to load date details'
            });
        });
}

// Show date details popup
function showDateDetailsPopup(date, data) {
    // Close any existing modals and clean up backdrop
    const currentModal = document.getElementById('dateDetailsModal');
    if (currentModal) {
        const modalInstance = bootstrap.Modal.getInstance(currentModal);
        if (modalInstance) {
            modalInstance.hide();
        }
        currentModal.remove();
    }

    // Remove any leftover modal backdrops
    const backdrops = document.querySelectorAll('.modal-backdrop');
    backdrops.forEach(backdrop => backdrop.remove());

    // Reset body classes
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';

    const formattedDate = new Date(date).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });

    let content = '';

    if (data && data.success) {
        const details = data.data;

        content = `
            <div class="date-details-content">
                <!-- Appointments Section -->
                <div class="mb-4">
                    <h6 class="fw-bold text-primary mb-3">
                        <i class="fas fa-calendar-check me-2"></i>Scheduled Appointments
                    </h6>
                    ${details.appointments && details.appointments.length > 0 ?
                        details.appointments.map(apt => `
                            <div class="appointment-item p-3 mb-2 border rounded-3" style="background-color: #f8f9fa;">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div>
                                        <strong>${apt.time_slot}</strong>
                                        <span class="badge ${apt.status === 'cancelled' ? 'bg-danger' : 'bg-success'} ms-2">
                                            ${apt.status === 'cancelled' ? 'Cancelled' : 'Booked'}
                                        </span>
                                        ${apt.cancelled_by ? `<small class="text-muted d-block">Cancelled by: ${apt.cancelled_by}</small>` : ''}
                                    </div>
                                    <div class="d-flex align-items-center">
                                        <small class="text-muted me-2">${apt.client_name || 'Client'}</small>
                                        <button class="btn btn-sm btn-outline-primary" onclick="viewAppointmentDetails(${apt.id})" title="View Details">
                                            <i class="fas fa-eye"></i>
                                        </button>
                                    </div>
                                </div>
                            </div>
                        `).join('') :
                        '<p class="text-muted fst-italic">No appointments scheduled</p>'
                    }
                </div>

                <!-- Frozen Slots Section -->
                <div class="mb-4">
                    <h6 class="fw-bold text-warning mb-3">
                        <i class="fas fa-snowflake me-2"></i>Frozen Time Slots
                    </h6>
                    ${details.frozen_slots && details.frozen_slots.length > 0 ?
                        details.frozen_slots.map(slot => {
                            let badgeClass = 'bg-danger';
                            let icon = 'fas fa-ban';

                            if (slot.freeze_type === 'morning') {
                                badgeClass = 'bg-warning';
                                icon = 'fas fa-sun';
                            } else if (slot.freeze_type === 'afternoon') {
                                badgeClass = 'bg-info';
                                icon = 'fas fa-moon';
                            }

                            return `
                                <div class="frozen-slot-item p-3 mb-2 border rounded-3" style="background-color: #fff3cd;">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <div>
                                            <i class="${icon} me-2"></i>
                                            <strong>${slot.time_range || slot.time_slot}</strong>
                                            <span class="badge ${badgeClass} ms-2">${slot.freeze_type.charAt(0).toUpperCase() + slot.freeze_type.slice(1)}</span>
                                        </div>
                                        <button class="btn btn-sm btn-outline-danger" onclick="unfreezeSlotFromPopup('${date}', '${slot.freeze_type}', '${slot.start_time}', '${slot.end_time}', '${slot.slot_id || ''}')">
                                            <i class="fas fa-fire me-1"></i>Unfreeze
                                        </button>
                                    </div>
                                    ${slot.reason ? `<small class="text-muted d-block mt-1">Reason: ${slot.reason}</small>` : ''}
                                </div>
                            `;
                        }).join('') :
                        '<p class="text-muted fst-italic">No frozen slots</p>'
                    }
                </div>


            </div>
        `;
    } else {
        // Show a more user-friendly message for dates with no data
        content = `
            <div class="text-center py-4">
                <i class="fas fa-calendar-times text-muted fa-2x mb-3"></i>
                <h5>No Details Available</h5>
                <p class="text-muted">This date has no appointments or frozen slots.</p>
                <button class="btn btn-primary btn-sm mt-2" onclick="openSlotFreezeModal('${date}')" style="border-radius: 25px;">
                    <i class="fas fa-snowflake me-1"></i>Freeze Slots
                </button>
            </div>
        `;
    }

    // Create and show modal
    const modalHtml = `
        <div class="modal fade" id="dateDetailsModal" tabindex="-1" aria-labelledby="dateDetailsModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content" style="border-radius: 20px;">
                    <div class="modal-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 20px 20px 0 0;">
                        <h5 class="modal-title" id="dateDetailsModalLabel">
                            <i class="fas fa-calendar-day me-2"></i>${formattedDate}
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body" style="max-height: 70vh; overflow-y: auto;">
                        ${content}
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if any
    const existingModal = document.getElementById('dateDetailsModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('dateDetailsModal'));
    modal.show();

    // Clean up modal when hidden
    document.getElementById('dateDetailsModal').addEventListener('hidden.bs.modal', function() {
        this.remove();

        // Clean up any remaining backdrops
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => backdrop.remove());

        // Reset body classes and styles
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
    });
}

// Open slot freeze modal with pre-selected date
function openSlotFreezeModal(date) {
    // Close date details modal first
    const dateDetailsModal = bootstrap.Modal.getInstance(document.getElementById('dateDetailsModal'));
    if (dateDetailsModal) {
        dateDetailsModal.hide();
    }

    // Open freeze modal and set the date
    setTimeout(() => {
        document.getElementById('slotFreezeBtn').click();

        // Wait for modal to open and set the date
        setTimeout(() => {
            const singleDateRadio = document.getElementById('singleDate');
            const dateInput = document.getElementById('freezeDate');

            if (singleDateRadio && dateInput) {
                singleDateRadio.checked = true;
                dateInput.value = date;

                // Trigger change event to show date input
                singleDateRadio.dispatchEvent(new Event('change'));
            }
        }, 300);
    }, 300);
}

// Admin Appointment Scheduling Functions
function openScheduleAppointmentModal() {
    // Clear any existing booking notification when modal opens
    const existingNotification = document.querySelector('.existing-booking-notification');
    if (existingNotification) {
        existingNotification.remove();
    }

    // Reset form fields
    const form = document.getElementById('scheduleAppointmentForm');
    if (form) {
        form.reset();
    }

    // Set default appointment title
    const appointmentTitle = document.getElementById('appointmentTitle');
    if (appointmentTitle) {
        appointmentTitle.value = 'Property Investigation';
    }

    // Clear dropdowns
    const timeSlotSelect = document.getElementById('appointmentTimeSlot');
    if (timeSlotSelect) {
        timeSlotSelect.innerHTML = '<option value="">Select Time Slot</option>';
    }

    const modal = new bootstrap.Modal(document.getElementById('scheduleAppointmentModal'));

    // Load unit owners and inspectors
    loadUnitOwners();
    loadInspectors();

    // Set minimum date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('appointmentDate').min = today;

    modal.show();
}

// Clear notifications when modal is hidden and setup event listeners
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM Content Loaded - Setting up event listeners');

    const scheduleModal = document.getElementById('scheduleAppointmentModal');
    if (scheduleModal) {
        scheduleModal.addEventListener('hidden.bs.modal', function() {
            // Clear any existing booking notification when modal is closed
            const existingNotification = document.querySelector('.existing-booking-notification');
            if (existingNotification) {
                existingNotification.remove();
            }
        });
    }

    // Event listener for unit owner selection is now added dynamically in loadUnitOwners()
    console.log('ℹ️ Unit owner event listener will be added after dropdown is populated');
});

function loadUnitOwners() {
    console.log('📡 Loading unit owners from API...');
    fetch('/admin/admin-appointment/api/unit-owners')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('unitOwnerSelect');
            select.innerHTML = '<option value="">Select Unit Owner</option>';

            data.forEach(owner => {
                const option = document.createElement('option');
                option.value = owner.unit_id;
                option.textContent = `${owner.owner_name} - ${owner.unit_number} (${owner.project_name})`;
                option.dataset.ownerEmail = owner.owner_email;
                option.dataset.ownerPhone = owner.owner_phone;
                option.dataset.projectName = owner.project_name;
                option.dataset.floorName = owner.floor_name;
                select.appendChild(option);
            });

            // Add event listener for unit owner selection after dropdown is populated
            console.log('✅ Unit owners loaded, adding event listener');
            select.removeEventListener('change', handleUnitOwnerChange); // Remove existing listener if any
            select.addEventListener('change', handleUnitOwnerChange);
        })
        .catch(error => {
            console.error('Error loading unit owners:', error);
            showAlert('Error loading unit owners', 'danger');
        });
}

// Separate function to handle unit owner change
function handleUnitOwnerChange(event) {
    console.log('🔄 Unit owner selection changed to:', event.target.value);
    checkExistingBookingsForUnitOwner(event.target.value);
}

function loadInspectors() {
    console.log('📡 Loading inspectors from API...');
    fetch('/admin/admin-appointment/api/inspectors')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('inspectorSelect');
            select.innerHTML = '<option value="">Select Inspector</option>';

            data.forEach(inspector => {
                const option = document.createElement('option');
                option.value = inspector.inspector_id;
                option.textContent = `${inspector.inspector_name} - ${inspector.inspector_phone}`;
                option.dataset.inspectorEmail = inspector.inspector_email;
                option.dataset.inspectorPhone = inspector.inspector_phone;
                select.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading inspectors:', error);
            showAlert('Error loading inspectors', 'danger');
        });
}

function checkExistingBookingsForUnitOwner(unitId) {
    console.log('🔍 Checking existing bookings for unit ID:', unitId);

    if (!unitId) {
        console.log('❌ No unit ID provided, removing notification');
        // Remove any existing booking notification when no unit owner is selected
        const existingNotification = document.querySelector('.existing-booking-notification');
        if (existingNotification) {
            existingNotification.remove();
        }
        return;
    }

    // Remove any existing booking notification
    const existingNotification = document.querySelector('.existing-booking-notification');
    if (existingNotification) {
        existingNotification.remove();
    }

    console.log('📡 Making API call to:', `/admin/appointments/api/unit-bookings/${unitId}`);

    fetch(`/admin/appointments/api/unit-bookings/${unitId}`)
        .then(response => {
            console.log('📡 API Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('📡 API Response data:', data);

            if (data.success && data.appointments && data.appointments.length > 0) {
                console.log('✅ Found appointments:', data.appointments.length);
                const scheduledAppointments = data.appointments.filter(apt => apt.status === 'scheduled');
                console.log('✅ Scheduled appointments:', scheduledAppointments.length);

                if (scheduledAppointments.length > 0) {
                    console.log('🚨 Showing notification for existing bookings');
                    showExistingBookingNotificationForUnitOwner(scheduledAppointments, data.unit_owner);
                } else {
                    console.log('ℹ️ No scheduled appointments found');
                }
            } else {
                console.log('ℹ️ No appointments found or API error');
            }
        })
        .catch(error => {
            console.error('❌ Error checking existing bookings for unit owner:', error);
        });
}

function showExistingBookingNotificationForUnitOwner(appointments, unitOwner) {
    const modal = document.getElementById('scheduleAppointmentModal');
    const modalBody = modal.querySelector('.modal-body');

    // Remove any existing notification first
    const existingNotification = document.querySelector('.existing-booking-notification');
    if (existingNotification) {
        existingNotification.remove();
    }

    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'existing-booking-notification alert alert-warning mb-3';
    notification.style.cssText = `
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        border: 1px solid #ffc107;
        border-radius: 8px;
        padding: 12px 16px;
        margin-bottom: 15px;
        font-size: 13px;
        box-shadow: 0 2px 4px rgba(255, 193, 7, 0.1);
    `;

    const appointmentsList = appointments.map(apt =>
        `<div style="margin: 4px 0; padding: 4px 8px; background: rgba(255,255,255,0.7); border-radius: 4px;" data-appointment-id="${apt.id}">
            <strong>${new Date(apt.appointment_date).toLocaleDateString()}</strong> - ${apt.start_time} to ${apt.end_time}
            <br><small style="color: #666;">Status: ${apt.status.charAt(0).toUpperCase() + apt.status.slice(1)}</small>
            ${apt.status === 'scheduled' ? `
                <button type="button" class="btn btn-sm btn-outline-danger ms-2"
                        onclick="cancelAppointmentFromNotification(${apt.id})"
                        style="font-size: 10px; padding: 2px 6px;">
                    <i class="fas fa-times"></i> Cancel
                </button>
            ` : ''}
        </div>`
    ).join('');

    // Store appointment IDs as data attribute
    const appointmentIds = appointments.map(apt => apt.id).join(',');
    notification.setAttribute('data-appointment-ids', appointmentIds);

    notification.innerHTML = `
        <div style="display: flex; align-items: flex-start; gap: 8px;">
            <i class="fas fa-exclamation-triangle" style="color: #ff8c00; margin-top: 2px; font-size: 14px;"></i>
            <div style="flex: 1;">
                <strong style="color: #856404; font-size: 13px;"> ${unitOwner.owner_name} Already Has Existing Bookings</strong>
                <div style="margin-top: 6px;">
                    ${appointmentsList}
                </div>
                <small style="color: #856404; font-style: italic; margin-top: 4px; display: block;">
                    Please verify before scheduling additional appointments
                </small>
            </div>
        </div>
    `;

    // Insert at the beginning of modal body
    modalBody.insertBefore(notification, modalBody.firstChild);
}

function loadAvailableTimeSlots() {
    const date = document.getElementById('appointmentDate').value;
    const inspectorId = document.getElementById('inspectorSelect').value;

    if (!date) {
        document.getElementById('appointmentTimeSlot').innerHTML = '<option value="">Select Time Slot</option>';
        return;
    }

    // If no inspector selected, show all time slots for the date
    let url = `/admin/admin-appointment/api/available-slots?date=${date}`;
    if (inspectorId) {
        url += `&inspector_id=${inspectorId}`;
    }

    fetch(url)
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('appointmentTimeSlot');
            select.innerHTML = '<option value="">Select Time Slot</option>';

            if (data.length === 0) {
                const option = document.createElement('option');
                option.value = '';
                option.textContent = 'No available slots';
                option.disabled = true;
                select.appendChild(option);
            } else {
                data.forEach(slot => {
                    const option = document.createElement('option');
                    option.value = slot.time_slot;
                    option.textContent = slot.time_slot; // Only show 12-hour format
                    select.appendChild(option);
                });
            }
        })
        .catch(error => {
            console.error('Error loading available slots:', error);
            showAlert('Error loading available time slots', 'danger');
        });
}

// Event listeners for schedule appointment form
document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners for date and inspector changes
    const appointmentDate = document.getElementById('appointmentDate');
    const inspectorSelect = document.getElementById('inspectorSelect');

    if (appointmentDate) {
        appointmentDate.addEventListener('change', loadAvailableTimeSlots);
    }

    if (inspectorSelect) {
        inspectorSelect.addEventListener('change', loadAvailableTimeSlots);
    }

    // Add event listener for unit owner selection (moved to DOMContentLoaded)
    // This is now handled in the DOMContentLoaded event listener below

    // Handle schedule appointment form submission
    const scheduleForm = document.getElementById('scheduleAppointmentForm');
    if (scheduleForm) {
        scheduleForm.addEventListener('submit', function(e) {
            e.preventDefault();
            scheduleAppointment();
        });
    }
});

function scheduleAppointment() {
    const formData = {
        appointment_date: document.getElementById('appointmentDate').value,
        time_slot: document.getElementById('appointmentTimeSlot').value,
        unit_id: document.getElementById('unitOwnerSelect').value,
        inspector_id: document.getElementById('inspectorSelect').value,
        title: document.getElementById('appointmentTitle').value,
        notes: document.getElementById('appointmentNotes').value
    };

    // Validate required fields
    if (!formData.appointment_date || !formData.time_slot || !formData.unit_id ||
        !formData.inspector_id || !formData.title) {
        showAlert('Please fill in all required fields', 'danger');
        return;
    }

    // Show loading state
    const submitBtn = document.querySelector('#scheduleAppointmentForm button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Scheduling...';
    submitBtn.disabled = true;

    fetch('/admin/admin-appointment/api/schedule', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessPopup('Appointment scheduled successfully! Emails sent to unit owner and inspector.');

            // Close modal and reset form
            const modal = bootstrap.Modal.getInstance(document.getElementById('scheduleAppointmentModal'));
            modal.hide();
            document.getElementById('scheduleAppointmentForm').reset();

            // Refresh calendar
            calendar.refetchEvents();
        } else {
            showAlert(data.error || 'Error scheduling appointment', 'danger');
        }
    })
    .catch(error => {
        console.error('Error scheduling appointment:', error);
        showAlert('Error scheduling appointment', 'danger');
    })
    .finally(() => {
        // Restore button state
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
}

// Unfreeze slot from date details popup
function unfreezeSlotFromPopup(date, freezeType, startTime, endTime, slotId) {

    const data = {
        date: date,
        freeze_type: freezeType,
        start_time: startTime,
        end_time: endTime
    };

    // Add slot_id if available
    if (slotId && slotId !== '' && slotId !== 'undefined') {
        data.slot_id = slotId;
    }

    fetch('/admin/appointments/api/unfreeze-slot', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Close the current modal first
            const modal = document.getElementById('dateDetailsModal');
            if (modal) {
                const modalInstance = bootstrap.Modal.getInstance(modal);
                if (modalInstance) {
                    modalInstance.hide();
                }
            }

            // Try to refresh the calendar
            try {
                if (typeof calendar !== 'undefined' && calendar && calendar.refetchEvents) {
                    calendar.refetchEvents();
                } else if (window.calendar && window.calendar.refetchEvents) {
                    window.calendar.refetchEvents();
                }
            } catch (error) {
                console.log('Calendar refresh failed, will reload page as fallback');
                // Reload page to show changes if calendar refresh fails
                setTimeout(() => {
                    window.location.reload();
                }, 500);
            }

            // Don't reopen the modal - let user click again if they want to see updated details
        } else {
            // Only show error if it's a real error, not just missing data
            if (data.error && data.error !== 'No matching slot found' && data.error !== 'Slot not found') {
                console.error('Unfreeze error:', data.error);
            }
        }
    })
    .catch(error => {
        console.error('Error unfreezing slot:', error);
        // Silently handle errors and reload page to show changes
        setTimeout(() => {
            window.location.reload();
        }, 500);
    });
}

// View appointment details function
function viewAppointmentDetails(appointmentId) {
    console.log('Viewing appointment details for ID:', appointmentId);

    // Fetch appointment details
    fetch(`/admin/appointments/api/appointment-details/${appointmentId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                showAppointmentDetailsModal(data.data);
            } else {
                alert('Error loading appointment details: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error fetching appointment details:', error);
            alert('Failed to load appointment details. Please try again.');
        });
}

// Show appointment details modal
function showAppointmentDetailsModal(appointment) {
    // Close any existing modals
    const existingModal = document.getElementById('appointmentDetailsModal');
    if (existingModal) {
        const modalInstance = bootstrap.Modal.getInstance(existingModal);
        if (modalInstance) {
            modalInstance.hide();
        }
        existingModal.remove();
    }

    // Remove any leftover modal backdrops
    const backdrops = document.querySelectorAll('.modal-backdrop');
    backdrops.forEach(backdrop => backdrop.remove());

    // Reset body classes
    document.body.classList.remove('modal-open');
    document.body.style.overflow = '';
    document.body.style.paddingRight = '';

    // Create modal HTML
    const modalHtml = `
        <div class="modal fade" id="appointmentDetailsModal" tabindex="-1" aria-labelledby="appointmentDetailsModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-lg">
                <div class="modal-content" style="border-radius: 15px;">
                    <div class="modal-header" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px 15px 0 0;">
                        <h5 class="modal-title" id="appointmentDetailsModalLabel">
                            <i class="fas fa-calendar-check me-2"></i>Appointment Details
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body" style="max-height: 70vh; overflow-y: auto;">
                        <div class="appointment-details-content">
                            <!-- Appointment Status -->
                            <div class="mb-4">
                                <div class="d-flex justify-content-between align-items-center mb-3">
                                    <h6 class="fw-bold text-primary mb-0">
                                        <i class="fas fa-info-circle me-2"></i>Appointment Status
                                    </h6>
                                    <span class="badge ${appointment.status === 'cancelled' ? 'bg-danger' : 'bg-success'} fs-6">
                                        ${appointment.status === 'cancelled' ? 'Cancelled' : 'Scheduled'}
                                    </span>
                                </div>
                                ${appointment.status === 'cancelled' ? `
                                    <div class="alert alert-warning">
                                        <strong>Cancelled by:</strong> ${appointment.cancelled_by}<br>
                                        <strong>Cancelled on:</strong> ${appointment.cancelled_at}<br>
                                        ${appointment.cancellation_reason ? `<strong>Reason:</strong> ${appointment.cancellation_reason}` : ''}
                                    </div>
                                ` : ''}
                            </div>

                            <!-- Appointment Information -->
                            <div class="mb-4">
                                <h6 class="fw-bold text-primary mb-3">
                                    <i class="fas fa-calendar-alt me-2"></i>Appointment Information
                                </h6>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="info-item p-3 mb-2 border rounded-3" style="background-color: #f8f9fa;">
                                            <strong>Date:</strong> ${appointment.appointment_date}
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="info-item p-3 mb-2 border rounded-3" style="background-color: #f8f9fa;">
                                            <strong>Time:</strong> ${appointment.time_slot}
                                        </div>
                                    </div>
                                </div>
                                <div class="info-item p-3 mb-2 border rounded-3" style="background-color: #f8f9fa;">
                                    <strong>Title:</strong> ${appointment.title}
                                </div>
                                ${appointment.description ? `
                                    <div class="info-item p-3 mb-2 border rounded-3" style="background-color: #f8f9fa;">
                                        <strong>Description:</strong> ${appointment.description}
                                    </div>
                                ` : ''}
                            </div>

                            <!-- Unit Owner Information -->
                            <div class="mb-4">
                                <h6 class="fw-bold text-success mb-3">
                                    <i class="fas fa-user me-2"></i>Unit Owner Information
                                </h6>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="info-item p-3 mb-2 border rounded-3" style="background-color: #e8f5e8;">
                                            <strong>Name:</strong> ${appointment.owner_name || 'N/A'}
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="info-item p-3 mb-2 border rounded-3" style="background-color: #e8f5e8;">
                                            <strong>Email:</strong> ${appointment.owner_email || 'N/A'}
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="info-item p-3 mb-2 border rounded-3" style="background-color: #e8f5e8;">
                                            <strong>Phone:</strong> ${appointment.country_code || ''}${appointment.owner_phone || 'N/A'}
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="info-item p-3 mb-2 border rounded-3" style="background-color: #e8f5e8;">
                                            <strong>Unit:</strong> ${appointment.project_name} - ${appointment.floor_name} Unit ${appointment.unit_number}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Inspector Information -->
                            <div class="mb-4">
                                <h6 class="fw-bold text-warning mb-3">
                                    <i class="fas fa-user-tie me-2"></i>SNAG Inspector Information
                                </h6>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="info-item p-3 mb-2 border rounded-3" style="background-color: #fff3cd;">
                                            <strong>Name:</strong> ${appointment.inspector_name || 'N/A'}
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="info-item p-3 mb-2 border rounded-3" style="background-color: #fff3cd;">
                                            <strong>Specialization:</strong> ${appointment.inspector_specialization || 'N/A'}
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="info-item p-3 mb-2 border rounded-3" style="background-color: #fff3cd;">
                                            <strong>Phone:</strong> ${appointment.inspector_phone || 'N/A'}
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="info-item p-3 mb-2 border rounded-3" style="background-color: #fff3cd;">
                                            <strong>Email:</strong> ${appointment.inspector_email || 'N/A'}
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Acknowledgment Information -->
                            ${appointment.is_acknowledged ? `
                                <div class="mb-4">
                                    <h6 class="fw-bold text-info mb-3">
                                        <i class="fas fa-check-circle me-2"></i>Acknowledgment Information
                                    </h6>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="info-item p-3 mb-2 border rounded-3" style="background-color: #d1ecf1;">
                                                <strong>Acknowledged by:</strong> ${appointment.acknowledgment_name || 'N/A'}
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <div class="info-item p-3 mb-2 border rounded-3" style="background-color: #d1ecf1;">
                                                <strong>Phone:</strong> ${appointment.acknowledgment_phone || 'N/A'}
                                            </div>
                                        </div>
                                    </div>
                                    <div class="info-item p-3 mb-2 border rounded-3" style="background-color: #d1ecf1;">
                                        <strong>Acknowledged on:</strong> ${appointment.acknowledged_at || 'N/A'}
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                    <div class="modal-footer">
                        ${appointment.status === 'scheduled' ? `
                            <button type="button" class="btn btn-danger" onclick="showCancelAppointmentModal(${appointment.id})">
                                <i class="fas fa-times me-1"></i>Cancel Appointment
                            </button>
                        ` : ''}
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('appointmentDetailsModal'));
    modal.show();

    // Clean up modal when hidden
    document.getElementById('appointmentDetailsModal').addEventListener('hidden.bs.modal', function() {
        this.remove();

        // Clean up any remaining backdrops
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => backdrop.remove());

        // Reset body classes and styles
        document.body.classList.remove('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
    });
}

// Show cancel appointment modal
function showCancelAppointmentModal(appointmentId) {
    // Close appointment details modal first
    const detailsModal = document.getElementById('appointmentDetailsModal');
    if (detailsModal) {
        const modalInstance = bootstrap.Modal.getInstance(detailsModal);
        if (modalInstance) {
            modalInstance.hide();
        }
    }

    // Create cancel modal HTML
    const cancelModalHtml = `
        <div class="modal fade" id="cancelAppointmentModal" tabindex="-1" aria-labelledby="cancelAppointmentModalLabel" aria-hidden="true">
            <div class="modal-dialog">
                <div class="modal-content" style="border-radius: 15px;">
                    <div class="modal-header" style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); color: white; border-radius: 15px 15px 0 0;">
                        <h5 class="modal-title" id="cancelAppointmentModalLabel">
                            <i class="fas fa-times-circle me-2"></i>Cancel Appointment
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <div class="alert alert-warning">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            <strong>Warning:</strong> This action will cancel the appointment and notify the unit owner via email.
                        </div>
                        <form id="cancelAppointmentForm">
                            <div class="mb-3">
                                <label for="cancellationReason" class="form-label">
                                    <strong>Cancellation Reason <span class="text-danger">*</span></strong>
                                </label>
                                <textarea class="form-control" id="cancellationReason" rows="4"
                                    placeholder="Please provide a detailed reason for cancelling this appointment..." required></textarea>
                                <div class="form-text">This reason will be included in the email notification to the unit owner.</div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            <i class="fas fa-arrow-left me-1"></i>Back
                        </button>
                        <button type="button" class="btn btn-danger" onclick="confirmCancelAppointment(${appointmentId})">
                            <i class="fas fa-times me-1"></i>Cancel Appointment
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', cancelModalHtml);

    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('cancelAppointmentModal'));
    modal.show();

    // Clean up modal when hidden
    document.getElementById('cancelAppointmentModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

// Confirm cancel appointment
function confirmCancelAppointment(appointmentId) {
    const reason = document.getElementById('cancellationReason').value.trim();

    if (!reason) {
        alert('Please provide a cancellation reason.');
        return;
    }

    // Show loading state
    const cancelBtn = document.querySelector('#cancelAppointmentModal .btn-danger');
    const originalText = cancelBtn.innerHTML;
    cancelBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Cancelling...';
    cancelBtn.disabled = true;

    // Send cancellation request
    fetch(`/admin/admin-appointment/api/cancel-appointment/${appointmentId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            reason: reason
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close cancel modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('cancelAppointmentModal'));
            modal.hide();

            // Update the appointment details modal if it's open
            updateAppointmentDetailsModal(appointmentId, {
                status: 'cancelled',
                cancelled_by: 'admin',
                cancellation_reason: reason,
                cancelled_at: new Date().toLocaleString()
            });

            // Show professional success popup
            showProfessionalPopup(
                'success',
                'Appointment Cancelled Successfully',
                'The unit owner and inspector have been notified via email. The appointment status has been updated.',
                [
                    {
                        text: 'Close',
                        class: 'success',
                        onclick: 'closeProfessionalPopup();'
                    }
                ]
            );

            // Refresh calendar
            if (typeof calendar !== 'undefined' && calendar && calendar.refetchEvents) {
                calendar.refetchEvents();
            }

            // Update any existing booking notifications
            updateExistingBookingNotifications(appointmentId, 'cancelled');

        } else {
            alert('Error cancelling appointment: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error cancelling appointment:', error);
        alert('Failed to cancel appointment. Please try again.');
    })
    .finally(() => {
        // Reset button state
        cancelBtn.innerHTML = originalText;
        cancelBtn.disabled = false;
    });
}

// Update appointment details modal with cancelled status
function updateAppointmentDetailsModal(appointmentId, cancelData) {
    const detailsModal = document.getElementById('appointmentDetailsModal');
    if (detailsModal && detailsModal.style.display !== 'none') {
        // Update status badge
        const statusBadge = detailsModal.querySelector('.badge');
        if (statusBadge) {
            statusBadge.className = 'badge bg-danger fs-6';
            statusBadge.textContent = 'Cancelled';
        }

        // Add cancellation info
        const statusSection = detailsModal.querySelector('.mb-4');
        if (statusSection) {
            const existingAlert = statusSection.querySelector('.alert-warning');
            if (!existingAlert) {
                const cancelInfo = `
                    <div class="alert alert-warning">
                        <strong>Cancelled by:</strong> ${cancelData.cancelled_by}<br>
                        <strong>Cancelled on:</strong> ${cancelData.cancelled_at}<br>
                        ${cancelData.cancellation_reason ? `<strong>Reason:</strong> ${cancelData.cancellation_reason}` : ''}
                    </div>
                `;
                statusSection.insertAdjacentHTML('beforeend', cancelInfo);
            }
        }

        // Remove cancel button
        const cancelButton = detailsModal.querySelector('.btn-danger');
        if (cancelButton && cancelButton.textContent.includes('Cancel Appointment')) {
            cancelButton.remove();
        }
    }
}

// Cancel appointment directly from notification
function cancelAppointmentFromNotification(appointmentId) {
    showProfessionalCancelModal(appointmentId);
}

// Show professional cancel modal
function showProfessionalCancelModal(appointmentId) {
    // Remove any existing cancel modal
    const existingModal = document.getElementById('professionalCancelModal');
    if (existingModal) {
        existingModal.remove();
    }

    // Create professional cancel modal HTML
    const cancelModalHtml = `
        <div class="modal fade" id="professionalCancelModal" tabindex="-1" aria-labelledby="professionalCancelModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content" style="border-radius: 15px; border: none; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
                    <div class="modal-header" style="background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); color: white; border-radius: 15px 15px 0 0; border: none;">
                        <h5 class="modal-title" id="professionalCancelModalLabel" style="font-weight: 600;">
                            <i class="fas fa-exclamation-triangle me-2"></i>Cancel Appointment
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body" style="padding: 25px;">
                        <div class="alert alert-warning" style="border-radius: 10px; border: none; background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);">
                            <i class="fas fa-info-circle me-2"></i>
                            <strong>Important:</strong> This action will cancel the appointment and notify the unit owner and inspector via email.
                        </div>
                        <form id="professionalCancelForm">
                            <div class="mb-3">
                                <label for="professionalCancellationReason" class="form-label" style="font-weight: 600; color: #495057;">
                                    <i class="fas fa-comment-alt me-2"></i>Cancellation Reason <span class="text-danger">*</span>
                                </label>
                                <textarea class="form-control" id="professionalCancellationReason" rows="4"
                                    placeholder="Please provide a detailed reason for cancelling this appointment..."
                                    style="border-radius: 10px; border: 2px solid #e9ecef; transition: all 0.3s ease; resize: vertical;"
                                    required autocomplete="off" spellcheck="true"></textarea>
                                <div class="form-text" style="color: #6c757d; font-size: 12px;">
                                    <i class="fas fa-envelope me-1"></i>This reason will be included in the email notification.
                                    <br><i class="fas fa-keyboard me-1"></i><strong>Tip:</strong> Press <kbd>Tab</kbd> for default rejection message.
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer" style="border: none; padding: 20px 25px;">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal"
                                style="border-radius: 8px; padding: 10px 20px; font-weight: 500;">
                            <i class="fas fa-arrow-left me-1"></i>Back
                        </button>
                        <button type="button" class="btn btn-danger" id="professionalCancelBtn"
                                onclick="confirmProfessionalCancel(${appointmentId})"
                                style="border-radius: 8px; padding: 10px 20px; font-weight: 500; background: linear-gradient(135deg, #dc3545 0%, #c82333 100%); border: none;">
                            <i class="fas fa-times me-1"></i>Cancel Appointment
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', cancelModalHtml);

    // Get modal and textarea elements
    const modalElement = document.getElementById('professionalCancelModal');
    const textarea = document.getElementById('professionalCancellationReason');

    // Ensure textarea is properly initialized
    textarea.value = ''; // Clear any default value
    textarea.disabled = false; // Ensure it's enabled
    textarea.readOnly = false; // Ensure it's not read-only

    // Add focus styling for textarea
    textarea.addEventListener('focus', function() {
        this.style.borderColor = '#dc3545';
        this.style.boxShadow = '0 0 0 0.2rem rgba(220, 53, 69, 0.25)';
    });

    textarea.addEventListener('blur', function() {
        this.style.borderColor = '#e9ecef';
        this.style.boxShadow = 'none';
    });

    // Add input event to clear error styling when user types
    textarea.addEventListener('input', function() {
        if (this.style.borderColor === 'rgb(220, 53, 69)') {
            this.style.borderColor = '#e9ecef';
            this.style.boxShadow = 'none';

            // Remove error message
            const errorMsg = this.parentNode.querySelector('.error-message');
            if (errorMsg) {
                errorMsg.remove();
            }
        }
    });

    // Add Tab key functionality for default rejection message
    textarea.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            e.preventDefault(); // Prevent default tab behavior

            // Default rejection messages
            const defaultMessages = [
                'Appointment rescheduled by admin due to scheduling conflicts.',
                'Appointment cancelled by admin - unit owner requested reschedule.',
                'Appointment cancelled by admin - inspector unavailable.',
                'Appointment rescheduled by admin for better time slot.',
                'Appointment cancelled by admin - maintenance work scheduled.',
                'Appointment rescheduled by admin due to emergency.'
            ];

            // Get random default message
            const randomMessage = defaultMessages[Math.floor(Math.random() * defaultMessages.length)];

            // Set the message with a nice animation
            this.style.background = 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)';
            this.value = randomMessage;

            // Add typing animation effect
            setTimeout(() => {
                this.style.background = '';
                this.style.borderColor = '#4caf50';
                this.style.boxShadow = '0 0 0 0.2rem rgba(76, 175, 80, 0.25)';

                // Reset border after 2 seconds
                setTimeout(() => {
                    this.style.borderColor = '#e9ecef';
                    this.style.boxShadow = 'none';
                }, 2000);
            }, 500);

            // Clear any error styling
            const errorMsg = this.parentNode.querySelector('.error-message');
            if (errorMsg) {
                errorMsg.remove();
            }
        }
    });

    // Show modal
    const modal = new bootstrap.Modal(modalElement);
    modal.show();

    // Clean up modal when hidden
    modalElement.addEventListener('hidden.bs.modal', function() {
        this.remove();
    });

    // Focus on textarea when modal is fully shown
    modalElement.addEventListener('shown.bs.modal', function() {
        setTimeout(() => {
            const textareaElement = document.getElementById('professionalCancellationReason');
            if (textareaElement) {
                textareaElement.focus();
                textareaElement.select(); // Select any existing text
            }
        }, 100); // Small delay to ensure modal is fully rendered
    });
}

// Confirm professional cancel
function confirmProfessionalCancel(appointmentId) {
    const reason = document.getElementById('professionalCancellationReason').value.trim();

    if (!reason) {
        // Show professional error styling
        const textarea = document.getElementById('professionalCancellationReason');
        textarea.style.borderColor = '#dc3545';
        textarea.style.boxShadow = '0 0 0 0.2rem rgba(220, 53, 69, 0.25)';

        // Create error message if it doesn't exist
        let errorMsg = textarea.parentNode.querySelector('.error-message');
        if (!errorMsg) {
            errorMsg = document.createElement('div');
            errorMsg.className = 'error-message text-danger mt-1';
            errorMsg.style.fontSize = '12px';
            errorMsg.innerHTML = '<i class="fas fa-exclamation-circle me-1"></i>Cancellation reason is required!';
            textarea.parentNode.appendChild(errorMsg);
        }

        textarea.focus();
        return;
    }

    // Show professional loading state
    const cancelBtn = document.getElementById('professionalCancelBtn');
    const originalText = cancelBtn.innerHTML;
    cancelBtn.innerHTML = `
        <div class="d-flex align-items-center">
            <div class="spinner-border spinner-border-sm me-2" role="status" style="width: 16px; height: 16px;">
                <span class="visually-hidden">Loading...</span>
            </div>
            Cancelling...
        </div>
    `;
    cancelBtn.disabled = true;
    cancelBtn.style.background = 'linear-gradient(135deg, #6c757d 0%, #5a6268 100%)';

    // Send cancellation request
    fetch(`/admin/admin-appointment/api/cancel-appointment/${appointmentId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            reason: reason
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('professionalCancelModal'));
            modal.hide();

            // Update the notification to show cancelled status
            updateExistingBookingNotifications(appointmentId, 'cancelled');

            // Show professional success popup
            showProfessionalPopup(
                'success',
                'Appointment Cancelled Successfully',
                'The unit owner and inspector have been notified via email. The appointment status has been updated.',
                [
                    {
                        text: 'Close',
                        class: 'success',
                        onclick: 'closeProfessionalPopup();'
                    }
                ]
            );

            // Refresh calendar
            if (typeof calendar !== 'undefined' && calendar && calendar.refetchEvents) {
                calendar.refetchEvents();
            }
        } else {
            // Show professional error popup
            showProfessionalPopup(
                'error',
                'Cancellation Failed',
                'Error: ' + data.error,
                [
                    {
                        text: 'Try Again',
                        class: 'danger',
                        onclick: 'closeProfessionalPopup();'
                    }
                ]
            );
        }
    })
    .catch(error => {
        console.error('Error cancelling appointment:', error);
        // Show professional error popup
        showProfessionalPopup(
            'error',
            'Network Error',
            'Failed to cancel appointment. Please check your connection and try again.',
            [
                {
                    text: 'Try Again',
                    class: 'danger',
                    onclick: 'closeProfessionalPopup();'
                }
            ]
        );
    })
    .finally(() => {
        // Reset button state
        cancelBtn.innerHTML = originalText;
        cancelBtn.disabled = false;
        cancelBtn.style.background = 'linear-gradient(135deg, #dc3545 0%, #c82333 100%)';
    });
}

// Update existing booking notifications to show cancelled status
function updateExistingBookingNotifications(appointmentId, status) {
    // Update any existing booking alerts that might be showing
    const existingNotifications = document.querySelectorAll('.existing-booking-notification');
    existingNotifications.forEach(notification => {
        const appointmentIds = notification.getAttribute('data-appointment-ids');
        if (appointmentIds && appointmentIds.split(',').includes(appointmentId.toString())) {
            // Find the specific appointment div within the notification
            const appointmentDiv = notification.querySelector(`[data-appointment-id="${appointmentId}"]`);
            if (appointmentDiv && status === 'cancelled') {
                // Update the appointment div to show cancelled status
                appointmentDiv.style.background = 'rgba(220, 53, 69, 0.1)';
                appointmentDiv.style.borderLeft = '3px solid #dc3545';

                // Update status text
                const statusText = appointmentDiv.querySelector('small');
                if (statusText) {
                    statusText.innerHTML = 'Status: <strong style="color: #dc3545;">Cancelled</strong>';
                }

                // Remove cancel button
                const cancelBtn = appointmentDiv.querySelector('.btn-outline-danger');
                if (cancelBtn) {
                    cancelBtn.remove();
                }

                // Add cancelled indicator
                appointmentDiv.insertAdjacentHTML('beforeend',
                    '<br><small style="color: #dc3545; font-weight: bold;"><i class="fas fa-times-circle"></i> This appointment has been cancelled</small>'
                );
            }
        }
    });
}

// Note: Old unfreeze functions removed - now using date details popup for unfreezing

// Professional Popup Functions
function showProfessionalPopup(type, title, message, buttons = []) {
    const popup = document.createElement('div');
    popup.className = 'professional-popup';

    const buttonsHtml = buttons.map(btn =>
        `<button class="professional-popup-btn ${btn.class}" onclick="${btn.onclick}">${btn.text}</button>`
    ).join('');

    popup.innerHTML = `
        <div class="professional-popup-content ${type}">
            <i class="professional-popup-icon ${type} ${type === 'success' ? 'fas fa-check-circle' : 'fas fa-question-circle'}"></i>
            <h3 class="professional-popup-title">${title}</h3>
            <p class="professional-popup-message">${message}</p>
            <div class="professional-popup-buttons">
                ${buttonsHtml}
            </div>
        </div>
    `;

    document.body.appendChild(popup);

    // Auto-remove for success popups after 3 seconds
    if (type === 'success' && buttons.length === 0) {
        setTimeout(() => {
            closeProfessionalPopup();
        }, 3000);
    }
}

function closeProfessionalPopup() {
    const popup = document.querySelector('.professional-popup');
    if (popup) {
        popup.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => {
            popup.remove();
        }, 300);
    }
}

function showRebookingConfirmation() {
    showProfessionalPopup(
        'confirm',
        'Re-booking Available',
        'This will allow you to book a new appointment. The current cancelled appointment details will remain for your records. Do you want to continue?',
        [
            {
                text: 'Cancel',
                class: 'secondary',
                onclick: 'closeProfessionalPopup()'
            },
            {
                text: 'Continue',
                class: 'primary',
                onclick: 'proceedWithRebooking()'
            }
        ]
    );
}

function proceedWithRebooking() {
    closeProfessionalPopup();
    // Redirect to appointments page with rebook parameter
    window.location.href = '/appointments?rebook=1';
}

function refreshAppointmentsList() {
    // Refresh the calendar to show updated appointments
    if (typeof calendar !== 'undefined' && calendar) {
        calendar.refetchEvents();
    }

    // If there's a specific date selected, refresh its data
    if (window.currentSelectedDate) {
        loadDateData(window.currentSelectedDate);
    }
}

function highlightAppointmentDates() {
    // Clear previous highlighting
    const dayCells = document.querySelectorAll('.fc-daygrid-day');
    dayCells.forEach(cell => {
        cell.classList.remove('booking-available');
    });

    // Get appointment dates from calendar events
    if (window.calendarEvents && window.calendarEvents.length > 0) {
        const appointmentDates = new Set();

        window.calendarEvents.forEach(event => {
            // Only highlight appointment events, not frozen slots
            if (event.extendedProps && event.extendedProps.type === 'appointment') {
                let eventDate;
                if (typeof event.start === 'string') {
                    eventDate = event.start.split('T')[0]; // Get date part only
                } else if (event.start && event.start.toISOString) {
                    eventDate = event.start.toISOString().split('T')[0];
                }

                if (eventDate) {
                    appointmentDates.add(eventDate);
                }
            }
        });

        // Apply highlighting to dates with appointments
        dayCells.forEach(cell => {
            const dateStr = cell.getAttribute('data-date');
            if (dateStr && appointmentDates.has(dateStr)) {
                cell.classList.add('booking-available');
            }
        });
    }
}

// Alert and notification functions
function showAlert(message, type = 'info') {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        max-width: 500px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;

    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alert);

    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

function showSuccessPopup(message) {
    showProfessionalPopup(
        'success',
        'Success!',
        message,
        [
            {
                text: 'OK',
                class: 'success',
                onclick: 'closeProfessionalPopup()'
            }
        ]
    );
}


