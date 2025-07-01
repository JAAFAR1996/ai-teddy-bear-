/**
 * Dependency Injection Container
 * 
 * Centralized container for all dependencies following
 * Clean Architecture principles and SOLID patterns
 */

import { ApiClient } from '../infrastructure/api/ApiClient';
import { LocalStorageService } from '../infrastructure/storage/LocalStorageService';
import { ChildRepository, ConversationRepository } from '../infrastructure/repositories';
import { ChildManagementUseCases, ConversationManagementUseCases } from '../application/useCases';

class DependencyContainer {
  constructor() {
    this.dependencies = new Map();
    this.singletons = new Map();
    this.isInitialized = false;
  }

  async initialize(config = {}) {
    if (this.isInitialized) {
      console.warn('DependencyContainer already initialized');
      return;
    }

    console.log('🔧 Initializing Dependency Container...');

    try {
      // Initialize Infrastructure Layer
      await this.initializeInfrastructure(config);
      
      // Initialize Application Layer
      await this.initializeApplication(config);
      
      // Initialize Presentation Layer
      await this.initializePresentation(config);

      this.isInitialized = true;
      console.log('✅ Dependency Container initialized successfully');
      
      // Log dependency graph
      this.logDependencyGraph();
    } catch (error) {
      console.error('❌ Failed to initialize Dependency Container:', error);
      throw error;
    }
  }

  async initializeInfrastructure(config) {
    console.log('🏗️ Initializing Infrastructure Layer...');

    // API Client (Singleton)
    const apiClient = new ApiClient({
      baseURL: config.apiBaseUrl || process.env.REACT_APP_API_BASE_URL,
      timeout: config.apiTimeout || 10000,
      retryAttempts: config.retryAttempts || 3
    });
    this.registerSingleton('apiClient', apiClient);

    // Local Storage Service (Singleton)
    const localStorageService = new LocalStorageService({
      prefix: config.storagePrefix || 'ai_teddy_',
      encrypt: config.encryptStorage || false,
      defaultExpiration: config.defaultCacheExpiration || null
    });
    this.registerSingleton('localStorageService', localStorageService);

    // Event Bus (Simple implementation)
    const eventBus = {
      listeners: new Map(),
      
      async emit(event, data) {
        console.log(`📡 Event emitted: ${event}`, data);
        const listeners = this.listeners.get(event) || [];
        await Promise.all(listeners.map(listener => listener(data)));
      },
      
      on(event, listener) {
        const listeners = this.listeners.get(event) || [];
        listeners.push(listener);
        this.listeners.set(event, listeners);
      },
      
      off(event, listener) {
        const listeners = this.listeners.get(event) || [];
        const filtered = listeners.filter(l => l !== listener);
        this.listeners.set(event, filtered);
      }
    };
    this.registerSingleton('eventBus', eventBus);

    // Repositories (Singletons)
    const childRepository = new ChildRepository({
      apiClient: this.get('apiClient'),
      localStorageService: this.get('localStorageService')
    });
    this.registerSingleton('childRepository', childRepository);

    const conversationRepository = new ConversationRepository({
      apiClient: this.get('apiClient'),
      localStorageService: this.get('localStorageService')
    });
    this.registerSingleton('conversationRepository', conversationRepository);

    console.log('✅ Infrastructure Layer initialized');
  }

  async initializeApplication(config) {
    console.log('📋 Initializing Application Layer...');

    // AI Service (Mock implementation)
    const aiService = {
      async generateResponse({ message, conversationHistory, childAge, emotionalState, topics }) {
        // Mock AI response - would integrate with actual AI service
        const responses = [
          'مرحباً! كيف حالك اليوم؟',
          'هذا سؤال رائع! دعني أفكر...',
          'أحب أن أتحدث معك، أنت ذكي جداً!',
          'هل تريد أن نلعب لعبة تعليمية؟'
        ];
        
        await new Promise(resolve => setTimeout(resolve, 500)); // Simulate API delay
        
        return {
          text: responses[Math.floor(Math.random() * responses.length)],
          emotionalState: ['happy', 'excited', 'content'][Math.floor(Math.random() * 3)],
          topics: ['play', 'learning', 'conversation'][Math.floor(Math.random() * 3)]
        };
      }
    };
    this.registerSingleton('aiService', aiService);

    // Use Cases (Singletons)
    const childManagementUseCases = new ChildManagementUseCases({
      childRepository: this.get('childRepository'),
      eventBus: this.get('eventBus')
    });
    this.registerSingleton('childManagementUseCases', childManagementUseCases);

    const conversationManagementUseCases = new ConversationManagementUseCases({
      conversationRepository: this.get('conversationRepository'),
      childRepository: this.get('childRepository'),
      eventBus: this.get('eventBus'),
      aiService: this.get('aiService')
    });
    this.registerSingleton('conversationManagementUseCases', conversationManagementUseCases);

    console.log('✅ Application Layer initialized');
  }

