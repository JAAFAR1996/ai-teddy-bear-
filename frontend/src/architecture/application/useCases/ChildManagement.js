/**
 * Child Management Use Cases
 * 
 * Contains all business use cases related to child management
 */

import { Child } from '../../domain/entities';

export class ChildManagementUseCases {
  constructor({ childRepository, eventBus }) {
    this.childRepository = childRepository;
    this.eventBus = eventBus;
  }

  async createChild({ name, age, parentId, preferences = {}, settings = {} }) {
    try {
      // Create child entity with business validation
      const child = new Child({
        id: this.generateId(),
        name,
        age,
        parentId,
        preferences,
        settings: {
          maxDailyTime: new Child({ name: 'temp', age, parentId: 'temp' }).getMaxDailyInteractionTime(),
          ...settings
        }
      });

      // Save to repository
      const savedChild = await this.childRepository.save(child);

      // Emit domain event
      await this.eventBus.emit('child.created', {
        childId: savedChild.id,
        parentId: savedChild.parentId,
        ageGroup: savedChild.getAgeGroup()
      });

      return savedChild;
    } catch (error) {
      throw new Error(`Failed to create child: ${error.message}`);
    }
  }

  async getChildById(childId) {
    try {
      const childData = await this.childRepository.findById(childId);
      
      if (!childData) {
        throw new Error('Child not found');
      }

      return new Child(childData);
    } catch (error) {
      throw new Error(`Failed to get child: ${error.message}`);
    }
  }

  async updateChildProfile(childId, updates) {
    try {
      const child = await this.getChildById(childId);
      
      // Use domain logic for updates
      child.updateProfile(updates);

      // Save updated child
      const savedChild = await this.childRepository.save(child);

      // Emit domain event
      await this.eventBus.emit('child.updated', {
        childId: savedChild.id,
        updates
      });

      return savedChild;
    } catch (error) {
      throw new Error(`Failed to update child: ${error.message}`);
    }
  }

  async getChildrenByParent(parentId) {
    try {
      const childrenData = await this.childRepository.findByParentId(parentId);
      
      return childrenData.map(data => new Child(data));
    } catch (error) {
      throw new Error(`Failed to get children: ${error.message}`);
    }
  }

  async deleteChild(childId) {
    try {
      const child = await this.getChildById(childId);
      
      await this.childRepository.delete(childId);

      // Emit domain event
      await this.eventBus.emit('child.deleted', {
        childId: child.id,
        parentId: child.parentId
      });

      return true;
    } catch (error) {
      throw new Error(`Failed to delete child: ${error.message}`);
    }
  }

  generateId() {
    return `child_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
} 