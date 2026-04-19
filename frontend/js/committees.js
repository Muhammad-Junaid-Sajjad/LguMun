document.addEventListener('DOMContentLoaded', async () => {
  const committeesGrid = document.getElementById('committees-grid');
  const loadingSkeleton = document.getElementById('loading-skeleton');
  const errorState = document.getElementById('error-state');

  try {
    const data = await apiGet('/committees');
    const committees = data.data.committees;

    // Hide skeleton
    loadingSkeleton.classList.add('hidden');

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
  card.className = 'card';

  const title = document.createElement('h3');
  title.className = 'card-title';
  title.textContent = committee.short_name;

  const subtitle = document.createElement('p');
  subtitle.className = 'card-subtitle';
  subtitle.textContent = committee.full_name;

  const chair = document.createElement('p');
  chair.textContent = `Chair: ${committee.chair_name}`;

  const agenda = document.createElement('p');
  agenda.textContent = `Agenda: ${committee.agenda_1}`;

  const language = document.createElement('p');
  language.textContent = `Language: ${committee.language}`;

  const seats = document.createElement('p');
  seats.textContent = `Seats: ${committee.filled_seats}/${committee.total_seats}`;

  // Progress bar
  const progressBar = document.createElement('div');
  progressBar.className = 'progress-bar';

  const progressFill = document.createElement('div');
  progressFill.className = 'progress-fill';
  progressFill.style.width = `${committee.capacity_percentage}%`;

  progressBar.appendChild(progressFill);

  // Full badge
  if (committee.is_full) {
    const badge = document.createElement('span');
    badge.className = 'badge';
    badge.textContent = 'FULL';
    title.appendChild(badge);
  }

  card.appendChild(title);
  card.appendChild(subtitle);
  card.appendChild(chair);
  card.appendChild(agenda);
  card.appendChild(language);
  card.appendChild(seats);
  card.appendChild(progressBar);

  return card;
}
