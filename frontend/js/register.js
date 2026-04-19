document.addEventListener('DOMContentLoaded', async () => {
  const committeeSelect = document.getElementById('committee_id');
  const submitButton = document.getElementById('submit-btn');
  const errorBanner = document.getElementById('error-banner');

  // Populate committee dropdown
  try {
    const data = await apiGet('/committees');
    const committees = data.data.committees;

    committees.forEach(committee => {
      const option = document.createElement('option');
      option.value = committee.id;
      option.textContent = `${committee.short_name} - ${committee.full_name}`;

      if (committee.is_full) {
        option.disabled = true;
        option.textContent += ' (FULL)';
      }

      committeeSelect.appendChild(option);
    });
  } catch (error) {
    showGlobalError('Failed to load committees. Please try again.');
    console.error('Failed to load committees:', error);
  }

  // Attach submit handler
  document.getElementById('registration-form').addEventListener('submit', handleSubmit);
});

async function handleSubmit(e) {
  e.preventDefault();

  const submitButton = document.getElementById('submit-btn');
  const errorBanner = document.getElementById('error-banner');

  // Validate form
  const errors = validate();
  if (Object.keys(errors).length > 0) {
    showErrors(errors);
    return;
  }

  // Disable button and show spinner
  submitButton.disabled = true;
  submitButton.innerHTML = '<span class="spinner"></span> Processing...';
  errorBanner.classList.remove('show');

  // Get form data
  const formData = {
    full_name: document.getElementById('full_name').value.trim(),
    student_id_cnic: document.getElementById('student_id_cnic').value.trim(),
    email: document.getElementById('email').value.trim().toLowerCase(),
    phone: document.getElementById('phone').value.trim(),
    institution: document.getElementById('institution').value.trim(),
    committee_id: parseInt(document.getElementById('committee_id').value),
  };

  try {
    const data = await apiPost('/delegates', formData);

    // Redirect to success page with URL params
    const params = new URLSearchParams({
      roll: data.data.roll_number,
      name: data.data.full_name,
      committee: data.data.committee_name,
      email: data.data.email,
    });
    window.location.href = `/success.html?${params.toString()}`;

  } catch (error) {
    // Show error
    if (error.code === 'RATE_LIMITED') {
      showGlobalError('Too many requests. Please wait 10 minutes and try again.');
    } else if (error.field) {
      showFieldError(error.field, error.message);
    } else {
      showGlobalError(error.message || 'Registration failed. Please try again.');
    }

    // Re-enable button
    submitButton.disabled = false;
    submitButton.textContent = 'Register';
  }
}

function validate() {
  const errors = {};

  // Full name
  const fullName = document.getElementById('full_name').value.trim();
  if (!fullName) {
    errors.full_name = 'Full name is required';
  } else if (fullName.length > 200) {
    errors.full_name = 'Name must be under 200 characters';
  }

  // Student ID/CNIC
  const studentId = document.getElementById('student_id_cnic').value.trim();
  if (!studentId) {
    errors.student_id_cnic = 'Student ID / CNIC is required';
  }

  // Email
  const email = document.getElementById('email').value.trim();
  if (!email) {
    errors.email = 'Email is required';
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    errors.email = 'Invalid email format';
  }

  // Phone
  const phone = document.getElementById('phone').value.trim();
  if (!phone) {
    errors.phone = 'Phone number is required';
  } else {
    const digitsOnly = phone.replace(/[\s\-\(\)]/g, '');
    if (!/^(\+92|92|0)3[0-9]{9}$/.test(digitsOnly)) {
      errors.phone = 'Enter a valid Pakistani phone number (e.g. 03001234567)';
    }
  }

  // Institution
  const institution = document.getElementById('institution').value.trim();
  if (!institution) {
    errors.institution = 'Institution name is required';
  } else if (institution.length > 200) {
    errors.institution = 'Institution name must be under 200 characters';
  }

  // Committee
  const committeeId = document.getElementById('committee_id').value;
  if (!committeeId || committeeId === '') {
    errors.committee_id = 'Please select a committee';
  }

  return errors;
}

function showErrors(errors) {
  // Clear previous errors
  document.querySelectorAll('.error-text').forEach(el => el.classList.remove('show'));
  document.querySelectorAll('.form-field').forEach(el => el.classList.remove('error'));

  // Show new errors
  Object.entries(errors).forEach(([field, message]) => {
    const errorEl = document.getElementById(`${field}-error`);
    const fieldEl = document.getElementById(field);

    if (errorEl) {
      errorEl.textContent = message;
      errorEl.classList.add('show');
    }

    if (fieldEl) {
      fieldEl.parentElement.classList.add('error');
    }
  });
}

function showFieldError(field, message) {
  const errorEl = document.getElementById(`${field}-error`);
  const fieldEl = document.getElementById(field);

  if (errorEl) {
    errorEl.textContent = message;
    errorEl.classList.add('show');
  }

  if (fieldEl) {
    fieldEl.parentElement.classList.add('error');
  }
}

function showGlobalError(message) {
  const errorBanner = document.getElementById('error-banner');
  const errorText = document.getElementById('error-message');
  errorText.textContent = message;
  errorBanner.classList.add('show');
}
