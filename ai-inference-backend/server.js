const express = require('express');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
const bodyParser = require('body-parser');
const cors = require('cors'); // Import the cors package
const { exec } = require('child_process');

const app = express();
const port = 3001;

const token = fs.readFileSync(path.join(__dirname, '../../API-KEY.txt'), 'utf8').trim();
const createUrl = 'https://api.autocontentapi.com/Content/Create';
const statusBaseUrl = 'https://api.autocontentapi.com/content/status/';
const pollInterval = 5000; // Poll every 5 seconds
const cacheFile = 'audio_cache.json';
const podcastsDir = path.join(__dirname, '../podcasts');
const mp3Dir = path.join(__dirname, '../mp3');
const studyGuidesDir = path.join(__dirname, '../study_guides');

app.use(bodyParser.json({ limit: '10mb' })); // Increase payload size limit
app.use(cors()); // Use the cors middleware

// Serve static files from the podcasts directory
app.use('/podcasts', express.static(podcastsDir));
app.use('/mp3', express.static(mp3Dir)); // Serve static files from the mp3 directory

if (!fs.existsSync(mp3Dir)) {
  fs.mkdirSync(mp3Dir);
}

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
  if (!fs.existsSync(podcastsDir)) {
    fs.mkdirSync(podcastsDir);
  }
  const wavFilePath = path.join(podcastsDir, `${audioTitle}.wav`);
  const mp3FilePath = path.join(mp3Dir, `${audioTitle}.mp3`);
  const writer = fs.createWriteStream(wavFilePath);
  response.data.pipe(writer);
  return new Promise((resolve, reject) => {
    writer.on('finish', () => {
      console.log(`Audio downloaded and saved to: ${wavFilePath}`); // Log audio file path
      exec(`ffmpeg -i "${wavFilePath}" "${mp3FilePath}"`, (error, stdout, stderr) => {
        if (error) {
          console.error('Error converting file:', error);
          return reject(new Error('Error converting file'));
        }
        console.log(`Audio converted and saved to: ${mp3FilePath}`); // Log mp3 file path
        resolve(mp3FilePath);
      });
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
    const { status, audioUrl, audioTitle, filePath } = await pollStatus(request_id);

    const result = { request_id, status, audioUrl, audioTitle, filePath };
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

app.get('/podcasts', (req, res) => {
  fs.readdir(podcastsDir, (err, files) => {
    if (err) {
      console.error('Error reading podcasts directory:', err);
      return res.status(500).json({ error: 'Error reading podcasts directory' });
    }
    const podcasts = files.map(file => ({
      name: file,
      path: path.join(podcastsDir, file)
    }));
    res.json(podcasts);
  });
});

app.get('/study-guides', (req, res) => {
  fs.readdir(studyGuidesDir, (err, files) => {
    if (err) {
      console.error('Error reading study guides directory:', err);
      return res.status(500).json({ error: 'Error reading study guides directory' });
    }
    const studyGuides = files.map(file => ({
      name: file,
      path: path.join(studyGuidesDir, file)
    }));
    res.json(studyGuides);
  });
});

app.get('/study-guides/:name', (req, res) => {
  const { name } = req.params;
  const filePath = path.join(studyGuidesDir, name);

  fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
      console.error('Error reading study guide file:', err);
      return res.status(500).json({ error: 'Error reading study guide file' });
    }
    res.json({ name, content: data });
  });
});

app.post('/convert-to-mp3', (req, res) => {
  const { filePath } = req.body;
  if (!filePath) {
    return res.status(400).json({ error: 'No file path provided' });
  }

  const wavFilePath = path.join(podcastsDir, filePath);
  const mp3FilePath = path.join(mp3Dir, `${path.parse(filePath).name}.mp3`);

  exec(`ffmpeg -i "${wavFilePath}" "${mp3FilePath}"`, (error, stdout, stderr) => {
    if (error) {
      console.error('Error converting file:', error);
      return res.status(500).json({ error: 'Error converting file' });
    }

    res.json({ message: 'File converted successfully', mp3_file_path: mp3FilePath });
  });
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});