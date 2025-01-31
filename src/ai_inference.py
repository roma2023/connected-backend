import time
import requests
import os
import json

# Read the token from the ../API-KEY.txt file
with open('../../API-KEY.txt', 'r') as file:
    token = file.read().strip()

create_url = 'https://api.autocontentapi.com/Content/Create'
status_base_url = 'https://api.autocontentapi.com/content/status/'
poll_interval = 5  # Poll every 5 seconds
cache_file = 'audio_cache.json'

# The request data to create the content
request_data = {
    "resources": [
        { "content": "https://youtu.be/lz_gMkQr7YE?si=vmCTnuJeq1I-3nm8", "type": "youtube" },
        { "content": "https://youtu.be/OQi8FwPSu5o?si=5OaQDEPWlvF6fJC9", "type": "youtube" }
    ],
    # "text": "This is an educational radio podcast on High School Chemistry. The podcast is designed to help students understand the concepts of chemistry in a simple and easy-to-understand manner. The podcast should also engage students with different generated quiz questions in between the podcast to test their understanding of the concepts, pausing and giving listeners some time to think about and answer the question themselves.",
    # "text": "This is an educational radio podcast on High School Chemistry, designed to help students understand chemistry concepts in a simple and engaging manner. The podcast should feature a structured format that includes clear explanations of chemistry topics, relatable examples, and interactive elements to keep students engaged. A critical feature of the podcast is the inclusion of a quiz segment every 2 minutes. These quiz questions should be directly related to the most recent topic covered, testing students understanding in real-time. The podcast should pause for 20-30 seconds after each quiz question, allowing listeners time to think and answer before proceeding with the explanation. Ensure that the tone remains engaging and student-friendly, making complex topics accessible while maintaining a structured flow. The podcast should seamlessly integrate the quizzes within the discussion, reinforcing learning without disrupting the natural progression of the episode.",
    "text": "This High School Chemistry podcast simplifies complex concepts through clear explanations, relatable examples, and interactive elements. Every 2 minutes, a quiz segment tests recent topics, with a 20-30 second pause for student reflection. The tone should be engaging and student-friendly, ensuring seamless integration of quizzes to reinforce learning without disrupting the flow.",
    "outputType": "audio"
}

def load_cache():
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            return json.load(file)
    return {}

def save_cache(cache):
    with open(cache_file, 'w') as file:
        json.dump(cache, file, indent=4)

def create_content():
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'accept': 'text/plain'
    }
    response = requests.post(create_url, json=request_data, headers=headers)
    response.raise_for_status()
    return response.json()

def poll_status(request_id):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'accept': 'application/json'
    }
    url = f'{status_base_url}{request_id}'

    while True:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        status = data.get('status')
        error_message = data.get('error_message')
        audio_url = data.get('audio_url')
        audio_title = data.get('audio_title')

        if error_message:
            print('Error from status check:', error_message)
            return None

        if status == 100:
            print('Content creation complete!')
            print('Audio URL:', audio_url)
            print('Audio Title:', audio_title)
            file_path = download_audio(audio_url, audio_title)
            return file_path

        print(f'Current status: {status}. Waiting for 100...')
        time.sleep(poll_interval)

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

def main():
    cache = load_cache()
    query_key = json.dumps(request_data, sort_keys=True)
    
    if query_key in cache:
        print('Using cached result.')
        cached_result = cache[query_key]
        print('Audio URL:', cached_result['audio_url'])
        print('Audio Title:', cached_result['audio_title'])
        print('Audio Path:', cached_result['audio_path'])
        return

    try:
        create_response = create_content()
        request_id = create_response.get('request_id')
        error_message = create_response.get('error_message')

        if error_message or not request_id:
            print('Error from create request:', error_message)
            return

        print('Request initiated. Request ID:', request_id)
        file_path = poll_status(request_id)
                
        # Save the result to cache
        cache[query_key] = {
            'audio_url': create_response['audio_url'],
            'audio_title': create_response['audio_title'],
            'audio_path': file_path
        }
        save_cache(cache)

    except requests.HTTPError as http_err:
        print('HTTP error:', http_err)
    except Exception as err:
        print('Error:', err)

if __name__ == '__main__':
    main()