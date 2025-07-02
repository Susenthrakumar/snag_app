// Project Details Page JavaScript - Updated with fixes

let floors = [];
let areas = [];

// Initialize project details page
document.addEventListener('DOMContentLoaded', function() {
    if (window.currentProjectId) {
        loadProjectFloors(window.currentProjectId);
        loadProjectAreas(window.currentProjectId);

        // Restore active tab from localStorage
        const activeTab = localStorage.getItem('activeProjectTab') || 'floors';
        switchTab(activeTab);

        // Update floors count
        updateFloorsCount();
    }
});

// Edit mode state
let isEditMode = false;

// Initialize bulk saving flag
window.isBulkSaving = false;

// Toggle edit mode for entire container
function toggleEditMode() {
    isEditMode = !isEditMode;
    const editBtn = document.getElementById('containerEditBtn');

    if (isEditMode) {
        // Enter edit mode
        editBtn.innerHTML = '<i class="fas fa-save"></i>';
        editBtn.style.background = '#10b981';
        showAllEditInputs();
    } else {
        // Exit edit mode and save all
        editBtn.innerHTML = '<i class="fas fa-edit"></i>';
        editBtn.style.background = '#6366f1';
        saveAllFields();
        hideAllEditInputs();
    }
}

// Show all edit inputs
function showAllEditInputs() {
    // Project Name
    const displayName = document.getElementById('displayProjectName');
    const editName = document.getElementById('editProjectName');
    editName.value = displayName.textContent;
    displayName.style.display = 'none';
    editName.style.display = 'block';

    // Status
    const displayStatus = document.getElementById('displayProjectStatus');
    const editStatus = document.getElementById('editProjectStatus');
    const currentStatus = displayStatus.className.split(' ').find(cls =>
        ['active', 'completed', 'on-hold', 'cancelled'].includes(cls)
    ) || 'active';
    editStatus.value = currentStatus;
    displayStatus.style.display = 'none';
    editStatus.style.display = 'block';

    // Location
    const displayLocation = document.getElementById('displayProjectLocation');
    const editLocation = document.getElementById('editProjectLocation');
    editLocation.value = displayLocation.textContent === 'No location set' ? '' : displayLocation.textContent;
    displayLocation.style.display = 'none';
    editLocation.style.display = 'block';

    // Description
    const displayDescription = document.getElementById('displayProjectDescription');
    const editDescription = document.getElementById('editProjectDescription');
    const currentText = displayDescription.textContent.trim();
    editDescription.value = currentText;
    displayDescription.style.display = 'none';
    editDescription.style.display = 'block';
}

// Hide all edit inputs
function hideAllEditInputs() {
    // Project Name
    document.getElementById('displayProjectName').style.display = 'block';
    document.getElementById('editProjectName').style.display = 'none';

    // Status
    document.getElementById('displayProjectStatus').style.display = 'inline-flex';
    document.getElementById('editProjectStatus').style.display = 'none';

    // Location
    document.getElementById('displayProjectLocation').style.display = 'block';
    document.getElementById('editProjectLocation').style.display = 'none';

    // Description
    document.getElementById('displayProjectDescription').style.display = 'block';
    document.getElementById('editProjectDescription').style.display = 'none';
}

// Save all fields
function saveAllFields() {
    // Set flag to prevent individual notifications
    window.isBulkSaving = true;

    saveProjectName();
    saveProjectStatus();
    saveProjectLocation();
    saveProjectDescription();

    // Reset flag and show single notification
    window.isBulkSaving = false;
    showNotification('Project details updated successfully!', 'success');
}

