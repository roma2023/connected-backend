import React, { useEffect, useState, useRef } from 'react';
import { Container, Typography, List, ListItem, ListItemText, IconButton, Box } from '@mui/material';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import PauseIcon from '@mui/icons-material/Pause';
import axios from 'axios';

const PodcastsPage = () => {
  const [podcasts, setPodcasts] = useState([]);
  const [currentPodcast, setCurrentPodcast] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef(null);

  useEffect(() => {
    const fetchPodcasts = async () => {
      try {
        const response = await axios.get('http://localhost:3001/podcasts');
        setPodcasts(response.data);
      } catch (error) {
        console.error('Error fetching podcasts:', error);
      }
    };

    fetchPodcasts();
  }, []);

  const handlePlayPause = (podcast) => {
    if (currentPodcast && currentPodcast.path === podcast.path) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play().catch((error) => console.error("Audio play error:", error));
      }
      setIsPlaying(!isPlaying);
    } else {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.src = ""; // Reset src before assigning a new one
        audioRef.current.load();
      }
      setCurrentPodcast(podcast);
      setIsPlaying(true);
      setTimeout(() => {
        audioRef.current.src = `http://localhost:3001/podcasts/${podcast.name}`;
        audioRef.current.play().catch((error) => {
          console.error("Audio play error:", error);
          console.error("Audio source:", audioRef.current.src);
        });
      }, 0);
    }
  };

  return (
    <Container maxWidth="md">
      <Typography variant="h4" gutterBottom>Your Podcasts</Typography>
      <List>
        {podcasts.map((podcast, index) => (
          <ListItem key={index} component="li" button onClick={() => handlePlayPause(podcast)}>
            <ListItemText primary={podcast.name} />
            <IconButton edge="end" color="primary">
              {currentPodcast && currentPodcast.path === podcast.path && isPlaying ? <PauseIcon /> : <PlayArrowIcon />}
            </IconButton>
          </ListItem>
        ))}
      </List>
      {currentPodcast && (
        <Box sx={{ mt: 2 }}>
          <audio ref={audioRef} controls style={{ display: 'none' }} />
        </Box>
      )}
    </Container>
  );
};

export default PodcastsPage;