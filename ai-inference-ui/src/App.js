import React, { useState } from 'react';
import { CssBaseline, Box, Typography, Toolbar } from '@mui/material';
import RequestForm from './RequestForm';
import ProgressPage from './ProgressPage';
import SideNav from './SideNav';
import PodcastsPage from './PodcastsPage';
import BroadcasterPage from './BroadcasterPage'; // Import BroadcasterPage
import StudyGuidesPage from './StudyGuidesPage'; // Import StudyGuidesPage
import axios from 'axios';

const App = () => {
  const [submitted, setSubmitted] = useState(false);
  const [requestData, setRequestData] = useState(null);
  const [requestId, setRequestId] = useState(null);
  const [selectedPage, setSelectedPage] = useState('home');

  const handleFormSubmit = async (data) => {
    console.log('Form submitted with data:', data); // Log the form data
    try {
      const response = await axios.post('http://localhost:3001/create-content', data);
      console.log('Response from backend:', response.data); // Log the response from the backend
      setRequestData(data);
      setRequestId(response.data.request_id);
      setSubmitted(true);
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  const renderContent = () => {
    if (submitted && requestId) {
      return <ProgressPage requestData={requestData} requestId={requestId} />;
    }

    switch (selectedPage) {
      case 'home':
        return <Typography variant="h4">Welcome to AI Inference</Typography>;
      case 'generate':
        return <RequestForm onSubmit={handleFormSubmit} />;
      case 'podcasts':
        return <PodcastsPage />;
      case 'study_guides':
        return <StudyGuidesPage />; // Add StudyGuidesPage
      case 'broadcaster':
        return <BroadcasterPage />; // Add BroadcasterPage
      default:
        return <Typography variant="h4">Welcome to AI Inference</Typography>;
    }
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <SideNav onSelect={setSelectedPage} />
      <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />
        {renderContent()}
      </Box>
    </Box>
  );
};

export default App;