// Show notification function using popup system
function showNotification(message, type = 'info', duration = 5000) {
    const popup = document.getElementById('notificationPopup');
    const titleElement = document.getElementById('notificationTitle');
    const messageElement = document.getElementById('notificationMessage');
    const iconElement = popup.querySelector('.notification-title i');

    if (!popup || !titleElement || !messageElement || !iconElement) {
        console.error('Notification elements not found!');
        alert(message); // Fallback to alert
        return;
    }

    // Set title based on type
    const titles = {
        'success': 'Success',
        'error': 'Error',
        'warning': 'Warning',
        'info': 'Information'
    };

    // Set content
    titleElement.textContent = titles[type] || 'Notification';
    messageElement.textContent = message;

    // Remove existing type classes
    popup.classList.remove('success', 'error', 'warning', 'info');

    // Add new type class
    popup.classList.add(type);

    // Set appropriate icon
    iconElement.className = 'fas ';
    switch(type) {
        case 'success':
            iconElement.className += 'fa-check-circle';
            break;
        case 'error':
            iconElement.className += 'fa-exclamation-circle';
            break;
        case 'warning':
            iconElement.className += 'fa-exclamation-triangle';
            break;
        case 'info':
            iconElement.className += 'fa-info-circle';
            break;
        default:
            iconElement.className += 'fa-bell';
    }

    // Show popup with animation
    popup.style.display = 'block';
    setTimeout(() => popup.classList.add('show'), 10);

    // Auto hide after duration
    if (duration > 0) {
        setTimeout(() => {
            closeNotification();
        }, duration);
    }
}

// Close notification function
function closeNotification() {
    const popup = document.getElementById('notificationPopup');
    if (popup) {
        popup.classList.remove('show');
        setTimeout(() => {
            popup.style.display = 'none';
        }, 300); // Match the CSS transition duration
    }
}

// Helper functions for different notification types
function showError(message, title = 'Error') {
    showNotification(message, 'error');
}

function showSuccess(message, title = 'Success') {
    showNotification(message, 'success');
}

function showWarning(message, title = 'Warning') {
    showNotification(message, 'warning');
}

function showInfo(message, title = 'Information') {
    showNotification(message, 'info');
}

// Professional Popup Function for Project Details
function showProfessionalPopup(title, message, type) {
    // Remove existing popup if any
    const existingPopup = document.querySelector('.popup-overlay');
    if (existingPopup) {
        existingPopup.remove();
    }

    // Create popup HTML
    const popupHTML = `
        <div class="popup-overlay" onclick="closeProfessionalPopup()">
            <div class="popup-container ${type}" onclick="event.stopPropagation()">
                <div class="popup-header">
                    <h3 class="popup-title ${type}">${title}</h3>
                </div>
                <p class="popup-message">${message}</p>
                <button class="popup-close" onclick="closeProfessionalPopup()">OK</button>
            </div>
        </div>
    `;

    // Add to body
    document.body.insertAdjacentHTML('beforeend', popupHTML);

    // Auto close after 5 seconds
    setTimeout(() => {
        closeProfessionalPopup();
    }, 5000);
}

// Close Professional Popup
function closeProfessionalPopup() {
    const popup = document.querySelector('.popup-overlay');
    if (popup) {
        popup.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => {
            popup.remove();
        }, 300);
    }
}

// Load project floors
async function loadProjectFloors(projectId) {
    try {
        const response = await fetch(`/api/projects/${projectId}/floors`);
        if (response.ok) {
            floors = await response.json();
            renderFloors();
        } else {
            floors = [];
            showEmptyFloors();
        }
    } catch (error) {
        console.error('Error loading floors:', error);
        floors = [];
        showEmptyFloors();
    }
}

// Render floors
function renderFloors() {
    const floorsGrid = document.getElementById('floorsGrid');
    const emptyFloors = document.getElementById('emptyFloors');
    
    if (floors.length === 0) {
        showEmptyFloors();
        return;
    }
    
    emptyFloors.style.display = 'none';
    floorsGrid.innerHTML = '';
    
    // Sort floors by number only (1, 2, 3, 4...)
    const sortedFloors = floors.sort((a, b) => {
        const aNum = parseInt(a.number);
        const bNum = parseInt(b.number);
        return aNum - bNum;
    });
    
    sortedFloors.forEach(floor => {
        const floorCard = createFloorCard(floor);
        floorsGrid.appendChild(floorCard);
    });

    // Update floors count
    updateFloorsCount();
}

