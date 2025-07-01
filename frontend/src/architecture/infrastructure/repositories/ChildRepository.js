/**
 * Child Repository
 * 
 * Handles data persistence for Child entities
 */

export class ChildRepository {
  constructor({ apiClient, localStorageService }) {
    this.apiClient = apiClient;
    this.localStorageService = localStorageService;
    this.cacheKey = 'children';
  }

  async save(child) {
    try {
      let savedChild;

      if (child.id && child.id.includes('temp')) {
        // New child - create via API
        savedChild = await this.apiClient.post('/children', child.toJSON());
      } else {
        // Update existing child
        savedChild = await this.apiClient.put(`/children/${child.id}`, child.toJSON());
      }

      // Update local cache
      await this.updateCache(savedChild);

      return savedChild;
    } catch (error) {
      console.error('Failed to save child:', error);
      
      // Fallback to local storage
      const localChild = child.toJSON();
      localChild.id = localChild.id || this.generateLocalId();
      
      await this.saveToLocalStorage(localChild);
      return localChild;
    }
  }

  async findById(childId) {
    try {
      // Try API first
      const child = await this.apiClient.get(`/children/${childId}`);
      
      // Cache the result
      await this.updateCache(child);
      
      return child;
    } catch (error) {
      console.warn('API call failed, trying local storage:', error);
      
      // Fallback to local storage
      return await this.findInLocalStorage(childId);
    }
  }

  async findByParentId(parentId) {
    try {
      // Try API first
      const children = await this.apiClient.get(`/children?parentId=${parentId}`);
      
      // Cache the results
      for (const child of children) {
        await this.updateCache(child);
      }
      
      return children;
    } catch (error) {
      console.warn('API call failed, trying local storage:', error);
      
      // Fallback to local storage
      return await this.findByParentInLocalStorage(parentId);
    }
  }

  async delete(childId) {
    try {
      // Delete from API
      await this.apiClient.delete(`/children/${childId}`);
      
      // Remove from cache
      await this.removeFromCache(childId);
      
      return true;
    } catch (error) {
      console.error('Failed to delete child:', error);
      
      // Remove from local storage as fallback
      await this.removeFromLocalStorage(childId);
      throw error;
    }
  }

  // Cache Management
  async updateCache(child) {
    try {
      const cached = await this.localStorageService.get(this.cacheKey) || {};
      cached[child.id] = {
        ...child,
        cachedAt: new Date().toISOString()
      };
      
      await this.localStorageService.set(this.cacheKey, cached);
    } catch (error) {
      console.warn('Failed to update cache:', error);
    }
  }

  async removeFromCache(childId) {
    try {
      const cached = await this.localStorageService.get(this.cacheKey) || {};
      delete cached[childId];
      
      await this.localStorageService.set(this.cacheKey, cached);
    } catch (error) {
      console.warn('Failed to remove from cache:', error);
    }
  }

  // Local Storage Fallbacks
  async saveToLocalStorage(child) {
    const cached = await this.localStorageService.get(this.cacheKey) || {};
    cached[child.id] = {
      ...child,
      savedAt: new Date().toISOString(),
      isLocal: true
    };
    
    await this.localStorageService.set(this.cacheKey, cached);
    return cached[child.id];
  }

  async findInLocalStorage(childId) {
    const cached = await this.localStorageService.get(this.cacheKey) || {};
    return cached[childId] || null;
  }

  async findByParentInLocalStorage(parentId) {
    const cached = await this.localStorageService.get(this.cacheKey) || {};
    
    return Object.values(cached).filter(child => child.parentId === parentId);
  }

  async removeFromLocalStorage(childId) {
    const cached = await this.localStorageService.get(this.cacheKey) || {};
    delete cached[childId];
    
    await this.localStorageService.set(this.cacheKey, cached);
  }

  generateLocalId() {
    return `local_child_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
} 