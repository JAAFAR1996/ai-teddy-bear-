/**
 * Conversation Repository
 * 
 * Handles data persistence for Conversation entities
 */

export class ConversationRepository {
  constructor({ apiClient, localStorageService }) {
    this.apiClient = apiClient;
    this.localStorageService = localStorageService;
    this.cacheKey = 'conversations';
  }

  async save(conversation) {
    try {
      let savedConversation;

      if (conversation.id && conversation.id.includes('temp')) {
        // New conversation - create via API
        savedConversation = await this.apiClient.post('/conversations', conversation.toJSON());
      } else {
        // Update existing conversation
        savedConversation = await this.apiClient.put(`/conversations/${conversation.id}`, conversation.toJSON());
      }

      // Update local cache
      await this.updateCache(savedConversation);

      return savedConversation;
    } catch (error) {
      console.error('Failed to save conversation:', error);
      
      // Fallback to local storage
      const localConversation = conversation.toJSON();
      localConversation.id = localConversation.id || this.generateLocalId();
      
      await this.saveToLocalStorage(localConversation);
      return localConversation;
    }
  }

  async findById(conversationId) {
    try {
      // Try API first
      const conversation = await this.apiClient.get(`/conversations/${conversationId}`);
      
      // Cache the result
      await this.updateCache(conversation);
      
      return conversation;
    } catch (error) {
      console.warn('API call failed, trying local storage:', error);
      
      // Fallback to local storage
      return await this.findInLocalStorage(conversationId);
    }
  }

  async findByChildId(childId, { limit = 20, offset = 0 } = {}) {
    try {
      // Try API first
      const conversations = await this.apiClient.get(
        `/conversations?childId=${childId}&limit=${limit}&offset=${offset}`
      );
      
      // Cache the results
      for (const conversation of conversations) {
        await this.updateCache(conversation);
      }
      
      return conversations;
    } catch (error) {
      console.warn('API call failed, trying local storage:', error);
      
      // Fallback to local storage
      return await this.findByChildInLocalStorage(childId, { limit, offset });
    }
  }

  async findByChildIdAndDate(childId, date) {
    try {
      const dateStr = date.toISOString().split('T')[0]; // YYYY-MM-DD format
      
      // Try API first
      const conversations = await this.apiClient.get(
        `/conversations?childId=${childId}&date=${dateStr}`
      );
      
      // Cache the results
      for (const conversation of conversations) {
        await this.updateCache(conversation);
      }
      
      return conversations;
    } catch (error) {
      console.warn('API call failed, trying local storage:', error);
      
      // Fallback to local storage
      return await this.findByChildAndDateInLocalStorage(childId, date);
    }
  }

  async delete(conversationId) {
    try {
      // Delete from API
      await this.apiClient.delete(`/conversations/${conversationId}`);
      
      // Remove from cache
      await this.removeFromCache(conversationId);
      
      return true;
    } catch (error) {
      console.error('Failed to delete conversation:', error);
      
      // Remove from local storage as fallback
      await this.removeFromLocalStorage(conversationId);
      throw error;
    }
  }

  // Cache Management
  async updateCache(conversation) {
    try {
      const cached = await this.localStorageService.get(this.cacheKey) || {};
      cached[conversation.id] = {
        ...conversation,
        cachedAt: new Date().toISOString()
      };
      
      await this.localStorageService.set(this.cacheKey, cached);
    } catch (error) {
      console.warn('Failed to update cache:', error);
    }
  }

  async removeFromCache(conversationId) {
    try {
      const cached = await this.localStorageService.get(this.cacheKey) || {};
      delete cached[conversationId];
      
      await this.localStorageService.set(this.cacheKey, cached);
    } catch (error) {
      console.warn('Failed to remove from cache:', error);
    }
  }

  // Local Storage Fallbacks
  async saveToLocalStorage(conversation) {
    const cached = await this.localStorageService.get(this.cacheKey) || {};
    cached[conversation.id] = {
      ...conversation,
      savedAt: new Date().toISOString(),
      isLocal: true
    };
    
    await this.localStorageService.set(this.cacheKey, cached);
    return cached[conversation.id];
  }

  async findInLocalStorage(conversationId) {
    const cached = await this.localStorageService.get(this.cacheKey) || {};
    return cached[conversationId] || null;
  }

  async findByChildInLocalStorage(childId, { limit = 20, offset = 0 } = {}) {
    const cached = await this.localStorageService.get(this.cacheKey) || {};
    
    const conversations = Object.values(cached)
      .filter(conv => conv.childId === childId)
      .sort((a, b) => new Date(b.startTime) - new Date(a.startTime))
      .slice(offset, offset + limit);
      
    return conversations;
  }

  async findByChildAndDateInLocalStorage(childId, date) {
    const cached = await this.localStorageService.get(this.cacheKey) || {};
    const targetDate = date.toISOString().split('T')[0];
    
    return Object.values(cached).filter(conv => {
      const convDate = new Date(conv.startTime).toISOString().split('T')[0];
      return conv.childId === childId && convDate === targetDate;
    });
  }

  async removeFromLocalStorage(conversationId) {
    const cached = await this.localStorageService.get(this.cacheKey) || {};
    delete cached[conversationId];
    
    await this.localStorageService.set(this.cacheKey, cached);
  }

  generateLocalId() {
    return `local_conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
} 