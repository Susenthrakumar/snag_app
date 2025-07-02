// Projects Management JavaScript - Updated for database image storage

let currentProject = null;
let projects = [];
let filteredProjects = [];
let floors = [];
let commonAreas = [];
let currentSort = 'name';
let currentFilter = 'all';

// Initialize projects page
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Projects page loaded');

    // Check if dropdown elements exist
    const sortDropdown = document.getElementById('sortDropdown');
    const filterDropdown = document.getElementById('filterDropdown');

    console.log('📋 Sort dropdown found:', !!sortDropdown);
    console.log('📋 Filter dropdown found:', !!filterDropdown);

    loadProjects();
});

// Load projects from server
async function loadProjects() {
    try {
        const response = await fetch('/api/projects');
        if (response.ok) {
            const data = await response.json();
            projects = data.projects || [];
            filteredProjects = [...projects];
            console.log('Loaded projects:', projects.length);
            applyFiltersAndSort();
        } else {
            console.log('No projects found or error response');
            projects = [];
            filteredProjects = [];
            showEmptyState();
        }
    } catch (error) {
        console.error('Error loading projects:', error);
        projects = [];
        filteredProjects = [];
        showEmptyState();
    }
}

// Render projects grid
function renderProjects() {
    const projectsGrid = document.getElementById('projectsGrid');
    const emptyState = document.getElementById('emptyState');

    console.log('Rendering projects:', filteredProjects.length, 'filtered,', projects.length, 'total');

    if (filteredProjects.length === 0) {
        if (projects.length === 0) {
            showEmptyState();
        } else {
            projectsGrid.innerHTML = '<div class="no-results">No projects match your search criteria</div>';
            emptyState.style.display = 'none';
        }
        return;
    }

    // Hide empty state and show projects
    emptyState.style.display = 'none';
    projectsGrid.innerHTML = '';
    projectsGrid.style.display = 'grid';

    filteredProjects.forEach(project => {
        const projectCard = createProjectCard(project);
        projectsGrid.appendChild(projectCard);
    });

    console.log('Projects rendered successfully');
}

// Create project card element
function createProjectCard(project) {
    const card = document.createElement('div');
    card.className = 'project-card';
    card.onclick = () => window.location.href = `/project/${project.id}`;

    card.innerHTML = `
        <div class="project-image">
            <img src="/api/projects/${project.id}/image/view" alt="${project.project_name}"
                 onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';"
                 onload="this.style.display='block'; this.nextElementSibling.style.display='none';">
            <div class="placeholder" style="display: flex;"><i class="fas fa-building"></i></div>
        </div>
        <div class="project-info">
            <div class="project-name">${project.project_name}</div>
            <div class="project-location">
                <i class="fas fa-map-marker-alt"></i>
                ${project.location || 'No location'}
            </div>
        </div>
    `;

    return card;
}

// Show empty state
function showEmptyState() {
    const projectsGrid = document.getElementById('projectsGrid');
    const emptyState = document.getElementById('emptyState');
    
    projectsGrid.innerHTML = '';
    emptyState.style.display = 'block';
}

