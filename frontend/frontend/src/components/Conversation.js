import React, { useState, useRef, useEffect, memo, useCallback, useMemo } from 'react';
import styled, { keyframes, css } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { formatTime, formatDuration, generateUniqueId, EMOTION_COLORS } from '../utils';

// Animations
const fadeInUp = keyframes`
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const pulse = keyframes`
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
`;

const wave = keyframes`
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
`;

// Styled Components
const ConversationContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  background: ${props => props.theme.colors.background};
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  direction: ${props => props.theme.direction};
`;

const ConversationHeader = styled.div`
  padding: 20px;
  background: linear-gradient(135deg, ${props => props.theme.colors.primary}, ${props => props.theme.colors.secondary});
  color: white;
  text-align: center;
  position: relative;
  
  h3 {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 600;
  }
  
  .status-indicator {
    position: absolute;
    top: 20px;
    ${props => props.theme.direction === 'rtl' ? 'left' : 'right'}: 20px;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: ${props => props.isOnline ? '#4CAF50' : '#f44336'};
    animation: ${pulse} 2s infinite;
  }
`;

const MessagesContainer = styled.div`
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: ${props => props.theme.colors.gray[100]};
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: ${props => props.theme.colors.gray[400]};
    border-radius: 3px;
    
    &:hover {
      background: ${props => props.theme.colors.gray[500]};
    }
  }
`;

const MessageBubble = styled(motion.div)`
  display: flex;
  align-items: flex-start;
  gap: 12px;
  animation: ${fadeInUp} 0.3s ease-out;
  
  ${props => props.isChild && css`
    flex-direction: ${props.theme.direction === 'rtl' ? 'row' : 'row-reverse'};
    justify-content: flex-start;
  `}
`;

const Avatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  flex-shrink: 0;
  
  ${props => props.isChild ? css`
    background: linear-gradient(135deg, ${props.theme.colors.primary}, ${props.theme.colors.secondary});
    color: white;
  ` : css`
    background: linear-gradient(135deg, #FF6B6B, #4ECDC4);
    color: white;
  `}
`;

const MessageContent = styled.div`
  max-width: 70%;
  
  ${props => props.isChild && css`
    align-self: flex-end;
  `}
`;

const MessageText = styled.div`
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 0.95rem;
  line-height: 1.4;
  position: relative;
  
  ${props => props.isChild ? css`
    background: linear-gradient(135deg, ${props.theme.colors.primary}, ${props.theme.colors.secondary});
    color: white;
    margin-${props.theme.direction === 'rtl' ? 'right' : 'left'}: auto;
  ` : css`
    background: ${props.theme.colors.gray[100]};
    color: ${props.theme.colors.text};
    border: 1px solid ${props.theme.colors.gray[200]};
  `}
`;

const MessageMeta = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  font-size: 0.75rem;
  color: ${props => props.theme.colors.gray[500]};
  
  ${props => props.isChild && css`
    justify-content: flex-end;
  `}
`;

const AudioPlayer = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: ${props => props.theme.colors.gray[50]};
  border-radius: 12px;
  margin-top: 8px;
  
  .play-button {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    border: none;
    background: ${props => props.theme.colors.primary};
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
    
    &:hover {
      transform: scale(1.1);
      background: ${props => props.theme.colors.primaryDark};
    }
    
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      transform: none;
    }
  }
  
  .audio-info {
    flex: 1;
    
    .duration {
      font-size: 0.8rem;
      color: ${props => props.theme.colors.gray[600]};
    }
    
    .waveform {
      display: flex;
      align-items: center;
      gap: 2px;
      margin-top: 4px;
      
      .bar {
        width: 3px;
        background: ${props => props.theme.colors.primary};
        border-radius: 2px;
        animation: ${wave} 1s infinite;
        
        &:nth-child(odd) {
          animation-delay: 0.1s;
        }
        
        &:nth-child(even) {
          animation-delay: 0.2s;
        }
      }
    }
  }
`;

const EmotionIndicator = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  background: ${props => EMOTION_COLORS[props.emotion] || '#ccc'}20;
  color: ${props => EMOTION_COLORS[props.emotion] || '#666'};
  border: 1px solid ${props => EMOTION_COLORS[props.emotion] || '#ccc'}40;
`;

const TypingIndicator = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 0;
`;

const TypingDots = styled.div`
  display: flex;
  gap: 4px;
  
  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: ${props => props.theme.colors.gray[400]};
    animation: ${pulse} 1.4s infinite;
    
    &:nth-child(1) { animation-delay: 0s; }
    &:nth-child(2) { animation-delay: 0.2s; }
    &:nth-child(3) { animation-delay: 0.4s; }
  }
`;

const InputContainer = styled.div`
  padding: 20px;
  border-top: 1px solid ${props => props.theme.colors.gray[200]};
  background: ${props => props.theme.colors.gray[50]};
`;

const InputBox = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 24px;
  border: 2px solid ${props => props.theme.colors.gray[200]};
  
  &:focus-within {
    border-color: ${props => props.theme.colors.primary};
  }
  
  input {
    flex: 1;
    border: none;
    outline: none;
    font-size: 0.95rem;
    padding: 0;
    background: transparent;
    
    &::placeholder {
      color: ${props => props.theme.colors.gray[400]};
    }
  }
  
  .record-button {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    border: none;
    background: ${props => props.isRecording ? '#f44336' : props.theme.colors.primary};
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
    animation: ${props => props.isRecording ? pulse : 'none'} 1s infinite;
    
    &:hover {
      transform: scale(1.1);
    }
    
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      transform: none;
    }
  }
  
  .send-button {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: none;
    background: ${props => props.theme.colors.primary};
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
    
    &:hover:not(:disabled) {
      transform: scale(1.1);
      background: ${props => props.theme.colors.primaryDark};
    }
    
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      transform: none;
    }
  }
`;

