import React, { useState, useEffect } from 'react';
import { Container, Typography, TextField, Button, MenuItem, Select, FormControl, InputLabel, Box, Alert } from '@mui/material';
import axios from 'axios';

const BroadcasterPage = () => {
  const [podcasts, setPodcasts] = useState([]);
  const [selectedPodcast, setSelectedPodcast] = useState('');
  const [section, setSection] = useState('');
  const [loopTime, setLoopTime] = useState('');
  const [numEvents, setNumEvents] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

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

  const handleBroadcast = async () => {
    try {
      const filePath = `http://localhost:3001/podcasts/${selectedPodcast.name}`;
      const fileName = selectedPodcast.name;

      const response = await axios.get(filePath, { responseType: 'blob' });
      const file = new File([response.data], fileName, { type: 'audio/mp3' });

      const formData = new FormData();
      formData.append('file', file);
      formData.append('filename', fileName);
      formData.append('section', section);
      formData.append('loopTime', loopTime);
      formData.append('numEvents', numEvents);

      const uploadResponse = await axios.post('http://localhost:8000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('Broadcast response:', uploadResponse.data);
      setSuccessMessage('Broadcast started successfully!');
    } catch (error) {
      console.error('Error broadcasting:', error);
      setSuccessMessage('Error broadcasting. Please try again.');
    }
  };

  return (
    <Container maxWidth="md">
      <Typography variant="h4" gutterBottom>Broadcaster</Typography>
      {successMessage && (
        <Alert severity={successMessage.includes('Error') ? 'error' : 'success'} sx={{ mb: 2 }}>
          {successMessage}
        </Alert>
      )}
      <FormControl fullWidth margin="normal">
        <InputLabel>Select Podcast</InputLabel>
        <Select
          value={selectedPodcast}
          onChange={(e) => setSelectedPodcast(e.target.value)}
        >
          {podcasts.map((podcast, index) => (
            <MenuItem key={index} value={podcast}>
              {podcast.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <FormControl fullWidth margin="normal">
        <InputLabel>Select Section</InputLabel>
        <Select
          value={section}
          onChange={(e) => setSection(e.target.value)}
        >
          <MenuItem value="English">English</MenuItem>
          <MenuItem value="Chemistry">Chemistry</MenuItem>
          <MenuItem value="Math">Math</MenuItem>
        </Select>
      </FormControl>
      <TextField
        label="Loop Iteration Time (seconds)"
        type="number"
        fullWidth
        margin="normal"
        value={loopTime}
        onChange={(e) => setLoopTime(e.target.value)}
      />
      <TextField
        label="Number of Events"
        type="number"
        fullWidth
        margin="normal"
        value={numEvents}
        onChange={(e) => setNumEvents(e.target.value)}
      />
      <Box sx={{ mt: 2 }}>
        <Button variant="contained" color="primary" onClick={handleBroadcast}>
          Start Broadcasting
        </Button>
      </Box>
    </Container>
  );
};

export default BroadcasterPage;