interface ServiceRegistration {
  factory: () => any;
  singleton?: boolean;
  instance?: any;
}

export class Container {
  private services = new Map<symbol | string, ServiceRegistration>();

  register<T>(token: symbol | string, factory: () => T, options?: { singleton?: boolean }): void {
    this.services.set(token, {
      factory,
      singleton: options?.singleton ?? true,
    });
  }

  resolve<T>(token: symbol | string): T {
    const registration = this.services.get(token);
    
    if (!registration) {
      throw new Error(`Service ${String(token)} not registered`);
    }

    if (registration.singleton) {
      if (!registration.instance) {
        registration.instance = registration.factory();
      }
      return registration.instance;
    }

    return registration.factory();
  }

  clear(): void {
    this.services.clear();
  }
}

// Service tokens
export const SERVICE_TOKENS = {
  // Infrastructure services
  API_SERVICE: Symbol('ApiService'),
  AUTH_SERVICE: Symbol('AuthService'),
  WEBSOCKET_SERVICE: Symbol('WebSocketService'),
  STORAGE_SERVICE: Symbol('StorageService'),
  
  // Domain services
  CHILD_SERVICE: Symbol('ChildService'),
  CONVERSATION_SERVICE: Symbol('ConversationService'),
  EMOTION_SERVICE: Symbol('EmotionService'),
  ANALYTICS_SERVICE: Symbol('AnalyticsService'),
  REPORT_SERVICE: Symbol('ReportService'),
  
  // Use cases
  START_CONVERSATION_USE_CASE: Symbol('StartConversationUseCase'),
  ANALYZE_EMOTION_USE_CASE: Symbol('AnalyzeEmotionUseCase'),
  GENERATE_REPORT_USE_CASE: Symbol('GenerateReportUseCase'),
  
  // Repositories
  CHILD_REPOSITORY: Symbol('ChildRepository'),
  CONVERSATION_REPOSITORY: Symbol('ConversationRepository'),
  EMOTION_REPOSITORY: Symbol('EmotionRepository'),
};

// Create and configure container
export const container = new Container();

// Register services (these will be implemented)
// Infrastructure layer
container.register(SERVICE_TOKENS.API_SERVICE, () => {
  // Will be implemented
  return {};
});

container.register(SERVICE_TOKENS.AUTH_SERVICE, () => {
  // Will be implemented
  return {};
});

container.register(SERVICE_TOKENS.WEBSOCKET_SERVICE, () => {
  // Will be implemented
  return {};
});

container.register(SERVICE_TOKENS.STORAGE_SERVICE, () => {
  // Will be implemented
  return {};
}); 