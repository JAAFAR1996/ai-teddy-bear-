import React, { useState, useRef, useEffect, useCallback, memo } from 'react';
import styled, { keyframes, css } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { formatDuration, isAudioSupported, getMimeType } from '../utils';

// Animations
const pulse = keyframes`
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
`;

const wave = keyframes`
  0%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(0.5); }
`;

const ripple = keyframes`
  0% {
    transform: scale(0);
    opacity: 1;
  }
  100% {
    transform: scale(4);
    opacity: 0;
  }
`;

// Styled Components
const PlayerContainer = styled.div`
  display: flex;
  flex-direction: column;
  background: ${props => props.theme.colors.background};
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  border: 1px solid ${props => props.theme.colors.gray[200]};
  max-width: 400px;
  width: 100%;
  direction: ${props => props.theme.direction};
`;

const PlayerHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  
  h4 {
    margin: 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: ${props => props.theme.colors.text};
  }
  
  .status {
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 500;
    
    ${props => props.isPlaying && css`
      background: #4CAF5020;
      color: #4CAF50;
    `}
    
    ${props => props.isPaused && css`
      background: #FF980020;
      color: #FF9800;
    `}
    
    ${props => !props.isPlaying && !props.isPaused && css`
      background: ${props.theme.colors.gray[100]};
      color: ${props.theme.colors.gray[600]};
    `}
  }
`;

const ControlsContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
`;

const PlayButton = styled.button`
  position: relative;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, ${props => props.theme.colors.primary}, ${props => props.theme.colors.secondary});
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  
  &:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(0,0,0,0.2);
  }
  
  &:active {
    transform: scale(0.95);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
  
  .icon {
    font-size: 1.5rem;
    ${props => props.isLoading && css`
      animation: ${pulse} 1s infinite;
    `}
  }
  
  &::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background: ${props => props.theme.colors.primary};
    transform: translate(-50%, -50%);
    opacity: 0;
    animation: ${props => props.isPlaying ? ripple : 'none'} 2s infinite;
  }
`;

const ControlButton = styled.button`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: ${props => props.theme.colors.gray[100]};
  color: ${props => props.theme.colors.text};
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    background: ${props => props.theme.colors.gray[200]};
    transform: scale(1.05);
  }
  
  &:active {
    transform: scale(0.95);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
  }
`;

const TimeInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  
  .time-display {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.9rem;
    color: ${props => props.theme.colors.text};
    font-weight: 500;
  }
  
  .time-remaining {
    font-size: 0.8rem;
    color: ${props => props.theme.colors.gray[500]};
  }
`;

const ProgressContainer = styled.div`
  margin-bottom: 20px;
`;

const ProgressBar = styled.div`
  position: relative;
  width: 100%;
  height: 6px;
  background: ${props => props.theme.colors.gray[200]};
  border-radius: 3px;
  cursor: pointer;
  overflow: hidden;
  
  &:hover {
    height: 8px;
  }
`;

const ProgressFill = styled.div`
  height: 100%;
  background: linear-gradient(90deg, ${props => props.theme.colors.primary}, ${props => props.theme.colors.secondary});
  border-radius: 3px;
  transition: width 0.1s ease;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    right: 0;
    top: 50%;
    width: 12px;
    height: 12px;
    background: white;
    border-radius: 50%;
    transform: translateY(-50%);
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    opacity: 0;
    transition: opacity 0.2s ease;
  }
  
  ${ProgressBar}:hover &::after {
    opacity: 1;
  }
`;

const WaveformContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 2px;
  height: 40px;
  margin-bottom: 16px;
  padding: 8px;
  background: ${props => props.theme.colors.gray[50]};
  border-radius: 8px;
`;

const WaveformBar = styled.div`
  width: 3px;
  background: ${props => props.isActive ? 
    `linear-gradient(135deg, ${props.theme.colors.primary}, ${props.theme.colors.secondary})` : 
    props.theme.colors.gray[300]
  };
  border-radius: 2px;
  transition: all 0.2s ease;
  
  ${props => props.isPlaying && props.isActive && css`
    animation: ${wave} 0.8s infinite;
    animation-delay: ${props.delay}ms;
  `}
`;

const VolumeContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  
  .volume-icon {
    color: ${props => props.theme.colors.gray[600]};
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    transition: all 0.2s ease;
    
    &:hover {
      background: ${props => props.theme.colors.gray[100]};
    }
  }
`;

const VolumeSlider = styled.input`
  flex: 1;
  height: 4px;
  border-radius: 2px;
  background: ${props => props.theme.colors.gray[200]};
  outline: none;
  cursor: pointer;
  
  &::-webkit-slider-thumb {
    appearance: none;
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: ${props => props.theme.colors.primary};
    cursor: pointer;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  }
  
  &::-moz-range-thumb {
    width: 16px;
    height: 16px;
    border-radius: 50%;
    background: ${props => props.theme.colors.primary};
    cursor: pointer;
    border: none;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  }
`;

const ErrorMessage = styled(motion.div)`
  padding: 12px;
  background: #f4433620;
  color: #f44336;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 0.9rem;
  text-align: center;
`;

const LoadingSpinner = styled.div`
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid ${props => props.theme.colors.gray[300]};
  border-radius: 50%;
  border-top-color: ${props => props.theme.colors.primary};
  animation: ${pulse} 1s linear infinite;
`;

// Generate waveform data
const generateWaveform = (length = 40) => {
  return Array.from({ length }, () => Math.random() * 100 + 20);
};

// Main Component
const VoicePlayer = ({
  audioUrl,
  title = 'رد دبدوب الذكي',
  autoPlay = false,
  onPlay,
  onPause,
  onEnd,
  onError,
  showWaveform = true,
  showVolume = true,
  className,
  ...props
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [error, setError] = useState(null);
  const [waveformData] = useState(generateWaveform);
  
  const audioRef = useRef(null);
  const progressRef = useRef(null);

  // Initialize audio element
  useEffect(() => {
    if (!audioUrl) return;
    
    const audio = new Audio();
    audioRef.current = audio;
    
    // Audio event listeners
    const handleLoadStart = () => setIsLoading(true);
    const handleLoadedData = () => {
      setIsLoading(false);
      setDuration(audio.duration || 0);
      if (autoPlay) {
        handlePlay();
      }
    };
    const handleTimeUpdate = () => setCurrentTime(audio.currentTime || 0);
    const handlePlay = () => {
      setIsPlaying(true);
      setIsPaused(false);
      onPlay?.();
    };
    const handlePause = () => {
      setIsPlaying(false);
      setIsPaused(true);
      onPause?.();
    };
    const handleEnded = () => {
      setIsPlaying(false);
      setIsPaused(false);
      setCurrentTime(0);
      onEnd?.();
    };
    const handleError = (e) => {
      setIsLoading(false);
      setError('فشل في تحميل الملف الصوتي');
      onError?.(e);
    };

    audio.addEventListener('loadstart', handleLoadStart);
    audio.addEventListener('loadeddata', handleLoadedData);
    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('play', handlePlay);
    audio.addEventListener('pause', handlePause);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('error', handleError);
    
    // Check if audio format is supported
    const extension = audioUrl.split('.').pop();
    if (!isAudioSupported(extension)) {
      setError(`تنسيق الصوت ${extension} غير مدعوم`);
      return;
    }
    
    audio.src = audioUrl;
    audio.volume = volume;
    
    if (autoPlay) {
      audio.play();
    }
    
    return () => {
      audio.removeEventListener('loadstart', handleLoadStart);
      audio.removeEventListener('loadeddata', handleLoadedData);
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('play', handlePlay);
      audio.removeEventListener('pause', handlePause);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('error', handleError);
      audio.pause();
      audio.src = '';
    };
  }, [audioUrl, autoPlay, volume, onPlay, onPause, onEnd, onError]);

  // Handle play/pause
  const handlePlayPause = useCallback(() => {
    if (!audioRef.current || isLoading) return;
    
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play().catch(err => {
        setError('فشل في تشغيل الصوت');
        console.error('Audio play error:', err);
      });
    }
  }, [isPlaying, isLoading]);

  // Handle progress click
  const handleProgressClick = useCallback((e) => {
    if (!audioRef.current || !progressRef.current) return;
    
    const rect = progressRef.current.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    const newTime = percent * duration;
    
    audioRef.current.currentTime = newTime;
    setCurrentTime(newTime);
  }, [duration]);

  // Handle volume change
  const handleVolumeChange = useCallback((e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    setIsMuted(newVolume === 0);
    
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
  }, []);

  // Handle mute toggle
  const handleMuteToggle = useCallback(() => {
    if (audioRef.current) {
      if (isMuted) {
        audioRef.current.volume = volume;
        setIsMuted(false);
      } else {
        audioRef.current.volume = 0;
        setIsMuted(true);
      }
    }
  }, [isMuted, volume]);

  // Skip functions
  const handleSkipBack = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.currentTime = Math.max(0, currentTime - 10);
    }
  }, [currentTime]);

  const handleSkipForward = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.currentTime = Math.min(duration, currentTime + 10);
    }
  }, [currentTime, duration]);

  // Calculate progress percentage
  const progressPercent = duration > 0 ? (currentTime / duration) * 100 : 0;
  const remainingTime = duration - currentTime;

  // Get current waveform position
  const getCurrentWaveformIndex = () => {
    if (duration === 0) return 0;
    return Math.floor((currentTime / duration) * waveformData.length);
  };

  const currentWaveformIndex = getCurrentWaveformIndex();

  if (!audioUrl) {
    return null;
  }

  return (
    <PlayerContainer className={className} {...props}>
      <PlayerHeader isPlaying={isPlaying} isPaused={isPaused}>
        <h4>{title}</h4>
        <div className="status">
          {isLoading && <LoadingSpinner />}
          {!isLoading && isPlaying && 'يتم التشغيل'}
          {!isLoading && isPaused && 'متوقف'}
          {!isLoading && !isPlaying && !isPaused && 'جاهز'}
        </div>
      </PlayerHeader>

      <AnimatePresence>
        {error && (
          <ErrorMessage
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
          >
            {error}
          </ErrorMessage>
        )}
      </AnimatePresence>

      <ControlsContainer>
        <PlayButton
          onClick={handlePlayPause}
          disabled={isLoading || !!error}
          isPlaying={isPlaying}
          isLoading={isLoading}
        >
          <span className="icon">
            {isLoading ? '⏳' : isPlaying ? '⏸️' : '▶️'}
          </span>
        </PlayButton>

        <ControlButton onClick={handleSkipBack} disabled={isLoading || !!error}>
          ⏪
        </ControlButton>

        <TimeInfo>
          <div className="time-display">
            <span>{formatDuration(currentTime)}</span>
            <span>{formatDuration(duration)}</span>
          </div>
          {remainingTime > 0 && (
            <div className="time-remaining">
              -{formatDuration(remainingTime)} متبقي
            </div>
          )}
        </TimeInfo>

        <ControlButton onClick={handleSkipForward} disabled={isLoading || !!error}>
          ⏩
        </ControlButton>
      </ControlsContainer>

      <ProgressContainer>
        <ProgressBar ref={progressRef} onClick={handleProgressClick}>
          <ProgressFill style={{ width: `${progressPercent}%` }} />
        </ProgressBar>
      </ProgressContainer>

      {showWaveform && (
        <WaveformContainer>
          {waveformData.map((height, index) => (
            <WaveformBar
              key={index}
              style={{ height: `${height}%` }}
              isActive={index <= currentWaveformIndex}
              isPlaying={isPlaying}
              delay={index * 50}
            />
          ))}
        </WaveformContainer>
      )}

      {showVolume && (
        <VolumeContainer>
          <div className="volume-icon" onClick={handleMuteToggle}>
            {isMuted || volume === 0 ? '🔇' : volume < 0.5 ? '🔉' : '🔊'}
          </div>
          <VolumeSlider
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={isMuted ? 0 : volume}
            onChange={handleVolumeChange}
          />
        </VolumeContainer>
      )}
    </PlayerContainer>
  );
};

VoicePlayer.displayName = 'VoicePlayer';

export default memo(VoicePlayer); 