// Update floors count display
function updateFloorsCount() {
    const totalFloorsElement = document.getElementById('totalFloorsCount');
    if (totalFloorsElement) {
        totalFloorsElement.textContent = floors.length;
    }
}

// Create floor card
function createFloorCard(floor) {
    const card = document.createElement('div');
    card.className = 'floor-card';

    // Add click handler for navigation
    card.onclick = (e) => {
        // Don't navigate if clicking on edit button
        if (!e.target.closest('.floor-edit-btn')) {
            window.location.href = `/floor/${floor.id}`;
        }
    };

    card.innerHTML = `
        <div class="floor-actions">
            <button class="floor-edit-btn" onclick="event.stopPropagation(); editFloor(${floor.id}, '${floor.prefix}', ${floor.number});">
                <i class="fas fa-edit"></i>
            </button>
        </div>
        <div class="floor-icon">
            <i class="fas fa-building"></i>
        </div>
        <div class="floor-name">${floor.prefix} ${floor.number}</div>
    `;

    return card;
}

// Show empty floors
function showEmptyFloors() {
    const floorsGrid = document.getElementById('floorsGrid');
    const emptyFloors = document.getElementById('emptyFloors');
    
    floorsGrid.innerHTML = '';
    emptyFloors.style.display = 'block';
}

// Load project areas
async function loadProjectAreas(projectId) {
    try {
        const response = await fetch(`/api/projects/${projectId}/areas`);
        if (response.ok) {
            areas = await response.json();
            renderAreas();
        } else {
            areas = [];
            showEmptyAreas();
        }
    } catch (error) {
        console.error('Error loading areas:', error);
        areas = [];
        showEmptyAreas();
    }
}

// Render areas
function renderAreas() {
    const areasGrid = document.getElementById('areasGrid');
    const emptyAreas = document.getElementById('emptyAreas');
    
    if (areas.length === 0) {
        showEmptyAreas();
        return;
    }
    
    emptyAreas.style.display = 'none';
    areasGrid.innerHTML = '';
    
    areas.forEach(area => {
        const areaCard = createAreaCard(area);
        areasGrid.appendChild(areaCard);
    });
}

// Get appropriate icon for area based on name
function getAreaIcon(areaName) {
    const name = areaName.toLowerCase();

    if (name.includes('pool') || name.includes('swimming')) return 'fas fa-swimmer';
    if (name.includes('Sitting Area') || name.includes('swimming')) return 'fas fa-couch';
    if (name.includes('gym') || name.includes('fitness')) return 'fas fa-dumbbell';
    if (name.includes('parking') || name.includes('garage')) return 'fas fa-car';
    if (name.includes('garden') || name.includes('park')) return 'fas fa-tree';
    if (name.includes('lobby') || name.includes('reception')) return 'fas fa-door-open';
    if (name.includes('security') || name.includes('guard')) return 'fas fa-shield-alt';
    if (name.includes('elevator') || name.includes('lift')) return 'fas fa-arrows-alt-v';
    if (name.includes('stairs') || name.includes('stair')) return 'fas fa-walking';
    if (name.includes('terrace') || name.includes('roof')) return 'fas fa-building';
    if (name.includes('club') || name.includes('community')) return 'fas fa-users';
    if (name.includes('play') || name.includes('children')) return 'fas fa-child';
    if (name.includes('library') || name.includes('study')) return 'fas fa-book';
    if (name.includes('hall') || name.includes('function')) return 'fas fa-calendar-alt';
    if (name.includes('kitchen') || name.includes('pantry')) return 'fas fa-utensils';
    if (name.includes('store') || name.includes('storage')) return 'fas fa-boxes';
    if (name.includes('office') || name.includes('admin')) return 'fas fa-briefcase';
    if (name.includes('toilet') || name.includes('washroom') || name.includes('restroom')) return 'fas fa-restroom';
    if (name.includes('laundry') || name.includes('wash')) return 'fas fa-tshirt';
    if (name.includes('generator') || name.includes('power')) return 'fas fa-bolt';
    if (name.includes('water') || name.includes('tank')) return 'fas fa-tint';

    // Default icon
    return 'fas fa-map-marker-alt';
}

