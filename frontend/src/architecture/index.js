/**
 * Clean Architecture Index
 * 
 * This file exports the main architectural layers and patterns
 * following Clean Architecture principles.
 * 
 * Layers:
 * 1. Domain - Business Logic & Entities
 * 2. Application - Use Cases & Services  
 * 3. Infrastructure - External APIs, Storage, etc.
 * 4. Presentation - UI Components & Views
 */

// Domain Layer
export * from './domain';

// Application Layer  
export * from './application';

// Infrastructure Layer
export * from './infrastructure';

// Presentation Layer
export * from './presentation';

// Shared Utilities
export * from './shared'; 