// Modal functions
function openAddProjectModal() {
    const modal = document.getElementById('addProjectModal');
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeAddProjectModal() {
    const modal = document.getElementById('addProjectModal');
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
    document.getElementById('addProjectForm').reset();
    resetImagePreview();
}

function openProjectDetails(project) {
    currentProject = project;
    const modal = document.getElementById('projectDetailsModal');
    
    // Populate project details
    document.getElementById('projectDetailsTitle').textContent = project.name;
    document.getElementById('projectDetailsImage').src = project.image || '/static/images/placeholder.jpg';
    document.getElementById('displayProjectName').textContent = project.name;
    document.getElementById('displayProjectLocation').textContent = project.location;
    document.getElementById('displayProjectDescription').textContent = project.description || 'No description';
    
    // Load floors and areas
    loadProjectFloors(project.id);
    loadProjectAreas(project.id);
    
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeProjectDetailsModal() {
    const modal = document.getElementById('projectDetailsModal');
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
    currentProject = null;
}

// Image preview function
function previewImage(input) {
    const preview = document.getElementById('imagePreview');
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            preview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
            preview.classList.add('has-image');
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

function resetImagePreview() {
    const preview = document.getElementById('imagePreview');
    preview.innerHTML = `
        <i class="fas fa-image"></i>
        <span>Choose cover image</span>
    `;
    preview.classList.remove('has-image');
}

// Add project function
async function addProject(event) {
    event.preventDefault();

    const formData = new FormData(event.target);

    // Convert FormData to JSON object for project creation
    const projectData = {
        projectName: formData.get('projectName'),
        projectLocation: formData.get('projectLocation'),
        projectDescription: formData.get('projectDescription')
    };

    try {
        // First create the project
        const response = await fetch('/api/projects', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(projectData)
        });

        if (response.ok) {
            const result = await response.json();
            console.log('Project created successfully:', result);

            // If there's an image, upload it
            const imageFile = formData.get('projectImage');
            if (imageFile && imageFile.size > 0) {
                const imageFormData = new FormData();
                imageFormData.append('image', imageFile);

                try {
                    const imageResponse = await fetch(`/api/projects/${result.project_id}/image`, {
                        method: 'POST',
                        body: imageFormData
                    });

                    if (imageResponse.ok) {
                        console.log('Image uploaded successfully');
                    } else {
                        console.log('Image upload failed, but project created');
                    }
                } catch (imageError) {
                    console.error('Error uploading image:', imageError);
                }
            }

            // Show success notification
            showNotification('Project created successfully!', 'success');

            // Close modal
            closeAddProjectModal();

            // Reload projects to show the new one
            await loadProjects();

        } else {
            let errorMessage = 'Failed to create project';
            try {
                const errorData = await response.json();
                errorMessage = errorData.error || errorData.message || errorMessage;
            } catch (parseError) {
                const errorText = await response.text();
                console.log('Error response:', errorText);
            }

            showNotification(errorMessage, 'error');
        }
    } catch (error) {
        console.error('Error creating project:', error);
        showNotification('Network error occurred while creating project', 'error');
    }
}

// Tab switching
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabName === 'floors' ? 'floorsTab' : 'commonAreasTab').classList.add('active');
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
        updateProject('name', input.value.trim());
    }
    
    display.style.display = 'block';
    input.style.display = 'none';
}

function editProjectLocation() {
    const display = document.getElementById('displayProjectLocation');
    const input = document.getElementById('editProjectLocation');
    
    input.value = display.textContent;
    display.style.display = 'none';
    input.style.display = 'block';
    input.focus();
}

function saveProjectLocation() {
    const display = document.getElementById('displayProjectLocation');
    const input = document.getElementById('editProjectLocation');
    
    if (input.value.trim()) {
        display.textContent = input.value.trim();
        updateProject('location', input.value.trim());
    }
    
    display.style.display = 'block';
    input.style.display = 'none';
}

function editProjectDescription() {
    const display = document.getElementById('displayProjectDescription');
    const input = document.getElementById('editProjectDescription');
    
    input.value = display.textContent;
    display.style.display = 'none';
    input.style.display = 'block';
    input.focus();
}

function saveProjectDescription() {
    const display = document.getElementById('displayProjectDescription');
    const input = document.getElementById('editProjectDescription');
    
    if (input.value.trim()) {
        display.textContent = input.value.trim();
        updateProject('description', input.value.trim());
    }
    
    display.style.display = 'block';
    input.style.display = 'none';
}