// Create area card
function createAreaCard(area) {
    const card = document.createElement('div');
    card.className = 'area-card';

    const iconClass = getAreaIcon(area.name);

    card.innerHTML = `
        <div class="area-actions">
            <button class="area-edit-btn" onclick="editArea(${area.id}, '${area.name}')">
                <i class="fas fa-edit"></i>
            </button>
        </div>
        <div class="area-icon">
            <i class="${iconClass}"></i>
        </div>
        <div class="area-name">${area.name}</div>
    `;

    return card;
}

// Show empty areas
function showEmptyAreas() {
    const areasGrid = document.getElementById('areasGrid');
    const emptyAreas = document.getElementById('emptyAreas');
    
    areasGrid.innerHTML = '';
    emptyAreas.style.display = 'block';
}

// Tab switching
function switchTab(tabName) {
    // Save active tab to localStorage
    localStorage.setItem('activeProjectTab', tabName);

    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    const activeTabBtn = document.querySelector(`[data-tab="${tabName}"]`);
    if (activeTabBtn) {
        activeTabBtn.classList.add('active');
    }

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    const activeTabContent = document.getElementById(tabName === 'floors' ? 'floorsTab' : 'areasTab');
    if (activeTabContent) {
        activeTabContent.classList.add('active');
    }
}

// Project editing functions
function editProjectName() {
    const display = document.getElementById('displayProjectName');
    const input = document.getElementById('editProjectName');
    
    input.value = display.textContent;
    display.style.display = 'none';
    input.style.display = 'block';
    input.focus();
}

function saveProjectName() {
    const display = document.getElementById('displayProjectName');
    const input = document.getElementById('editProjectName');

    if (input.value.trim()) {
        display.textContent = input.value.trim();
        updateProject('project_name', input.value.trim());
        if (!isEditMode && !window.isBulkSaving) {
            showNotification('Project name updated successfully!', 'success');
        }
    }

    display.style.display = 'block';
    input.style.display = 'none';
}

function editProjectLocation() {
    const display = document.getElementById('displayProjectLocation');
    const input = document.getElementById('editProjectLocation');
    
    input.value = display.textContent === 'No location set' ? '' : display.textContent;
    display.style.display = 'none';
    input.style.display = 'block';
    input.focus();
}

function saveProjectLocation() {
    const display = document.getElementById('displayProjectLocation');
    const input = document.getElementById('editProjectLocation');

    const value = input.value.trim() || 'No location set';
    display.textContent = value;
    updateProject('location', input.value.trim());

    display.style.display = 'block';
    input.style.display = 'none';
}

function editProjectDescription() {
    const display = document.getElementById('displayProjectDescription');
    const input = document.getElementById('editProjectDescription');

    const currentText = display.textContent;
    const isPlaceholder = currentText.includes('Add a professional description');
    input.value = isPlaceholder ? '' : currentText;
    display.style.display = 'none';
    input.style.display = 'block';
    input.focus();
}

function saveProjectDescription() {
    const display = document.getElementById('displayProjectDescription');
    const input = document.getElementById('editProjectDescription');

    const value = input.value.trim();
    if (value) {
        display.textContent = value;
        display.style.fontStyle = 'normal';
        display.style.color = '#1f2937';
    } else {
        display.textContent = '';
        display.style.fontStyle = 'italic';
        display.style.color = '#9ca3af';
    }

    updateProject('description', value);

    if (!isEditMode && !window.isBulkSaving) {
        showNotification('Project description updated successfully!', 'success');
    }

    display.style.display = 'block';
    input.style.display = 'none';
}

function editProjectStatus() {
    const display = document.getElementById('displayProjectStatus');
    const select = document.getElementById('editProjectStatus');

    // Get current status from the badge
    const currentStatus = display.className.split(' ').find(cls =>
        ['active', 'completed', 'on-hold', 'cancelled'].includes(cls)
    ) || 'active';

    select.value = currentStatus;
    display.style.display = 'none';
    select.style.display = 'block';
    select.focus();
}

