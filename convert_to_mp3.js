const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

const podcastsDir = path.join(__dirname, 'podcasts');
const mp3Dir = path.join(__dirname, 'mp3');

if (!fs.existsSync(mp3Dir)) {
  fs.mkdirSync(mp3Dir);
}

fs.readdir(podcastsDir, (err, files) => {
  if (err) {
    console.error('Error reading podcasts directory:', err);
    return;
  }

  files.forEach(file => {
    const filePath = path.join(podcastsDir, file);
    const mp3FilePath = path.join(mp3Dir, `${path.parse(file).name}.mp3`);

    exec(`ffmpeg -i "${filePath}" "${mp3FilePath}"`, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error converting file ${file}:`, error);
        return;
      }
      console.log(`Converted ${file} to ${mp3FilePath}`);
    });
  });
});