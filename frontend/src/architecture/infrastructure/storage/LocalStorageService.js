/**
 * Local Storage Service
 * 
 * Enhanced local storage with error handling, encryption, and expiration
 */

export class LocalStorageService {
  constructor({ prefix = 'ai_teddy_', encrypt = false, defaultExpiration = null }) {
    this.prefix = prefix;
    this.encrypt = encrypt;
    this.defaultExpiration = defaultExpiration;
    
    this.isAvailable = this.checkAvailability();
  }

  checkAvailability() {
    try {
      const testKey = '__test__';
      localStorage.setItem(testKey, 'test');
      localStorage.removeItem(testKey);
      return true;
    } catch (error) {
      console.warn('LocalStorage not available:', error);
      return false;
    }
  }

  async set(key, value, expiration = null) {
    if (!this.isAvailable) {
      throw new Error('LocalStorage not available');
    }

    try {
      const fullKey = this.getFullKey(key);
      const expirationTime = expiration || this.defaultExpiration;
      
      const storageValue = {
        data: value,
        timestamp: Date.now(),
        expiration: expirationTime ? Date.now() + expirationTime : null
      };

      let serializedValue = JSON.stringify(storageValue);
      
      if (this.encrypt) {
        serializedValue = await this.encryptValue(serializedValue);
      }

      localStorage.setItem(fullKey, serializedValue);
      
      console.log(`💾 Stored: ${key} (${this.getStorageSize(serializedValue)} bytes)`);
      
      return true;
    } catch (error) {
      console.error(`Failed to store ${key}:`, error);
      throw error;
    }
  }

  async get(key) {
    if (!this.isAvailable) {
      return null;
    }

    try {
      const fullKey = this.getFullKey(key);
      let serializedValue = localStorage.getItem(fullKey);

      if (!serializedValue) {
        return null;
      }

      if (this.encrypt) {
        serializedValue = await this.decryptValue(serializedValue);
      }

      const storageValue = JSON.parse(serializedValue);

      // Check expiration
      if (storageValue.expiration && Date.now() > storageValue.expiration) {
        console.log(`⏰ Expired: ${key}`);
        await this.remove(key);
        return null;
      }

      console.log(`📖 Retrieved: ${key}`);
      return storageValue.data;
    } catch (error) {
      console.error(`Failed to retrieve ${key}:`, error);
      // Remove corrupted data
      await this.remove(key);
      return null;
    }
  }

  async remove(key) {
    if (!this.isAvailable) {
      return false;
    }

    try {
      const fullKey = this.getFullKey(key);
      localStorage.removeItem(fullKey);
      console.log(`🗑️ Removed: ${key}`);
      return true;
    } catch (error) {
      console.error(`Failed to remove ${key}:`, error);
      return false;
    }
  }

  async clear() {
    if (!this.isAvailable) {
      return false;
    }

    try {
      const keys = this.getAllKeys();
      
      for (const key of keys) {
        localStorage.removeItem(key);
      }

      console.log(`🧹 Cleared ${keys.length} items`);
      return true;
    } catch (error) {
      console.error('Failed to clear storage:', error);
      return false;
    }
  }

  async exists(key) {
    const value = await this.get(key);
    return value !== null;
  }

  getAllKeys() {
    if (!this.isAvailable) {
      return [];
    }

    const keys = [];
    
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(this.prefix)) {
        keys.push(key);
      }
    }

    return keys;
  }

  async getAllItems() {
    const keys = this.getAllKeys();
    const items = {};

    for (const fullKey of keys) {
      const key = this.getOriginalKey(fullKey);
      const value = await this.get(key);
      
      if (value !== null) {
        items[key] = value;
      }
    }

    return items;
  }

  getStorageStats() {
    if (!this.isAvailable) {
      return null;
    }

    const keys = this.getAllKeys();
    let totalSize = 0;

    for (const key of keys) {
      const value = localStorage.getItem(key);
      totalSize += this.getStorageSize(value);
    }

    return {
      itemCount: keys.length,
      totalSize: totalSize,
      totalSizeFormatted: this.formatBytes(totalSize),
      availableSpace: this.getAvailableSpace()
    };
  }

  async cleanup() {
    if (!this.isAvailable) {
      return;
    }

    console.log('🧹 Starting storage cleanup...');
    
    const keys = this.getAllKeys();
    let removedCount = 0;

    for (const fullKey of keys) {
      try {
        const serializedValue = localStorage.getItem(fullKey);
        
        if (!serializedValue) continue;

        let storageValue;
        try {
          if (this.encrypt) {
            const decrypted = await this.decryptValue(serializedValue);
            storageValue = JSON.parse(decrypted);
          } else {
            storageValue = JSON.parse(serializedValue);
          }
        } catch (error) {
          // Remove corrupted data
          localStorage.removeItem(fullKey);
          removedCount++;
          continue;
        }

        // Remove expired items
        if (storageValue.expiration && Date.now() > storageValue.expiration) {
          localStorage.removeItem(fullKey);
          removedCount++;
        }
      } catch (error) {
        console.error(`Error cleaning up ${fullKey}:`, error);
      }
    }

    console.log(`🧹 Cleanup complete: removed ${removedCount} items`);
  }

  // Utility methods
  getFullKey(key) {
    return `${this.prefix}${key}`;
  }

  getOriginalKey(fullKey) {
    return fullKey.replace(this.prefix, '');
  }

  getStorageSize(value) {
    return new Blob([value || '']).size;
  }

  formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  getAvailableSpace() {
    // Rough estimation - not accurate but useful for monitoring
    try {
      let used = 0;
      for (let key in localStorage) {
        if (localStorage.hasOwnProperty(key)) {
          used += localStorage.getItem(key).length;
        }
      }
      
      // Most browsers limit localStorage to ~5-10MB
      const estimated = 5 * 1024 * 1024; // 5MB estimate
      return Math.max(0, estimated - used);
    } catch (error) {
      return null;
    }
  }

  // Encryption methods (basic implementation)
  async encryptValue(value) {
    // Simple Base64 encoding for demonstration
    // In production, use proper encryption like AES
    return btoa(encodeURIComponent(value));
  }

  async decryptValue(encryptedValue) {
    // Simple Base64 decoding for demonstration
    try {
      return decodeURIComponent(atob(encryptedValue));
    } catch (error) {
      throw new Error('Failed to decrypt value');
    }
  }
} 