function saveProjectStatus() {
    const display = document.getElementById('displayProjectStatus');
    const select = document.getElementById('editProjectStatus');

    const status = select.value;
    const statusText = status.charAt(0).toUpperCase() + status.slice(1).replace('-', ' ');

    // Update display with new status
    display.className = `status-badge ${status}`;
    display.textContent = statusText;

    // Update project silently without any notifications
    updateProject('status', status);

    display.style.display = 'inline-flex';
    select.style.display = 'none';
}

// Update project
async function updateProject(field, value) {
    if (!window.currentProjectId) {
        console.error('No currentProjectId found!');
        return false;
    }

    try {
        const response = await fetch(`/api/projects/${window.currentProjectId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                field: field,
                value: value
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            console.error('Update failed:', errorData);
            return false;
        }

        const result = await response.json();

        if (result.success) {
            console.log('Project updated successfully');
            return true;
        } else {
            console.error('Update failed:', result);
            return false;
        }
    } catch (error) {
        console.error('Network error updating project:', error);
        return false;
    }
}

// Change project image
function changeProjectImage() {
    document.getElementById('changeImageInput').click();
}

async function updateProjectImage(input) {
    if (input.files && input.files[0]) {
        const file = input.files[0];

        const formData = new FormData();
        formData.append('image', file);

        try {
            const response = await fetch(`/api/projects/${window.currentProjectId}/image`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Response not OK:', errorText);
                showNotification('Error updating image: Server error', 'error');
                return;
            }

            const data = await response.json();

            if (data.success) {
                // Get the image element and placeholder
                const imageElement = document.getElementById('projectImage');
                const placeholderElement = document.getElementById('imagePlaceholder');

                if (imageElement) {
                    // Set the new image URL with cache busting
                    const timestamp = new Date().getTime();
                    imageElement.src = `${data.imageUrl}?t=${timestamp}`;
                    imageElement.style.display = 'block';

                    // Hide placeholder if it exists
                    if (placeholderElement) {
                        placeholderElement.style.display = 'none';
                    }

                    // Force image reload
                    imageElement.onload = function() {
                        showNotification('Image updated successfully!', 'success');
                    };

                    imageElement.onerror = function() {
                        showNotification('Image updated but failed to display', 'warning');
                    };
                } else {
                    showNotification('Image updated successfully!', 'success');
                }
            } else {
                showNotification(`Error updating image: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('Error updating image:', error);
            showNotification('Error updating image: Network error', 'error');
        }
    } else {
        showNotification('Please select an image file', 'error');
    }
}

// Handle Enter key
function handleEnterKey(event, callback) {
    if (event.key === 'Enter') {
        callback();
    }
}

// Floor management functions
function openAddFloorModal() {
    const modal = document.getElementById('addFloorModal');
    modal.classList.add('active');
}

function closeAddFloorModal() {
    const modal = document.getElementById('addFloorModal');
    modal.classList.remove('active');
    document.getElementById('addFloorForm').reset();
}

