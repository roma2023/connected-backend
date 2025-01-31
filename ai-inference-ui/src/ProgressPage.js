import React, { useEffect, useState, useRef } from 'react';
import { Container, Typography, LinearProgress, Box, Button, IconButton, Tooltip, Card, CardContent } from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';
import axios from 'axios';

const ProgressPage = ({ requestData, requestId }) => {
  const [status, setStatus] = useState(0);
  const [audioUrl, setAudioUrl] = useState('');
  const [audioTitle, setAudioTitle] = useState('');
  const [filePath, setFilePath] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const audioRef = useRef(null);

  useEffect(() => {
    console.log('ProgressPage mounted with requestId:', requestId); // Log the requestId
    const pollStatus = async () => {
      const statusUrl = `http://localhost:3001/content/status/${requestId}`;

      while (true) {
        try {
          const response = await axios.get(statusUrl);
          const data = response.data;
          setStatus(data.status);
          if (data.status === 100) {
            setAudioUrl(data.audioUrl);
            setAudioTitle(data.audioTitle);
            setFilePath(data.filePath);
            break;
          }
          if (data.error_message) {
            setErrorMessage(data.error_message);
            break;
          }
          console.log(`Current status: ${data.status}. Waiting for 100...`);
        } catch (error) {
          console.error('Error fetching status:', error);
          setErrorMessage(error.message);
        }
        await new Promise(resolve => setTimeout(resolve, 5000)); // Wait for 5 seconds before polling again
      }
    };

    pollStatus();

    return () => {}; // Cleanup function
  }, [requestId]);

  const handleDownload = async () => {
    try {
      const response = await axios.get(`http://localhost:3001/download-audio/${requestId}`, {
        params: { audioUrl, audioTitle }
      });
      const data = response.data;
      console.log('Audio file path:', data.filePath); // Log the file path
      // Optionally, you can trigger a download in the browser
      window.location.href = audioUrl;
      // Open the audio URL in a new tab
      window.open(audioUrl, '_blank');
    } catch (error) {
      console.error('Error downloading audio:', error);
      setErrorMessage(error.message);
    }
  };

  const handlePlayPauseAudio = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
      setDuration(audioRef.current.duration);
    }
  };

  const formatTime = (time) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 3 }}>
        <Typography variant="h4" gutterBottom>Thank you for your submission</Typography>
        <Typography variant="body1" gutterBottom>Your request is being processed.</Typography>
        <Card sx={{ mt: 3, backgroundColor: '#f5f5f5', border: '1px solid #ccc' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>Request Data</Typography>
            <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>
              {JSON.stringify(requestData, null, 2)}
            </Typography>
          </CardContent>
        </Card>
        <Box sx={{ mt: 3 }}>
          <LinearProgress variant="determinate" value={status} />
          <Typography variant="body2" sx={{ mt: 1 }}>Status: {status}%</Typography>
        </Box>
        {status === 100 && audioUrl && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6">Audio Title: {audioTitle}</Typography>
            <Button variant="contained" color="primary" onClick={handleDownload}>
              Download Audio
            </Button>
            <Box sx={{ mt: 2, display: 'flex', alignItems: 'center' }}>
              <audio ref={audioRef} src={audioUrl} onTimeUpdate={handleTimeUpdate} controls style={{ display: 'none' }} />
              <Tooltip title={isPlaying ? "Pause Audio" : "Play Audio"}>
                <IconButton color="primary" onClick={handlePlayPauseAudio}>
                  {isPlaying ? <PauseIcon /> : <PlayArrowIcon />}
                </IconButton>
              </Tooltip>
              <Typography variant="body1" sx={{ ml: 1 }}>{isPlaying ? "Pause Audio" : "Play Audio"}</Typography>
            </Box>
            <Box sx={{ mt: 1 }}>
              <Typography variant="body2">
                {formatTime(currentTime)} / {formatTime(duration)}
              </Typography>
            </Box>
          </Box>
        )}
        {status === 100 && !audioUrl && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6">Study Guide</Typography>
            <Button variant="contained" color="primary" href={filePath} download>
              Download Study Guide
            </Button>
          </Box>
        )}
        {errorMessage && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="body1" color="error">Error: {errorMessage}</Typography>
          </Box>
        )}
      </Box>
    </Container>
  );
};

export default ProgressPage;