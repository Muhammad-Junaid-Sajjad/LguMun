document.addEventListener('DOMContentLoaded', () => {
  const params = new URLSearchParams(window.location.search);

  const rollNumber = params.get('roll');
  const name = params.get('name');
  const committee = params.get('committee');
  const email = params.get('email');

  // Check for missing params
  if (!rollNumber || !committee || !email) {
    document.getElementById('success-content').style.display = 'none';
    document.getElementById('error-content').style.display = 'block';
    return;
  }

  // Set values (textContent only, never innerHTML)
  document.getElementById('roll-number').textContent = rollNumber;
  document.getElementById('detail-roll').textContent = rollNumber;
  document.getElementById('detail-committee').textContent = committee;
  document.getElementById('detail-email').textContent = email;
});