// Update project function
async function updateProject(field, value) {
    if (!currentProject) return;
    
    try {
        const response = await fetch(`/api/projects/${currentProject.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                field: field,
                value: value
            })
        });
        
        if (response.ok) {
            // Update local project data
            currentProject[field] = value;
            const projectIndex = projects.findIndex(p => p.id === currentProject.id);
            if (projectIndex !== -1) {
                projects[projectIndex][field] = value;
                renderProjects();
            }
            showNotification('Project updated successfully!', 'success');
        } else {
            showNotification('Error updating project', 'error');
        }
    } catch (error) {
        console.error('Error updating project:', error);
        showNotification('Error updating project', 'error');
    }
}

// Change project image
function changeProjectImage() {
    document.getElementById('changeImageInput').click();
}

function updateProjectImage(input) {
    if (input.files && input.files[0]) {
        const formData = new FormData();
        formData.append('image', input.files[0]);
        
        fetch(`/api/projects/${currentProject.id}/image`, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('projectDetailsImage').src = data.imageUrl;
                currentProject.image = data.imageUrl;
                renderProjects();
                showNotification('Image updated successfully!', 'success');
            } else {
                showNotification('Error updating image', 'error');
            }
        })
        .catch(error => {
            console.error('Error updating image:', error);
            showNotification('Error updating image', 'error');
        });
    }
}

// Handle Enter key press
function handleEnterKey(event, callback) {
    if (event.key === 'Enter') {
        callback();
    }
}

// Floors Management
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

function renderFloors() {
    const floorsGrid = document.getElementById('floorsGrid');
    const emptyFloors = document.getElementById('emptyFloors');

    if (floors.length === 0) {
        showEmptyFloors();
        return;
    }

    emptyFloors.style.display = 'none';
    floorsGrid.innerHTML = '';

    // Sort floors properly (Floor 1, Floor 2, ..., Floor 10, Floor 11)
    const sortedFloors = floors.sort((a, b) => {
        const aNum = parseInt(a.number);
        const bNum = parseInt(b.number);
        if (a.prefix === b.prefix) {
            return aNum - bNum;
        }
        return a.prefix.localeCompare(b.prefix);
    });

    sortedFloors.forEach(floor => {
        const floorCard = createFloorCard(floor);
        floorsGrid.appendChild(floorCard);
    });
}

function createFloorCard(floor) {
    const card = document.createElement('div');
    card.className = 'floor-card';

    card.innerHTML = `
        <div class="floor-actions">
            <button class="floor-edit-btn" onclick="editFloor(${floor.id})">
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

function showEmptyFloors() {
    const floorsGrid = document.getElementById('floorsGrid');
    const emptyFloors = document.getElementById('emptyFloors');

    floorsGrid.innerHTML = '';
    emptyFloors.style.display = 'block';
}

// Floor modal functions
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
}

function closeBulkAddModal() {
    const modal = document.getElementById('bulkAddModal');
    modal.classList.remove('active');
    document.getElementById('bulkAddForm').reset();
}

// Add single floor
async function addFloor(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const floorData = {
        projectId: currentProject.id,
        prefix: formData.get('floorPrefix').trim(),
        number: parseInt(formData.get('floorNumber'))
    };

    // Check for duplicates - number must be unique regardless of prefix
    const exists = floors.some(floor => floor.number === floorData.number);

    if (exists) {
        showNotification(`Floor number ${floorData.number} already exists! Numbers must be unique regardless of prefix.`, 'error');
        return;
    }

    try {
        const response = await fetch('/api/floors', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(floorData)
        });

        if (response.ok) {
            const newFloor = await response.json();
            floors.push(newFloor);
            renderFloors();
            closeAddFloorModal();
            showNotification('Floor added successfully!', 'success');
        } else {
            showNotification('Error adding floor', 'error');
        }
    } catch (error) {
        console.error('Error adding floor:', error);
        showNotification('Error adding floor', 'error');
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
    for (let i = startNumber; i <= endNumber; i++) {
        // Check for duplicates - number must be unique regardless of prefix
        const exists = floors.some(floor => floor.number === i);

        if (!exists) {
            floorsToAdd.push({
                projectId: currentProject.id,
                prefix: prefix,
                number: i
            });
        }
    }

    if (floorsToAdd.length === 0) {
        showNotification('All floor numbers in this range already exist! Numbers must be unique regardless of prefix.', 'error');
        return;
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
            showNotification(`${newFloors.length} floors added successfully!`, 'success');
        } else {
            showNotification('Error adding floors', 'error');
        }
    } catch (error) {
        console.error('Error adding floors:', error);
        showNotification('Error adding floors', 'error');
    }
}

// Edit floor
function editFloor(floorId) {
    const floor = floors.find(f => f.id === floorId);
    if (!floor) return;

    const newName = prompt(`Edit floor name:`, `${floor.prefix} ${floor.number}`);
    if (newName && newName.trim()) {
        const parts = newName.trim().split(' ');
        if (parts.length >= 2) {
            const number = parseInt(parts[parts.length - 1]);
            const prefix = parts.slice(0, -1).join(' ');

            if (!isNaN(number)) {
                updateFloor(floorId, prefix, number);
            } else {
                showNotification('Invalid floor format! Use format: "Prefix Number"', 'error');
            }
        } else {
            showNotification('Invalid floor format! Use format: "Prefix Number"', 'error');
        }
    }
}

// Update floor
async function updateFloor(floorId, prefix, number) {
    try {
        const response = await fetch(`/api/floors/${floorId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prefix, number })
        });

        if (response.ok) {
            const floorIndex = floors.findIndex(f => f.id === floorId);
            if (floorIndex !== -1) {
                floors[floorIndex].prefix = prefix;
                floors[floorIndex].number = number;
                renderFloors();
            }
            showNotification('Floor updated successfully!', 'success');
        } else {
            showNotification('Error updating floor', 'error');
        }
    } catch (error) {
        console.error('Error updating floor:', error);
        showNotification('Error updating floor', 'error');
    }
}

// Common Areas Management
async function loadProjectAreas(projectId) {
    try {
        const response = await fetch(`/api/projects/${projectId}/areas`);
        if (response.ok) {
            commonAreas = await response.json();
            renderAreas();
        } else {
            commonAreas = [];
            showEmptyAreas();
        }
    } catch (error) {
        console.error('Error loading areas:', error);
        commonAreas = [];
        showEmptyAreas();
    }
}

function renderAreas() {
    const areasGrid = document.getElementById('areasGrid');
    const emptyAreas = document.getElementById('emptyAreas');

    if (commonAreas.length === 0) {
        showEmptyAreas();
        return;
    }

    emptyAreas.style.display = 'none';
    areasGrid.innerHTML = '';

    commonAreas.forEach(area => {
        const areaCard = createAreaCard(area);
        areasGrid.appendChild(areaCard);
    });
}

function createAreaCard(area) {
    const card = document.createElement('div');
    card.className = 'area-card';

    card.innerHTML = `
        <div class="area-actions">
            <button class="area-edit-btn" onclick="editArea(${area.id})">
                <i class="fas fa-edit"></i>
            </button>
        </div>
        <div class="area-icon">
            <i class="fas fa-map"></i>
        </div>
        <div class="area-name">${area.name}</div>
    `;

    return card;
}

function showEmptyAreas() {
    const areasGrid = document.getElementById('areasGrid');
    const emptyAreas = document.getElementById('emptyAreas');

    areasGrid.innerHTML = '';
    emptyAreas.style.display = 'block';
}

function openAddAreaModal() {
    const areaName = prompt('Enter area name:');
    if (areaName && areaName.trim()) {
        addArea(areaName.trim());
    }
}

async function addArea(name) {
    const areaData = {
        projectId: currentProject.id,
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
            commonAreas.push(newArea);
            renderAreas();
            showNotification('Area added successfully!', 'success');
        } else {
            showNotification('Error adding area', 'error');
        }
    } catch (error) {
        console.error('Error adding area:', error);
        showNotification('Error adding area', 'error');
    }
}

function editArea(areaId) {
    const area = commonAreas.find(a => a.id === areaId);
    if (!area) return;

    const newName = prompt('Edit area name:', area.name);
    if (newName && newName.trim()) {
        updateArea(areaId, newName.trim());
    }
}

async function updateArea(areaId, name) {
    try {
        const response = await fetch(`/api/areas/${areaId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name })
        });

        if (response.ok) {
            const areaIndex = commonAreas.findIndex(a => a.id === areaId);
            if (areaIndex !== -1) {
                commonAreas[areaIndex].name = name;
                renderAreas();
            }
            showNotification('Area updated successfully!', 'success');
        } else {
            showNotification('Error updating area', 'error');
        }
    } catch (error) {
        console.error('Error updating area:', error);
        showNotification('Error updating area', 'error');
    }
}