function openBulkAddModal() {
    const modal = document.getElementById('bulkAddModal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';

    // Add event listeners for live preview
    document.getElementById('bulkPrefix').addEventListener('input', updateBulkPreview);
    document.getElementById('startNumber').addEventListener('input', updateBulkPreview);
    document.getElementById('endNumber').addEventListener('input', updateBulkPreview);

    // Initial preview update
    updateBulkPreview();
}

function closeBulkAddModal() {
    const modal = document.getElementById('bulkAddModal');
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
    document.getElementById('bulkAddForm').reset();

    // Remove event listeners
    document.getElementById('bulkPrefix').removeEventListener('input', updateBulkPreview);
    document.getElementById('startNumber').removeEventListener('input', updateBulkPreview);
    document.getElementById('endNumber').removeEventListener('input', updateBulkPreview);

    // Reset preview
    document.getElementById('previewContent').textContent = 'Enter range to see preview';
}

// Update bulk add preview
function updateBulkPreview() {
    const prefix = document.getElementById('bulkPrefix').value.trim() || 'Floor';
    const startNumber = parseInt(document.getElementById('startNumber').value) || 0;
    const endNumber = parseInt(document.getElementById('endNumber').value) || 0;
    const previewContent = document.getElementById('previewContent');

    if (startNumber <= 0 || endNumber <= 0 || startNumber > endNumber) {
        previewContent.innerHTML = '<span style="color: #6b7280;">Enter valid range to see preview</span>';
        return;
    }

    const totalFloors = endNumber - startNumber + 1;
    if (totalFloors > 50) {
        previewContent.innerHTML = `<span style="color: #dc2626;">Range too large! Maximum 50 floors allowed. Current: ${totalFloors} floors</span>`;
        return;
    }

    // Create preview
    let previewHTML = `<div style="margin-bottom: 8px; color: #374151;">Will create <strong>${totalFloors} floors</strong>:</div>`;
    previewHTML += '<div class="preview-floors">';

    const existingNumbers = floors.map(f => f.number);
    let duplicateCount = 0;

    for (let i = startNumber; i <= Math.min(endNumber, startNumber + 9); i++) {
        const isDuplicate = existingNumbers.includes(i);
        if (isDuplicate) duplicateCount++;

        previewHTML += `<span class="preview-floor ${isDuplicate ? 'duplicate' : ''}">${prefix} ${i}</span>`;
    }

    if (totalFloors > 10) {
        previewHTML += `<span style="color: #6b7280; font-size: 12px; padding: 4px 8px;">... and ${totalFloors - 10} more</span>`;
    }

    previewHTML += '</div>';

    if (duplicateCount > 0) {
        previewHTML += `<div style="margin-top: 8px; color: #f59e0b; font-size: 12px;"><i class="fas fa-exclamation-triangle"></i> ${duplicateCount} duplicate${duplicateCount > 1 ? 's' : ''} will be skipped</div>`;
    }

    previewContent.innerHTML = previewHTML;
}



function closeEditFloorModal() {
    const modal = document.getElementById('editFloorModal');
    if (modal) {
        modal.classList.remove('active');
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        document.getElementById('editFloorForm').reset();
    }
}

// Add floor
async function addFloor(event) {
    event.preventDefault();
    
    const form = event.target;
    const prefix = form.floorPrefix.value.trim();
    const number = parseInt(form.floorNumber.value);

    // Check for duplicate floor number
    const isDuplicate = floors.some(floor => 
        floor.prefix.toLowerCase() === prefix.toLowerCase() && 
        floor.number === number
    );

    if (isDuplicate) {
        showError('A floor with this prefix and number already exists');
        return;
    }

    try {
        const response = await fetch('/api/floors', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                projectId: window.currentProjectId,
                prefix,
                number
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to add floor');
        }

        const newFloor = await response.json();
        floors.push(newFloor);
        renderFloors();
        closeAddFloorModal();
        showProfessionalPopup('✅ Floor Added Successfully', 'Floor has been added to the project successfully.', 'success');
    } catch (error) {
        console.error('Error adding floor:', error);
        if (error.message.includes('already exists')) {
            showProfessionalPopup('⚠️ Floor Already Exists', error.message, 'duplicate');
        } else {
            showProfessionalPopup('❌ Add Floor Failed', 'Failed to add floor: ' + error.message, 'error');
        }
    }
}

// Bulk add floors
async function bulkAddFloors(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const prefix = formData.get('bulkPrefix').trim();
    const startNumber = parseInt(formData.get('startNumber'));
    const endNumber = parseInt(formData.get('endNumber'));
    
    if (startNumber > endNumber) {
        showNotification('Start number must be less than end number!', 'error');
        return;
    }
    
    const floorsToAdd = [];
    const duplicateNumbers = [];

    for (let i = startNumber; i <= endNumber; i++) {
        const numberExists = floors.some(floor => floor.number === i);

        if (!numberExists) {
            floorsToAdd.push({
                projectId: window.currentProjectId,
                prefix: prefix,
                number: i
            });
        } else {
            duplicateNumbers.push(i);
        }
    }
    
    if (floorsToAdd.length === 0) {
        showNotification(`All floor numbers in this range already exist! Duplicates: ${duplicateNumbers.join(', ')}`, 'error');
        return;
    }

    if (duplicateNumbers.length > 0) {
        showNotification(`Skipping duplicate floor numbers: ${duplicateNumbers.join(', ')}`, 'warning');
    }
    
    try {
        const response = await fetch('/api/floors/bulk', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ floors: floorsToAdd })
        });
        
        if (response.ok) {
            const newFloors = await response.json();
            floors.push(...newFloors);
            renderFloors();
            closeBulkAddModal();
            showProfessionalPopup('✅ Floors Added Successfully', `${newFloors.length} floors added successfully!`, 'success');
        } else {
            showProfessionalPopup('❌ Bulk Add Failed', 'Error adding floors', 'error');
        }
    } catch (error) {
        console.error('Error adding floors:', error);
        showProfessionalPopup('❌ Bulk Add Failed', 'Error adding floors', 'error');
    }
}