// Components
const Message = memo(({ message, isChild, onPlayAudio }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  
  const handlePlayAudio = useCallback(async () => {
    if (message.audioUrl && onPlayAudio) {
      setIsPlaying(true);
      try {
        await onPlayAudio(message.audioUrl);
      } finally {
        setIsPlaying(false);
      }
    }
  }, [message.audioUrl, onPlayAudio]);

  return (
    <MessageBubble
      isChild={isChild}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Avatar isChild={isChild}>
        {isChild ? '👶' : '🧸'}
      </Avatar>
      
      <MessageContent isChild={isChild}>
        <MessageText isChild={isChild}>
          {message.text}
        </MessageText>
        
        {message.audioUrl && (
          <AudioPlayer>
            <button 
              className="play-button"
              onClick={handlePlayAudio}
              disabled={isPlaying}
            >
              {isPlaying ? '⏸️' : '▶️'}
            </button>
            <div className="audio-info">
              <div className="duration">
                {formatDuration(message.audioDuration || 0)}
              </div>
              {isPlaying && (
                <div className="waveform">
                  {[...Array(8)].map((_, i) => (
                    <div 
                      key={i} 
                      className="bar" 
                      style={{ height: `${Math.random() * 16 + 8}px` }}
                    />
                  ))}
                </div>
              )}
            </div>
          </AudioPlayer>
        )}
        
        <MessageMeta isChild={isChild}>
          <span>{formatTime(message.timestamp)}</span>
          {message.emotion && (
            <EmotionIndicator emotion={message.emotion}>
              <span>{getEmotionEmoji(message.emotion)}</span>
              <span>{getEmotionLabel(message.emotion)}</span>
            </EmotionIndicator>
          )}
          {message.delivered && <span>✓</span>}
          {message.read && <span>✓✓</span>}
        </MessageMeta>
      </MessageContent>
    </MessageBubble>
  );
});

const TypingIndicatorComponent = memo(() => (
  <TypingIndicator
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
  >
    <Avatar isChild={false}>🧸</Avatar>
    <TypingDots>
      <div className="dot" />
      <div className="dot" />
      <div className="dot" />
    </TypingDots>
  </TypingIndicator>
));

// Helper functions
const getEmotionEmoji = (emotion) => {
  const emojis = {
    happiness: '😊',
    sadness: '😢',
    anger: '😠',
    fear: '😨',
    surprise: '😲',
    neutral: '😐'
  };
  return emojis[emotion] || '😐';
};

const getEmotionLabel = (emotion) => {
  const labels = {
    happiness: 'سعيد',
    sadness: 'حزين',
    anger: 'غاضب',
    fear: 'خائف',
    surprise: 'متفاجئ',
    neutral: 'طبيعي'
  };
  return labels[emotion] || 'طبيعي';
};

// Main Component
const Conversation = ({
  messages = [],
  isTyping = false,
  isOnline = true,
  onSendMessage,
  onSendAudio,
  onPlayAudio,
  currentChildName = 'طفلي',
  isRecording = false,
  onStartRecording,
  onStopRecording,
  ...props
}) => {
  const [inputText, setInputText] = useState('');
  const [isInputFocused, setIsInputFocused] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Memoized message list
  const messageList = useMemo(() => {
    return messages.map(message => ({
      ...message,
      id: message.id || generateUniqueId()
    }));
  }, [messages]);

  // Event handlers
  const handleSendMessage = useCallback(() => {
    if (inputText.trim() && onSendMessage) {
      onSendMessage(inputText.trim());
      setInputText('');
    }
  }, [inputText, onSendMessage]);

  const handleKeyPress = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  }, [handleSendMessage]);

  const handleRecordToggle = useCallback(() => {
    if (isRecording) {
      onStopRecording?.();
    } else {
      onStartRecording?.();
    }
  }, [isRecording, onStartRecording, onStopRecording]);

  return (
    <ConversationContainer {...props}>
      <ConversationHeader isOnline={isOnline}>
        <h3>محادثة مع {currentChildName}</h3>
        <div className="status-indicator" />
      </ConversationHeader>

      <MessagesContainer>
        <AnimatePresence>
          {messageList.map((message) => (
            <Message
              key={message.id}
              message={message}
              isChild={message.sender === 'child'}
              onPlayAudio={onPlayAudio}
            />
          ))}
          
          {isTyping && (
            <TypingIndicatorComponent key="typing" />
          )}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </MessagesContainer>

      <InputContainer>
        <InputBox isInputFocused={isInputFocused}>
          <input
            ref={inputRef}
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            onFocus={() => setIsInputFocused(true)}
            onBlur={() => setIsInputFocused(false)}
            placeholder="اكتب رسالة..."
            disabled={isRecording}
          />
          
          <button
            className="record-button"
            onClick={handleRecordToggle}
            isRecording={isRecording}
            title={isRecording ? 'إيقاف التسجيل' : 'ابدأ التسجيل'}
          >
            {isRecording ? '⏹️' : '🎤'}
          </button>
          
          <button
            className="send-button"
            onClick={handleSendMessage}
            disabled={!inputText.trim() || isRecording}
            title="إرسال"
          >
            📤
          </button>
        </InputBox>
      </InputContainer>
    </ConversationContainer>
  );
};

Conversation.displayName = 'Conversation';

export default memo(Conversation); 