// Utility function for notifications
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `flash-message flash-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i>
        ${message}
    `;

    document.body.appendChild(notification);

    // Position notification
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '10000';
    notification.style.maxWidth = '400px';

    // Auto-hide after 3 seconds
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Search, Sort, and Filter Functions
function filterProjects() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();

    filteredProjects = projects.filter(project => {
        const matchesSearch = project.project_name.toLowerCase().includes(searchTerm) ||
                            (project.location && project.location.toLowerCase().includes(searchTerm)) ||
                            (project.description && project.description.toLowerCase().includes(searchTerm));

        const matchesFilter = currentFilter === 'all' ||
                            (project.status && project.status === currentFilter);

        return matchesSearch && matchesFilter;
    });

    applySorting();
    renderProjects();
}

function sortProjects(sortType) {
    console.log('Sort projects called with:', sortType);
    currentSort = sortType;
    applySorting();
    renderProjects();
    closeSortDropdown();
}

function filterByStatus(status) {
    console.log('Filter by status called with:', status);
    currentFilter = status;
    filterProjects();
    closeFilterDropdown();
}

function applySorting() {
    filteredProjects.sort((a, b) => {
        switch (currentSort) {
            case 'name':
                return a.project_name.localeCompare(b.project_name);
            case 'name-desc':
                return b.project_name.localeCompare(a.project_name);
            case 'date':
                return new Date(b.created_at || 0) - new Date(a.created_at || 0);
            case 'date-desc':
                return new Date(a.created_at || 0) - new Date(b.created_at || 0);
            default:
                return 0;
        }
    });
}