// Edit floor
function editFloor(floorId, prefix, number) {
    console.log('🔧 Edit floor called:', floorId, prefix, number);

    const modal = document.getElementById('editFloorModal');
    const form = document.getElementById('editFloorForm');
    const idInput = document.getElementById('editFloorId');
    const prefixInput = document.getElementById('editFloorPrefix');
    const numberInput = document.getElementById('editFloorNumber');

    if (!modal || !form || !idInput || !prefixInput || !numberInput) {
        console.error('❌ Edit modal elements not found');
        showProfessionalPopup('❌ Modal Error', 'Edit modal elements not found', 'error');
        return;
    }

    // Set form values
    idInput.value = floorId;
    prefixInput.value = prefix;
    numberInput.value = number;

    // Show modal with proper CSS classes
    modal.style.display = 'flex';
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';

    console.log('✅ Edit modal opened successfully');
}

// Update floor
async function updateFloor(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const floorId = formData.get('editFloorId');
    const prefix = formData.get('editFloorPrefix');
    const numberValue = formData.get('editFloorNumber');

    // Clean and validate inputs
    const cleanPrefix = prefix ? prefix.trim() : '';
    const number = numberValue ? parseInt(numberValue) : 0;

    // Validation
    if (!cleanPrefix) {
        showNotification('Please enter a valid prefix', 'error');
        return;
    }

    if (!numberValue || isNaN(number) || number <= 0) {
        showNotification('Please enter a valid floor number', 'error');
        return;
    }

    // Check for duplicate floor numbers (excluding current floor)
    const numberExists = floors.some(floor =>
        floor.number === number && floor.id != floorId
    );

    if (numberExists) {
        showNotification(`Floor number ${number} already exists!`, 'error');
        return;
    }

    try {
        const response = await fetch(`/api/floors/${floorId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prefix: cleanPrefix,
                number: number
            })
        });

        if (response.ok) {
            const result = await response.json();

            // Update local floors array
            const floorIndex = floors.findIndex(f => f.id == floorId);
            if (floorIndex !== -1) {
                floors[floorIndex].prefix = cleanPrefix;
                floors[floorIndex].number = number;
                renderFloors();
            }

            closeEditFloorModal();
            showProfessionalPopup('✅ Floor Updated Successfully', 'Floor details have been updated successfully.', 'success');
        } else {
            const errorData = await response.json();
            if (errorData.error && errorData.error.includes('already exists')) {
                showProfessionalPopup('⚠️ Floor Already Exists', errorData.error, 'duplicate');
            } else {
                showProfessionalPopup('❌ Update Failed', errorData.error || 'Error updating floor', 'error');
            }
        }
    } catch (error) {
        console.error('Network error updating floor:', error);

        // Check if it's a network connectivity issue
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            showProfessionalPopup('❌ Connection Error', 'Network connection failed. Please check your internet connection.', 'error');
        } else {
            showProfessionalPopup('❌ Update Failed', 'Failed to update floor. Please try again.', 'error');
        }
    }
}

// Area management
function openAddAreaModal() {
    const modal = document.getElementById('addAreaModal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';

    // Hide custom input if it was open
    document.getElementById('customAreaInput').style.display = 'none';
}

function closeAddAreaModal() {
    const modal = document.getElementById('addAreaModal');
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';

    // Reset custom input
    document.getElementById('customAreaInput').style.display = 'none';
    document.getElementById('customAreaName').value = '';
}

function addAreaFromOption(areaName) {
    addArea(areaName);
    closeAddAreaModal();
}

function openCustomAreaInput() {
    document.getElementById('customAreaInput').style.display = 'block';
    document.getElementById('customAreaName').focus();
}

function cancelCustomArea() {
    document.getElementById('customAreaInput').style.display = 'none';
    document.getElementById('customAreaName').value = '';
}

function addCustomArea() {
    const areaName = document.getElementById('customAreaName').value.trim();
    if (areaName) {
        addArea(areaName);
        closeAddAreaModal();
    } else {
        showNotification('Please enter an area name', 'error');
    }
}

function handleCustomAreaEnter(event) {
    if (event.key === 'Enter') {
        addCustomArea();
    }
}

async function addArea(name) {
    // Check for duplicate area names
    const nameExists = areas.some(area =>
        area.name.toLowerCase() === name.toLowerCase()
    );

    if (nameExists) {
        showProfessionalPopup('⚠️ Area Already Exists', `Area "${name}" already exists!`, 'duplicate');
        return;
    }

    const areaData = {
        projectId: window.currentProjectId,
        name: name
    };

    try {
        const response = await fetch('/api/areas', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(areaData)
        });

        if (response.ok) {
            const newArea = await response.json();
            areas.push(newArea);
            renderAreas();
            showProfessionalPopup('✅ Area Added Successfully', 'Area has been added to the project successfully.', 'success');
        } else {
            const errorData = await response.json();
            showProfessionalPopup('❌ Add Area Failed', errorData.error || 'Error adding area', 'error');
        }
    } catch (error) {
        console.error('Error adding area:', error);
        showProfessionalPopup('❌ Add Area Failed', 'Error adding area', 'error');
    }
}

function editArea(areaId, currentName) {
    document.getElementById('editAreaId').value = areaId;
    document.getElementById('editAreaName').value = currentName;
    openEditAreaModal();
}

// Edit area modal functions
function openEditAreaModal() {
    const modal = document.getElementById('editAreaModal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeEditAreaModal() {
    const modal = document.getElementById('editAreaModal');
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
    document.getElementById('editAreaForm').reset();
}

// Update area function for form submission
async function updateArea(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const areaId = formData.get('editAreaId');
    const name = formData.get('editAreaName').trim();

    if (!name) {
        showNotification('Please enter a valid area name', 'error');
        return;
    }

    // Check for duplicate area names (excluding current area)
    const nameExists = areas.some(area =>
        area.name.toLowerCase() === name.toLowerCase() && area.id != areaId
    );

    if (nameExists) {
        showProfessionalPopup('⚠️ Area Already Exists', `Area "${name}" already exists!`, 'duplicate');
        return;
    }

    try {
        const response = await fetch(`/api/areas/${areaId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name })
        });

        if (response.ok) {
            const areaIndex = areas.findIndex(a => a.id == areaId);
            if (areaIndex !== -1) {
                areas[areaIndex].name = name;
                renderAreas();
            }
            closeEditAreaModal();
            showProfessionalPopup('✅ Area Updated Successfully', 'Area details have been updated successfully.', 'success');
        } else {
            const errorData = await response.json();
            showProfessionalPopup('❌ Update Failed', errorData.error || 'Error updating area', 'error');
        }
    } catch (error) {
        console.error('Error updating area:', error);
        showProfessionalPopup('❌ Update Failed', 'Error updating area', 'error');
    }
}


