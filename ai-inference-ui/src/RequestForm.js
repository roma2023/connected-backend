import React, { useState } from 'react';
import { TextField, Button, Select, MenuItem, FormControl, InputLabel, Checkbox, FormControlLabel, Typography, Box, Container } from '@mui/material';

const RequestForm = ({ onSubmit }) => {
  const [resources, setResources] = useState([{ content: '', type: 'text' }]);
  const [text, setText] = useState('');
  const [outputType, setOutputType] = useState('audio');
  const [includeCitations, setIncludeCitations] = useState(false);

  const handleResourceChange = (index, field, value) => {
    const newResources = [...resources];
    newResources[index][field] = value;
    setResources(newResources);
  };

  const addResource = () => {
    setResources([...resources, { content: '', type: 'text' }]);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const requestData = {
      resources,
      text,
      outputType,
      includeCitations: outputType === 'text' ? includeCitations : false,
    };
    onSubmit(requestData);
  };

  return (
    <Container maxWidth="sm">
      <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
        <Typography variant="h4" gutterBottom>AI Inference Request Form</Typography>
        {resources.map((resource, index) => (
          <Box key={index} sx={{ mb: 2 }}>
            <TextField
              fullWidth
              label="Resource Content"
              value={resource.content}
              onChange={(e) => handleResourceChange(index, 'content', e.target.value)}
              sx={{ mb: 2 }}
            />
            <FormControl fullWidth>
              <InputLabel>Resource Type</InputLabel>
              <Select
                value={resource.type}
                onChange={(e) => handleResourceChange(index, 'type', e.target.value)}
              >
                <MenuItem value="text">Text</MenuItem>
                <MenuItem value="youtube">YouTube</MenuItem>
                <MenuItem value="website">Website</MenuItem>
                <MenuItem value="pdf">PDF</MenuItem>
              </Select>
            </FormControl>
          </Box>
        ))}
        <Button variant="contained" onClick={addResource} sx={{ mb: 3 }}>Add Resource</Button>
        <TextField
          fullWidth
          label="Text"
          multiline
          rows={4}
          value={text}
          onChange={(e) => setText(e.target.value)}
          sx={{ mb: 3 }}
        />
        <FormControl fullWidth sx={{ mb: 3 }}>
          <InputLabel>Output Type</InputLabel>
          <Select
            value={outputType}
            onChange={(e) => setOutputType(e.target.value)}
          >
            <MenuItem value="audio">Audio</MenuItem>
            <MenuItem value="text">Text</MenuItem>
            <MenuItem value="faq">FAQ</MenuItem>
            <MenuItem value="study_guide">Study Guide</MenuItem>
            <MenuItem value="timeline">Timeline</MenuItem>
            <MenuItem value="briefing_doc">Briefing Document</MenuItem>
          </Select>
        </FormControl>
        {outputType === 'text' && (
          <FormControlLabel
            control={
              <Checkbox
                checked={includeCitations}
                onChange={(e) => setIncludeCitations(e.target.checked)}
              />
            }
            label="Include Citations"
            sx={{ mb: 3 }}
          />
        )}
        <Button type="submit" variant="contained" color="primary">Submit</Button>
      </Box>
    </Container>
  );
};

export default RequestForm;