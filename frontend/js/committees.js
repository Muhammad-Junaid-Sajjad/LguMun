document.addEventListener('DOMContentLoaded', async () => {
  const committeesGrid = document.getElementById('committees-grid');
  const loadingSkeleton = document.getElementById('loading-skeleton');
  const errorState = document.getElementById('error-state');

  try {
    const data = await apiGet('/committees');
    const committees = data.data.committees;

    // Hide skeleton
    loadingSkeleton.classList.add('hidden');

    // Update count
    const totalSeats = committees.reduce((sum, c) => sum + c.total_seats, 0);
    const filledSeats = committees.reduce((sum, c) => sum + c.filled_seats, 0);
    document.getElementById('committees-count').textContent =
      `${committees.length} committees • ${totalSeats} seats`;

    // Render committees
    committees.forEach(committee => {
      const card = createCommitteeCard(committee);
      committeesGrid.appendChild(card);
    });

  } catch (error) {
    // Show error state
    loadingSkeleton.classList.add('hidden');
    errorState.classList.remove('hidden');
    console.error('Failed to load committees:', error);
  }
});

function createCommitteeCard(committee) {
  const card = document.createElement('div');
  card.className = 'committee-card';

  const isFull = committee.filled_seats >= committee.total_seats;
  const isPNA = committee.short_name === 'PNA';
  const capacityPercentage = Math.round((committee.filled_seats / committee.total_seats) * 100);

  // Determine progress bar color
  let fillColor = '#2563eb'; // primary blue
  if (isFull) {
    fillColor = '#ef4444'; // red
  } else if (capacityPercentage > 70) {
    fillColor = '#f59e0b'; // amber
  }

  // Build badge HTML
  let badgeHtml = '';
  if (isFull) {
    badgeHtml = '<span class="badge badge-full">Full</span>';
  } else if (isPNA) {
    badgeHtml = '<span class="badge badge-pna">National</span>';
  }

  card.innerHTML = `
    <div class="committee-header">
      <span class="committee-code">${committee.short_name}</span>
      ${badgeHtml}
    </div>
    <h3 class="committee-name">${committee.full_name}</h3>
    <p class="committee-lang">${committee.language}</p>
    <div class="committee-progress">
      <div class="progress-labels">
        <span>Capacity</span>
        <span>${committee.filled_seats}/${committee.total_seats}</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" style="width:${capacityPercentage}%;background:${fillColor}"></div>
      </div>
    </div>
    <div class="committee-seats">${capacityPercentage}% filled</div>
  `;

  return card;
}
