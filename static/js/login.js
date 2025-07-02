// Two-Step Login System

document.addEventListener('DOMContentLoaded', function() {
    const usernameForm = document.getElementById('usernameForm');
    const passwordForm = document.getElementById('passwordForm');
    
    if (usernameForm) {
        usernameForm.addEventListener('submit', handleUsernameSubmit);
    }
    
    if (passwordForm) {
        passwordForm.addEventListener('submit', handlePasswordSubmit);
    }
});

async function handleUsernameSubmit(event) {
    event.preventDefault();
    
    const identifier = document.getElementById('identifier').value.trim();
    
    if (!identifier) {
        showError('Please enter your username or email');
        return;
    }
    
    try {
        // Check if user exists and get user type
        const response = await fetch('/api/check-user', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ identifier: identifier })
        });
        
        const result = await response.json();
        
        if (response.ok && result.exists) {
            // User exists, show step 2
            showStep2(result.name, result.userType, identifier);
        } else {
            showError(result.message || 'User not found. Please check your username or email.');
        }
        
    } catch (error) {
        console.error('Error checking user:', error);
        showError('Network error. Please try again.');
    }
}

async function handlePasswordSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    
    try {
        const response = await fetch('/login', {
            method: 'POST',
            body: formData
        });
        
        if (response.redirected) {
            // Login successful, redirect
            window.location.href = response.url;
        } else {
            const result = await response.text();
            // Parse error message from response
            const parser = new DOMParser();
            const doc = parser.parseFromString(result, 'text/html');
            const errorElement = doc.querySelector('.flash-error');
            
            if (errorElement) {
                showError(errorElement.textContent.trim());
            } else {
                showError('Invalid password. Please try again.');
            }
        }
        
    } catch (error) {
        console.error('Login error:', error);
        showError('Network error. Please try again.');
    }
}

function showStep2(name, userType, identifier) {
    // Hide step 1
    document.getElementById('step1').style.display = 'none';
    
    // Show step 2
    document.getElementById('step2').style.display = 'block';
    
    // Update user info
    document.getElementById('displayName').textContent = name;
    document.getElementById('userType').textContent = userType;
    
    // Set hidden fields
    document.getElementById('hiddenIdentifier').value = identifier;
    document.getElementById('hiddenUserType').value = userType;
    
    // Focus on password field
    document.getElementById('password').focus();
}

function goBackToStep1() {
    // Show step 1
    document.getElementById('step1').style.display = 'block';
    
    // Hide step 2
    document.getElementById('step2').style.display = 'none';
    
    // Clear password field
    document.getElementById('password').value = '';
    
    // Focus on identifier field
    document.getElementById('identifier').focus();
    
    // Clear any error messages
    clearErrors();
}

function showError(message) {
    // Remove existing error messages
    clearErrors();
    
    // Create error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'flash-message flash-error';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;
    
    // Insert error message
    const activeStep = document.getElementById('step1').style.display === 'none' ? 
                      document.getElementById('step2') : 
                      document.getElementById('step1');
    
    const form = activeStep.querySelector('form');
    form.insertBefore(errorDiv, form.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentElement) {
            errorDiv.remove();
        }
    }, 5000);
}

function clearErrors() {
    const errorMessages = document.querySelectorAll('.flash-error');
    errorMessages.forEach(error => error.remove());
}

// Handle Enter key navigation
document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        const activeStep = document.getElementById('step1').style.display === 'none' ? 'step2' : 'step1';
        
        if (activeStep === 'step1') {
            const identifier = document.getElementById('identifier').value.trim();
            if (identifier) {
                document.getElementById('usernameForm').dispatchEvent(new Event('submit'));
            }
        }
    }
});
