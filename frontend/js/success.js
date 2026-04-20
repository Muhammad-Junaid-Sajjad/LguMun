document.addEventListener('DOMContentLoaded', () => {
  const params = new URLSearchParams(window.location.search);

  const rollNumber = params.get('roll');
  const name = params.get('name');
  const committee = params.get('committee');
  const email = params.get('email');

  // Check for missing params
  if (!rollNumber || !name || !committee || !email) {
    document.getElementById('success-content').classList.add('hidden');
    document.getElementById('error-content').classList.remove('hidden');
    return;
  }

  // Set values (textContent only, never innerHTML)
  document.getElementById('roll-number').textContent = rollNumber;
  document.getElementById('delegate-name').textContent = name;
  document.getElementById('committee-name').textContent = committee;
  document.getElementById('delegate-email').textContent = email;
});
