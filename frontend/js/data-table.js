/* Data Table - Filtering and Sorting */
/* Industrial-grade table functionality */

class DataTable {
  constructor(tableId, options = {}) {
    this.table = document.getElementById(tableId);
    this.tbody = this.table?.querySelector('tbody');
    this.originalRows = [];
    this.filteredRows = [];
    this.options = {
      searchable: true,
      sortable: true,
      ...options
    };

    if (this.tbody) {
      this.init();
    }
  }

  init() {
    // Store original rows
    this.originalRows = Array.from(this.tbody.querySelectorAll('tr'));
    this.filteredRows = [...this.originalRows];

    // Setup sorting if enabled
    if (this.options.sortable) {
      this.setupSorting();
    }
  }

  setupSorting() {
    const headers = this.table.querySelectorAll('thead th[data-sortable]');
    headers.forEach((header, index) => {
      header.style.cursor = 'pointer';
      header.addEventListener('click', () => this.sortByColumn(index));
    });
  }

  sortByColumn(columnIndex) {
    const rows = Array.from(this.tbody.querySelectorAll('tr'));
    const isAscending = this.currentSort?.column === columnIndex && this.currentSort?.direction === 'asc';
    const direction = isAscending ? 'desc' : 'asc';

    rows.sort((a, b) => {
      const aValue = a.cells[columnIndex]?.textContent.trim() || '';
      const bValue = b.cells[columnIndex]?.textContent.trim() || '';

      // Try numeric comparison first
      const aNum = parseFloat(aValue);
      const bNum = parseFloat(bValue);

      if (!isNaN(aNum) && !isNaN(bNum)) {
        return direction === 'asc' ? aNum - bNum : bNum - aNum;
      }

      // Fall back to string comparison
      return direction === 'asc'
        ? aValue.localeCompare(bValue)
        : bValue.localeCompare(aValue);
    });

    // Clear and re-append sorted rows
    this.tbody.innerHTML = '';
    rows.forEach(row => this.tbody.appendChild(row));

    this.currentSort = { column: columnIndex, direction };
  }

  filter(filters) {
    const searchTerm = filters.search?.toLowerCase() || '';
    const language = filters.language || 'all';
    const status = filters.status || 'all';

    this.filteredRows = this.originalRows.filter(row => {
      const text = row.textContent.toLowerCase();
      const matchesSearch = !searchTerm || text.includes(searchTerm);

      // Get language from row
      const langCell = row.querySelector('[data-language]');
      const rowLanguage = langCell?.dataset.language || '';
      const matchesLanguage = language === 'all' || rowLanguage === language;

      // Get status from row
      const statusCell = row.querySelector('[data-status]');
      const rowStatus = statusCell?.dataset.status || '';
      const matchesStatus = status === 'all' || rowStatus === status;

      return matchesSearch && matchesLanguage && matchesStatus;
    });

    this.render();
  }

  render() {
    this.tbody.innerHTML = '';

    if (this.filteredRows.length === 0) {
      const colspan = this.table.querySelectorAll('thead th').length;
      this.tbody.innerHTML = `
        <tr>
          <td colspan="${colspan}" style="text-align: center; padding: 2rem; color: var(--text-tertiary);">
            No committees found matching your filters
          </td>
        </tr>
      `;
    } else {
      this.filteredRows.forEach(row => this.tbody.appendChild(row));
    }
  }

  getFilteredCount() {
    return this.filteredRows.length;
  }

  getTotalCount() {
    return this.originalRows.length;
  }
}

// Setup filter controls
function setupFilters(tableInstance) {
  const searchInput = document.getElementById('search-input');
  const languageFilter = document.getElementById('language-filter');
  const statusFilter = document.getElementById('status-filter');
  const resultsCount = document.getElementById('results-count');

  function applyFilters() {
    const filters = {
      search: searchInput?.value || '',
      language: languageFilter?.value || 'all',
      status: statusFilter?.value || 'all'
    };

    tableInstance.filter(filters);

    // Update results count
    if (resultsCount) {
      const filtered = tableInstance.getFilteredCount();
      const total = tableInstance.getTotalCount();
      resultsCount.textContent = filtered === total
        ? `${total} committees`
        : `${filtered} of ${total} committees`;
    }
  }

  // Debounced search
  if (searchInput) {
    searchInput.addEventListener('input', debounce(applyFilters, 300));
  }

  if (languageFilter) {
    languageFilter.addEventListener('change', applyFilters);
  }

  if (statusFilter) {
    statusFilter.addEventListener('change', applyFilters);
  }
}