function applyFiltersAndSort() {
    filterProjects();
}

function toggleSortDropdown() {
    console.log('🔄 Toggle sort dropdown clicked');
    const dropdown = document.getElementById('sortDropdown');
    const filterDropdown = document.getElementById('filterDropdown');

    if (!dropdown) {
        console.error('❌ Sort dropdown element not found');
        return;
    }

    // Close filter dropdown first
    if (filterDropdown) {
        filterDropdown.classList.remove('active');
    }

    // Toggle sort dropdown
    const isActive = dropdown.classList.contains('active');
    dropdown.classList.toggle('active');

    console.log('✅ Sort dropdown now:', isActive ? 'closed' : 'open');
}

function toggleFilterDropdown() {
    console.log('🔄 Toggle filter dropdown clicked');
    const dropdown = document.getElementById('filterDropdown');
    const sortDropdown = document.getElementById('sortDropdown');

    if (!dropdown) {
        console.error('❌ Filter dropdown element not found');
        return;
    }

    // Close sort dropdown first
    if (sortDropdown) {
        sortDropdown.classList.remove('active');
    }

    // Toggle filter dropdown
    const isActive = dropdown.classList.contains('active');
    dropdown.classList.toggle('active');

    console.log('✅ Filter dropdown now:', isActive ? 'closed' : 'open');
}

function closeSortDropdown() {
    document.getElementById('sortDropdown').classList.remove('active');
}

function closeFilterDropdown() {
    document.getElementById('filterDropdown').classList.remove('active');
}

// Close dropdowns when clicking outside
document.addEventListener('click', function(event) {
    const sortBtn = event.target.closest('[onclick*="toggleSortDropdown"]');
    const filterBtn = event.target.closest('[onclick*="toggleFilterDropdown"]');
    const sortDropdown = document.getElementById('sortDropdown');
    const filterDropdown = document.getElementById('filterDropdown');

    // Close sort dropdown if clicking outside
    if (!sortBtn && !event.target.closest('#sortDropdown')) {
        sortDropdown.classList.remove('active');
    }

    // Close filter dropdown if clicking outside
    if (!filterBtn && !event.target.closest('#filterDropdown')) {
        filterDropdown.classList.remove('active');
    }
});
