import React, { useEffect, useState } from 'react';
import { Container, Typography, List, ListItem, ListItemText, Box, Dialog, DialogTitle, DialogContent } from '@mui/material';
import axios from 'axios';

const StudyGuidesPage = () => {
  const [studyGuides, setStudyGuides] = useState([]);
  const [selectedStudyGuide, setSelectedStudyGuide] = useState(null);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const fetchStudyGuides = async () => {
      try {
        const response = await axios.get('http://localhost:3001/study-guides');
        setStudyGuides(response.data);
      } catch (error) {
        console.error('Error fetching study guides:', error);
      }
    };

    fetchStudyGuides();
  }, []);

  const handleListItemClick = async (studyGuide) => {
    try {
      const response = await axios.get(`http://localhost:3001/study-guides/${studyGuide.name}`);
      setSelectedStudyGuide(response.data);
      setOpen(true);
    } catch (error) {
      console.error('Error fetching study guide content:', error);
    }
  };

  const handleClose = () => {
    setOpen(false);
    setSelectedStudyGuide(null);
  };

  return (
    <Container maxWidth="md">
      <Typography variant="h4" gutterBottom>Your Study Guides</Typography>
      <List>
        {studyGuides.map((studyGuide, index) => (
          <ListItem key={index} button onClick={() => handleListItemClick(studyGuide)}>
            <ListItemText primary={studyGuide.name} />
          </ListItem>
        ))}
      </List>
      <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
        <DialogTitle>{selectedStudyGuide?.name}</DialogTitle>
        <DialogContent dividers>
          <Box sx={{ whiteSpace: 'pre-wrap' }}>
            {selectedStudyGuide?.content}
          </Box>
        </DialogContent>
      </Dialog>
    </Container>
  );
};

export default StudyGuidesPage;