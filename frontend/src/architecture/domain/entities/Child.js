/**
 * Child Entity
 * 
 * Represents a child in the system with all business rules
 */

export class Child {
  constructor({
    id,
    name,
    age,
    parentId,
    preferences = {},
    settings = {},
    stats = {},
    createdAt = new Date(),
    updatedAt = new Date()
  }) {
    this.id = id;
    this.name = name;
    this.age = age;
    this.parentId = parentId;
    this.preferences = preferences;
    this.settings = settings;
    this.stats = stats;
    this.createdAt = createdAt;
    this.updatedAt = updatedAt;
    
    this.validateChild();
  }

  validateChild() {
    if (!this.name || this.name.trim().length === 0) {
      throw new Error('Child name is required');
    }
    
    if (!this.age || this.age < 1 || this.age > 18) {
      throw new Error('Child age must be between 1 and 18');
    }
    
    if (!this.parentId) {
      throw new Error('Parent ID is required');
    }
  }

  // Business Logic Methods
  isToddler() {
    return this.age >= 1 && this.age <= 3;
  }

  isPreschooler() {
    return this.age >= 4 && this.age <= 5;
  }

  isSchoolAge() {
    return this.age >= 6 && this.age <= 12;
  }

  isTeenager() {
    return this.age >= 13 && this.age <= 18;
  }

  getAgeGroup() {
    if (this.isToddler()) return 'toddler';
    if (this.isPreschooler()) return 'preschooler';
    if (this.isSchoolAge()) return 'school-age';
    if (this.isTeenager()) return 'teenager';
    return 'unknown';
  }

  getMaxDailyInteractionTime() {
    // Business rule: different age groups have different limits
    const limits = {
      toddler: 15, // 15 minutes
      preschooler: 30, // 30 minutes  
      'school-age': 45, // 45 minutes
      teenager: 60 // 60 minutes
    };
    
    return limits[this.getAgeGroup()] || 30;
  }

  updateProfile(updates) {
    const allowedUpdates = ['name', 'preferences', 'settings'];
    
    Object.keys(updates).forEach(key => {
      if (allowedUpdates.includes(key)) {
        this[key] = updates[key];
      }
    });
    
    this.updatedAt = new Date();
    this.validateChild();
    
    return this;
  }

  toJSON() {
    return {
      id: this.id,
      name: this.name,
      age: this.age,
      parentId: this.parentId,
      preferences: this.preferences,
      settings: this.settings,
      stats: this.stats,
      ageGroup: this.getAgeGroup(),
      maxDailyTime: this.getMaxDailyInteractionTime(),
      createdAt: this.createdAt,
      updatedAt: this.updatedAt
    };
  }
} 