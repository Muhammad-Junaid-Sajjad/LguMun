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
      `${committees.length} committees · ${totalSeats} total seats`;

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
  let fillColor = '#C9A227'; // gold
  if (isFull) {
    fillColor = '#C0392B'; // red
  } else if (capacityPercentage > 70) {
    fillColor = '#D4900A'; // amber
  }

  // Build badge HTML
  let badgeHtml = '';
  if (isFull) {
    badgeHtml = '<div class="committee-badge full">FULL</div>';
  } else if (isPNA) {
    badgeHtml = '<div class="committee-badge pna">National</div>';
  }

  card.innerHTML = `
    ${badgeHtml}
    <div class="committee-code">${committee.short_name}</div>
    <div class="committee-name">${committee.full_name}</div>
    <div class="committee-lang">${committee.language}</div>
    <div class="committee-progress-bg">
      <div class="committee-progress-fill" style="width:${capacityPercentage}%;background:${fillColor}"></div>
    </div>
    <div class="committee-seats">${committee.filled_seats}/${committee.total_seats} seats filled</div>
  `;

  return card;
}
