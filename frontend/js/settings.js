// Settings Fetcher for real-time admin configuration
// Fetches and caches admin settings from backend API

class SettingsManager {
  constructor() {
    this.settingsCache = new Map();
    this.cacheTimestamp = null;
    this.CACHE_TTL = 30000; // 30 seconds cache TTL
  }

  /**
   * Fetch all settings from backend
   * @returns {Promise<Array<{key: string, value: any}>>}
   */
  async fetchAllSettings() {
    const now = Date.now();

    // Return cached settings if still valid
    if (this.cacheTimestamp && (now - this.cacheTimestamp) < this.CACHE_TTL) {
      return Array.from(this.settingsCache.entries()).map(([key, value]) => ({ key, value }));
    }

    try {
      // Use public endpoint for general fetching
      const response = await fetch('/api/v1/settings');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Handle nested response structure: { success: true, data: { settings: [...] } }
      const settingsArray = data.data?.settings || data.settings || [];

      // Update cache
      this.settingsCache.clear();
      settingsArray.forEach(setting => {
        this.settingsCache.set(setting.key, this.parseSettingValue(setting.value));
      });
      this.cacheTimestamp = now;

      return settingsArray.map(setting => ({
        key: setting.key,
        value: this.parseSettingValue(setting.value)
      }));
    } catch (error) {
      console.error('Failed to fetch settings:', error);
      // Return cached settings even if stale, as fallback
      if (this.settingsCache.size > 0) {
        return Array.from(this.settingsCache.entries()).map(([key, value]) => ({ key, value }));
      }
      throw error;
    }
  }

  /**
   * Get a specific setting by key
   * @param {string} key - Setting key to fetch
   * @returns {Promise<any>} Setting value
   */
  async getSetting(key) {
    const now = Date.now();

    // Return cached setting if still valid
    if (this.cacheTimestamp && (now - this.cacheTimestamp) < this.CACHE_TTL && this.settingsCache.has(key)) {
      return this.settingsCache.get(key);
    }

    try {
      // Use public endpoint for frontend
      const response = await fetch(`/api/v1/settings`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      // Handle nested response structure: { success: true, data: { settings: [...] } }
      const settingsArray = data.data?.settings || data.settings || [];

      // Update cache
      this.settingsCache.clear();
      settingsArray.forEach(setting => {
        this.settingsCache.set(setting.key, this.parseSettingValue(setting.value));
      });
      this.cacheTimestamp = now;

      const setting = settingsArray.find(s => s.key === key);
      return setting ? this.parseSettingValue(setting.value) : null;
    } catch (error) {
      console.error(`Failed to fetch setting ${key}:`, error);
      // Return cached setting even if stale, as fallback
      if (this.settingsCache.has(key)) {
        return this.settingsCache.get(key);
      }
      return null;
    }
  }

  /**
   * Parse setting value from string to appropriate type
   * @param {string} value - Raw string value from database
   * @returns {any} Parsed value
   */
  parseSettingValue(value) {
    if (value === null || value === undefined) return null;

    // Try to parse as JSON
    try {
      return JSON.parse(value);
    } catch (e) {
      // If not JSON, return as string
      return value;
    }
  }

  /**
   * Check if registration is currently open
   * @returns {Promise<boolean>}
   */
  async isRegistrationOpen() {
    const value = await this.getSetting('registration_open');
    if (value === null) return true; // Default to open if settings cannot be fetched (e.g. 401 Unauthorized)
    return value === true || value === 'true';
  }

  /**
   * Check if transfers are currently enabled
   * @returns {Promise<boolean>}
   */
  async isTransferEnabled() {
    const value = await this.getSetting('transfer_enabled');
    return value === true || value === 'true';
  }

  /**
   * Get registration deadline timestamp
   * @returns {Promise<number|null>} Unix timestamp in milliseconds
   */
  async getRegistrationDeadline() {
    const value = await this.getSetting('registration_deadline');
    if (value) {
      const date = new Date(value);
      return isNaN(date.getTime()) ? null : date.getTime();
    }
    return null;
  }

  /**
   * Get transfer deadline timestamp
   * @returns {Promise<number|null>} Unix timestamp in milliseconds
   */
  async getTransferDeadline() {
    const value = await this.getSetting('transfer_deadline');
    if (value) {
      const date = new Date(value);
      return isNaN(date.getTime()) ? null : date.getTime();
    }
    return null;
  }

  /**
   * Get event title
   * @returns {Promise<string|null>}
   */
  async getEventTitle() {
    return await this.getSetting('event_title');
  }

  /**
   * Get event date
   * @returns {Promise<string|null>}
   */
  async getEventDate() {
    return await this.getSetting('event_date');
  }

  /**
   * Get event venue
   * @returns {Promise<string|null>}
   */
  async getEventVenue() {
    return await this.getSetting('event_venue');
  }
}

// Export singleton instance
const settingsManager = new SettingsManager();
window.settingsManager = settingsManager;