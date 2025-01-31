import os 
import requests

def download_audio(audio_url, audio_title):
    response = requests.get(audio_url, stream=True)
    response.raise_for_status()
    
    # Ensure the podcasts directory exists
    os.makedirs('../podcasts', exist_ok=True)
    
    # Create the file path
    file_path = f'../podcasts/{audio_title}.wav'
    
    # Save the audio file
    with open(file_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    
    print(f'Audio downloaded successfully: {file_path}')
    
audio_url = "https://autocontentapi.blob.core.windows.net/audios/25164035-7eb2-4d16-bd4a-a1998a36f3c2_20250130202402.wav"
audio_title = "AI and Productivity"

download_audio(audio_url, audio_title)