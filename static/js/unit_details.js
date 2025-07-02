// ===== UNIT DETAILS PAGE JAVASCRIPT =====

// Global variables
let currentUnitId = null;
let currentDocuments = [];

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Get unit ID from URL
    const pathParts = window.location.pathname.split('/');
    currentUnitId = pathParts[pathParts.length - 1];
    
    // Load current documents
    loadCurrentDocuments();
    
    console.log('Unit details page initialized for unit:', currentUnitId);
});

// Professional Popup Function
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

// Navigation Functions
function goBack() {
    window.history.back();
}

// Edit Unit Modal Functions
function editUnit() {
    const modal = document.getElementById('editUnitModal');
    modal.classList.add('active');
}

function closeEditModal() {
    const modal = document.getElementById('editUnitModal');
    modal.classList.remove('active');
}

// Update Unit Details
function updateUnitDetails(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const unitData = {
        unit_number: formData.get('unitNumber').trim()
    };
    
    console.log('Updating unit details:', unitData);
    
    fetch(`/api/unit/${currentUnitId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(unitData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showProfessionalPopup('✅ Unit Updated Successfully', 'Unit details have been updated successfully.', 'success');
            closeEditModal();
            // Reload page to show updated data
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            // Enhanced duplicate detection
            const errorMsg = data.message || 'Failed to update unit details';
            if (data.error_type === 'duplicate' || 
                errorMsg.toLowerCase().includes('already exists') || 
                errorMsg.toLowerCase().includes('duplicate') ||
                errorMsg.includes('already exist')) {
                showProfessionalPopup('⚠️ Unit Already Exists', errorMsg, 'duplicate');
            } else {
                showProfessionalPopup('❌ Update Failed', errorMsg, 'error');
            }
        }
    })
    .catch(error => {
        console.error('Error updating unit:', error);
        showProfessionalPopup('❌ Connection Error', 'Network error occurred while updating unit details', 'error');
    });
}

// Document Functions (Read-only)
function loadCurrentDocuments() {
    const documentsList = document.getElementById('documentsList');
    if (!documentsList) return;

    // Get documents from the page (already rendered by template)
    const documentItems = documentsList.querySelectorAll('.document-item .document-name');
    currentDocuments = Array.from(documentItems).map(item => item.textContent.trim());
}

// Quick Action Functions
function generateReport() {
    // Create report data
    const unitData = {
        unit_number: document.querySelector('.page-title').textContent.replace('Unit ', '').replace(' Details', ''),
        project: document.querySelector('.page-subtitle').textContent,
        owner_name: document.querySelector('.owner-info .value')?.textContent?.trim() || 'Not assigned',
        documents: currentDocuments,
        created_date: new Date().toLocaleDateString()
    };

    // Convert to JSON and download
    const dataStr = JSON.stringify(unitData, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);

    const link = document.createElement('a');
    link.href = url;
    link.download = `unit_${unitData.unit_number}_report.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    showProfessionalPopup('✅ Report Generated', 'Unit report has been generated successfully.', 'success');
}

function deleteUnit() {
    showDeleteConfirmation();
}

function showDeleteConfirmation() {
    // Remove existing popup if any
    const existingPopup = document.querySelector('.delete-confirmation-overlay');
    if (existingPopup) {
        existingPopup.remove();
    }

    // Create delete confirmation popup
    const popupHTML = `
        <div class="delete-confirmation-overlay" onclick="closeDeleteConfirmation()">
            <div class="delete-confirmation-container" onclick="event.stopPropagation()">
                <div class="delete-confirmation-header">
                    <h3 class="delete-confirmation-title">⚠️ Confirm Delete</h3>
                </div>
                <p class="delete-confirmation-message">Are you sure you want to delete this unit? This action cannot be undone.</p>
                <div class="delete-confirmation-buttons">
                    <button class="btn btn-secondary" onclick="closeDeleteConfirmation()">Cancel</button>
                    <button class="btn btn-danger" onclick="confirmDeleteUnit()">Delete Unit</button>
                </div>
            </div>
        </div>
    `;

    // Add to body
    document.body.insertAdjacentHTML('beforeend', popupHTML);
}

function closeDeleteConfirmation() {
    const popup = document.querySelector('.delete-confirmation-overlay');
    if (popup) {
        popup.remove();
    }
}

function confirmDeleteUnit() {
    closeDeleteConfirmation();

    fetch(`/api/unit/${currentUnitId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showProfessionalPopup('✅ Unit Deleted', 'Unit has been deleted successfully.', 'success');
            setTimeout(() => {
                // Get floor ID from the breadcrumb and redirect properly
                const breadcrumbLinks = document.querySelectorAll('.breadcrumb a');
                let floorUrl = '/projects'; // fallback

                for (let link of breadcrumbLinks) {
                    if (link.href.includes('/floor/')) {
                        floorUrl = link.href;
                        break;
                    }
                }

                // Navigate to floor page and force refresh
                window.location.href = floorUrl + '?refresh=true';
            }, 2000);
        } else {
            showProfessionalPopup('❌ Delete Failed', data.message || 'Failed to delete unit', 'error');
        }
    })
    .catch(error => {
        console.error('Error deleting unit:', error);
        showProfessionalPopup('❌ Connection Error', 'Network error occurred while deleting unit', 'error');
    });
}

// Close modals when clicking outside
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal-overlay')) {
        event.target.classList.remove('active');
    }
});

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Escape key to close modals
    if (event.key === 'Escape') {
        const activeModal = document.querySelector('.modal-overlay.active');
        if (activeModal) {
            activeModal.classList.remove('active');
        }
    }
    
    // Ctrl+E to edit unit
    if (event.ctrlKey && event.key === 'e') {
        event.preventDefault();
        editUnit();
    }
    
    // Ctrl+P to print
    if (event.ctrlKey && event.key === 'p') {
        event.preventDefault();
        printDetails();
    }
});
