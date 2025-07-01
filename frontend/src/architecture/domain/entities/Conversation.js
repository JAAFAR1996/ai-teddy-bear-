/**
 * Conversation Entity
 * 
 * Represents a conversation between child and AI teddy bear
 */

export class Conversation {
  constructor({
    id,
    childId,
    messages = [],
    startTime = new Date(),
    endTime = null,
    emotionalState = 'neutral',
    topics = [],
    summary = '',
    isActive = true,
    metadata = {}
  }) {
    this.id = id;
    this.childId = childId;
    this.messages = messages;
    this.startTime = startTime;
    this.endTime = endTime;
    this.emotionalState = emotionalState;
    this.topics = topics;
    this.summary = summary;
    this.isActive = isActive;
    this.metadata = metadata;
    
    this.validateConversation();
  }

  validateConversation() {
    if (!this.childId) {
      throw new Error('Child ID is required for conversation');
    }
    
    if (this.endTime && this.endTime < this.startTime) {
      throw new Error('End time cannot be before start time');
    }
  }

  // Business Logic Methods
  getDuration() {
    const endTime = this.endTime || new Date();
    return Math.round((endTime - this.startTime) / 1000); // in seconds
  }

  getDurationMinutes() {
    return Math.round(this.getDuration() / 60);
  }

  addMessage(message) {
    const conversationMessage = {
      id: Date.now().toString(),
      timestamp: new Date(),
      ...message
    };
    
    this.messages.push(conversationMessage);
    
    // Update emotional state if provided
    if (message.emotionalState) {
      this.emotionalState = message.emotionalState;
    }
    
    // Add topics if provided
    if (message.topics && Array.isArray(message.topics)) {
      this.topics = [...new Set([...this.topics, ...message.topics])];
    }
    
    return conversationMessage;
  }

  endConversation(summary = '') {
    this.endTime = new Date();
    this.isActive = false;
    this.summary = summary;
    
    return this;
  }

  getMessageCount() {
    return this.messages.length;
  }

  getChildMessages() {
    return this.messages.filter(msg => msg.sender === 'child');
  }

  getAIMessages() {
    return this.messages.filter(msg => msg.sender === 'ai');
  }

  isLongConversation() {
    return this.getDurationMinutes() > 10;
  }

  hasEducationalContent() {
    const educationalTopics = ['learning', 'education', 'school', 'math', 'science', 'reading'];
    return this.topics.some(topic => 
      educationalTopics.some(eduTopic => 
        topic.toLowerCase().includes(eduTopic)
      )
    );
  }

  toJSON() {
    return {
      id: this.id,
      childId: this.childId,
      messages: this.messages,
      startTime: this.startTime,
      endTime: this.endTime,
      duration: this.getDuration(),
      durationMinutes: this.getDurationMinutes(),
      emotionalState: this.emotionalState,
      topics: this.topics,
      summary: this.summary,
      isActive: this.isActive,
      messageCount: this.getMessageCount(),
      isLong: this.isLongConversation(),
      hasEducationalContent: this.hasEducationalContent(),
      metadata: this.metadata
    };
  }
} 