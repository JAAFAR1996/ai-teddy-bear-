/**
 * Conversation Management Use Cases
 * 
 * Contains all business use cases related to conversation management
 */

import { Conversation } from '../../domain/entities';

export class ConversationManagementUseCases {
  constructor({ conversationRepository, childRepository, eventBus, aiService }) {
    this.conversationRepository = conversationRepository;
    this.childRepository = childRepository;
    this.eventBus = eventBus;
    this.aiService = aiService;
  }

  async startConversation(childId) {
    try {
      // Validate child exists
      const child = await this.childRepository.findById(childId);
      if (!child) {
        throw new Error('Child not found');
      }

      // Check daily time limits
      const todayConversations = await this.getTodayConversations(childId);
      const totalTime = todayConversations.reduce((total, conv) => total + conv.getDurationMinutes(), 0);
      
      const childEntity = new Child(child);
      if (totalTime >= childEntity.getMaxDailyInteractionTime()) {
        throw new Error('Daily interaction time limit reached');
      }

      // Create new conversation
      const conversation = new Conversation({
        id: this.generateId(),
        childId,
        startTime: new Date(),
        metadata: {
          childAge: child.age,
          ageGroup: childEntity.getAgeGroup()
        }
      });

      // Save conversation
      const savedConversation = await this.conversationRepository.save(conversation);

      // Emit domain event
      await this.eventBus.emit('conversation.started', {
        conversationId: savedConversation.id,
        childId,
        startTime: savedConversation.startTime
      });

      return savedConversation;
    } catch (error) {
      throw new Error(`Failed to start conversation: ${error.message}`);
    }
  }

  async addMessage(conversationId, { content, sender, emotionalState, topics }) {
    try {
      const conversationData = await this.conversationRepository.findById(conversationId);
      
      if (!conversationData) {
        throw new Error('Conversation not found');
      }

      const conversation = new Conversation(conversationData);

      // Add message using domain logic
      const message = conversation.addMessage({
        content,
        sender,
        emotionalState,
        topics
      });

      // If this is a child message, generate AI response
      if (sender === 'child') {
        const aiResponse = await this.generateAIResponse(conversation, content);
        conversation.addMessage(aiResponse);
      }

      // Save updated conversation
      const savedConversation = await this.conversationRepository.save(conversation);

      // Emit domain event
      await this.eventBus.emit('message.added', {
        conversationId,
        messageId: message.id,
        sender,
        emotionalState: conversation.emotionalState
      });

      return savedConversation;
    } catch (error) {
      throw new Error(`Failed to add message: ${error.message}`);
    }
  }

  async endConversation(conversationId, summary = '') {
    try {
      const conversationData = await this.conversationRepository.findById(conversationId);
      
      if (!conversationData) {
        throw new Error('Conversation not found');
      }

      const conversation = new Conversation(conversationData);
      
      // End conversation using domain logic
      conversation.endConversation(summary);

      // Save updated conversation
      const savedConversation = await this.conversationRepository.save(conversation);

      // Emit domain event
      await this.eventBus.emit('conversation.ended', {
        conversationId,
        childId: conversation.childId,
        duration: conversation.getDurationMinutes(),
        messageCount: conversation.getMessageCount(),
        hasEducationalContent: conversation.hasEducationalContent()
      });

      return savedConversation;
    } catch (error) {
      throw new Error(`Failed to end conversation: ${error.message}`);
    }
  }

  async getConversationsByChild(childId, { limit = 20, offset = 0 } = {}) {
    try {
      const conversationsData = await this.conversationRepository.findByChildId(
        childId, 
        { limit, offset }
      );
      
      return conversationsData.map(data => new Conversation(data));
    } catch (error) {
      throw new Error(`Failed to get conversations: ${error.message}`);
    }
  }

  async getTodayConversations(childId) {
    try {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      const conversationsData = await this.conversationRepository.findByChildIdAndDate(
        childId, 
        today
      );
      
      return conversationsData.map(data => new Conversation(data));
    } catch (error) {
      throw new Error(`Failed to get today's conversations: ${error.message}`);
    }
  }

  async generateAIResponse(conversation, userMessage) {
    try {
      const response = await this.aiService.generateResponse({
        message: userMessage,
        conversationHistory: conversation.messages,
        childAge: conversation.metadata.childAge,
        emotionalState: conversation.emotionalState,
        topics: conversation.topics
      });

      return {
        content: response.text,
        sender: 'ai',
        emotionalState: response.emotionalState,
        topics: response.topics
      };
    } catch (error) {
      // Fallback response
      return {
        content: 'عذراً، لم أستطع فهم ما قلته. هل يمكنك إعادة المحاولة؟',
        sender: 'ai',
        emotionalState: 'neutral',
        topics: []
      };
    }
  }

  generateId() {
    return `conv_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
} 