  async initializePresentation(config) {
    console.log('🎨 Initializing Presentation Layer...');

    // PDF Service
    const pdfService = {
      async generateReport(data, options) {
        console.log('📄 Generating PDF report...', { data, options });
        // Mock PDF generation
        return {
          success: true,
          filename: `report_${Date.now()}.pdf`,
          size: '2.3 MB'
        };
      }
    };
    this.registerSingleton('pdfService', pdfService);

    // Notification Service
    const notificationService = {
      async send(type, message, options = {}) {
        console.log(`🔔 Notification: [${type}] ${message}`, options);
        // Would integrate with browser notifications or push service
      }
    };
    this.registerSingleton('notificationService', notificationService);

    console.log('✅ Presentation Layer initialized');
  }

  // Dependency Management Methods
  register(key, factory, options = {}) {
    this.dependencies.set(key, {
      factory,
      singleton: options.singleton || false,
      lazy: options.lazy || true
    });
  }

  registerSingleton(key, instance) {
    this.singletons.set(key, instance);
  }

  get(key) {
    // Check if singleton exists
    if (this.singletons.has(key)) {
      return this.singletons.get(key);
    }

    // Check if dependency is registered
    if (!this.dependencies.has(key)) {
      throw new Error(`Dependency '${key}' not registered`);
    }

    const dependency = this.dependencies.get(key);
    const instance = dependency.factory();

    // Store as singleton if needed
    if (dependency.singleton) {
      this.singletons.set(key, instance);
    }

    return instance;
  }

  has(key) {
    return this.singletons.has(key) || this.dependencies.has(key);
  }

  // Utility Methods
  logDependencyGraph() {
    console.log('📊 Dependency Graph:');
    console.log('Singletons:', Array.from(this.singletons.keys()));
    console.log('Factories:', Array.from(this.dependencies.keys()));
  }

  async healthCheck() {
    console.log('🏥 Running health check...');
    
    const results = {};
    
    try {
      // Check API Client
      const apiClient = this.get('apiClient');
      results.apiClient = await apiClient.healthCheck();
    } catch (error) {
      results.apiClient = { status: 'error', message: error.message };
    }

    try {
      // Check Local Storage
      const localStorageService = this.get('localStorageService');
      results.localStorage = {
        status: localStorageService.isAvailable ? 'healthy' : 'unavailable',
        stats: localStorageService.getStorageStats()
      };
    } catch (error) {
      results.localStorage = { status: 'error', message: error.message };
    }

    console.log('Health Check Results:', results);
    return results;
  }

  async cleanup() {
    console.log('🧹 Cleaning up dependencies...');
    
    try {
      // Cleanup storage
      const localStorageService = this.get('localStorageService');
      await localStorageService.cleanup();
      
      // Clear dependency maps
      this.dependencies.clear();
      this.singletons.clear();
      
      this.isInitialized = false;
      console.log('✅ Cleanup completed');
    } catch (error) {
      console.error('❌ Cleanup failed:', error);
    }
  }

  // Development helpers
  getDependencyInfo() {
    return {
      initialized: this.isInitialized,
      singletonCount: this.singletons.size,
      factoryCount: this.dependencies.size,
      singletons: Array.from(this.singletons.keys()),
      factories: Array.from(this.dependencies.keys())
    };
  }

  // Event handling for dependency changes
  onDependencyChange(callback) {
    this.get('eventBus').on('dependency:changed', callback);
  }

  async replaceDependency(key, newInstance) {
    console.log(`🔄 Replacing dependency: ${key}`);
    
    const oldInstance = this.singletons.get(key);
    this.singletons.set(key, newInstance);
    
    await this.get('eventBus').emit('dependency:changed', { 
      key, 
      oldInstance, 
      newInstance 
    });
  }
}

// Create global container instance
export const container = new DependencyContainer();

// Convenience methods for common dependencies
export const getDependency = (key) => container.get(key);
export const registerDependency = (key, factory, options) => container.register(key, factory, options);
export const initializeContainer = (config) => container.initialize(config);

// Export for testing
export { DependencyContainer }; 