const express = require('express');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const bodyParser = require('body-parser');
const cors = require('cors'); // Import the cors package
const { convert } = require('html-to-text'); // Import the html-to-text library

const app = express();
const port = 3001;

const token = fs.readFileSync(path.join(__dirname, '../../API-KEY.txt'), 'utf8').trim();
const createUrl = 'https://api.autocontentapi.com/Content/Create';
const statusBaseUrl = 'https://api.autocontentapi.com/content/status/';
const pollInterval = 5000; // Poll every 5 seconds
const cacheFile = 'audio_cache.json';

app.use(bodyParser.json({ limit: '10mb' })); // Increase payload size limit
app.use(cors()); // Use the cors middleware

const loadCache = () => {
  if (fs.existsSync(cacheFile)) {
    console.log('Loading cache from file'); // Log cache loading
    return JSON.parse(fs.readFileSync(cacheFile, 'utf8'));
  }
  return {};
};

const saveCache = (cache) => {
  console.log('Saving cache to file'); // Log cache saving
  fs.writeFileSync(cacheFile, JSON.stringify(cache, null, 4));
};

const createContent = async (requestData) => {
  try {
    console.log('Creating content with data:', requestData); // Log the request data
    const response = await axios.post(createUrl, requestData, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'accept': 'text/plain'
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error creating content:', error.response ? error.response.data : error.message);
    throw error;
  }
};


const pollStatus = async (requestId) => {
    const statusUrl = `${statusBaseUrl}${requestId}`;
  
    const response = await axios.get(statusUrl, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'accept': 'application/json'
      }
    });
    console.log('Response from status poll:', response.data); // Log the status poll response
    const { status, error_message, audio_url, audio_title, response_text } = response.data;
    console.log(`Current status: ${status}. Waiting for 100...`);
  
    if (error_message) {
      throw new Error(error_message);
    }


    if (status === 100) {
        if (response_text) {
          const studyGuidesDir = path.join(__dirname, '../study_guides');
          if (!fs.existsSync(studyGuidesDir)) {
            fs.mkdirSync(studyGuidesDir);
          }
          const filePath = path.join(studyGuidesDir, `${requestId}.txt`);
          const plainText = convert(response_text, {
            wordwrap: 130
          });
          fs.writeFileSync(filePath, plainText);
          return { status, filePath };
        }
        return { status, audioUrl: audio_url, audioTitle: audio_title };
      }
  
    return { status, audioUrl: audio_url, audioTitle: audio_title };
};


const downloadAudio = async (audioUrl, audioTitle) => {
  if (!audioUrl) {
    throw new Error('Invalid audio URL');
  }

  console.log(`Downloading audio from URL: ${audioUrl}`); // Log audio download URL
  const response = await axios.get(audioUrl, { responseType: 'stream' });
  const podcastsDir = path.join(__dirname, '../podcasts');
  if (!fs.existsSync(podcastsDir)) {
    fs.mkdirSync(podcastsDir);
  }
  const filePath = path.join(podcastsDir, `${audioTitle}.wav`);
  const writer = fs.createWriteStream(filePath);
  response.data.pipe(writer);
  return new Promise((resolve, reject) => {
    writer.on('finish', () => {
      console.log(`Audio downloaded and saved to: ${filePath}`); // Log audio file path
      resolve(filePath);
    });
    writer.on('error', (error) => {
      console.error('Error downloading audio:', error); // Log download error
      reject(error);
    });
  });
};

app.post('/create-content', async (req, res) => {
  console.log('Received request:', req.body); // Log the received request
  const requestData = req.body;
  console.log('Gonna cache:'); // Log the received request
  const cache = loadCache();
  const queryKey = JSON.stringify(requestData, Object.keys(requestData).sort());

  if (cache[queryKey]) {
    console.log('Using cached result.');
    return res.json(cache[queryKey]);
  }

  try {
    const { request_id, error_message } = await createContent(requestData);

    if (error_message || !request_id) {
      console.error('Error from create request:', error_message);
      return res.status(500).json({ error: error_message });
    }

    console.log('Request ID:', request_id); // Log the request ID
    const { status, audioUrl, audioTitle, responseText } = await pollStatus(request_id);

    const result = { request_id, status, audioUrl, audioTitle, responseText };
    cache[queryKey] = result;
    saveCache(cache);

    res.json(result);
  } catch (error) {
    console.error('Error processing request:', error); // Log any errors
    res.status(500).json({ error: error.message });
  }
});

app.get('/content/status/:requestId', async (req, res) => {
  const { requestId } = req.params;
  try {
    const statusData = await pollStatus(requestId);
    res.json(statusData);
  } catch (error) {
    console.error('Error fetching status:', error); // Log any errors
    res.status(500).json({ error: error.message });
  }
});

app.get('/download-audio/:requestId', async (req, res) => {
  const { requestId } = req.params;
  const { audioUrl, audioTitle } = req.query;

  try {
    const filePath = await downloadAudio(audioUrl, audioTitle);
    res.json({ filePath });
  } catch (error) {
    console.error('Error downloading audio:', error); // Log any errors
    res.status(500).json({ error: error.message });
  }
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});