import requests
import re
import webbrowser
import certifi
import subprocess
import json
import os
from bs4 import BeautifulSoup as bs

CACHE_FILE = 'libgen_cache.json'

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as file:
        json.dump(cache, file, indent=4)

def search_library_genesis(book_name):
    cache = load_cache()
    if book_name in cache:
        print(f"Found cached data for: {book_name}")
        return cache[book_name]

    try:
        print(f"Searching Library Genesis for: {book_name}")
        result = subprocess.run(['node', 'cheerio_script.js', book_name], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running Node.js script: {result.stderr}")
            return []

        book_metadata = json.loads(result.stdout)
        print(f"Found {len(book_metadata)} books in Library Genesis search results.")
        
        # Limit to the first 10 results
        book_metadata = book_metadata[1:2]
        
        for metadata in book_metadata:
            print("*" * 50)
            print("title: ", metadata['title'])
            print("author: ", metadata['author'])
            print("year: ", metadata['year'])
            print("publisher: ", metadata['publisher'])
            print("format: ", metadata['format'])
            print("size: ", metadata['size'])
            print("link: ", metadata['link'])
            print("*" * 50)
        
        cache[book_name] = book_metadata
        save_cache(cache)
        
        return book_metadata
    
    except Exception as e:
        print(f"Error fetching data from Library Genesis: {e}")
        return []

def get_download_book(book_metadata, open_browser=False):
    try:
        if not book_metadata:
            print("No book metadata provided. Cannot fetch download link.")
            return
        
        for book in book_metadata:
            print(f"Fetching download page for book link: {book['link']}")
            link = f'https://libgen.is/{book["link"]}'
            
            print(f"Fetching GET link from: {link}")
            result = subprocess.run(['node', 'cheerio_download.js', link], capture_output=True, text=True)
            print(f"Subprocess stdout: {result.stdout}")
            print(f"Subprocess stderr: {result.stderr}")
            print(f"Subprocess return code: {result.returncode}")
            if result.returncode != 0:
                print(f"Error running Node.js script: {result.stderr}")
                continue

            try:
                download_info = json.loads(result.stdout.strip())
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                print(f"Subprocess stdout: {result.stdout}")
                continue

            if 'error' in download_info:
                print(download_info['error'])
                continue

            final_download_link = f'https://libgen.li/{download_info["downloadLink"]}'
            print(f"Final download link found: {final_download_link}")
            book['download_link'] = final_download_link
            
            if open_browser:
                webbrowser.open(final_download_link)
            else:
                # Automatically download the book
                download_response = requests.get(final_download_link, stream=True)
                download_response.raise_for_status()
                
                # Extract filename from content-disposition header
                print("HERE")
                filename = book['title'] + '.pdf'
                print("filename: ", filename)
                file_path = f'../assets/{filename}'
                # Save the file
                with open(file_path, 'wb') as f:
                    for chunk in download_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Book downloaded successfully: {filename}")
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching download page: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    try:
        book_name = input('Enter a book name: ').lower().replace(' ', '+')
        print(f"Book name entered: {book_name}")
        
        book_metadata = search_library_genesis(book_name)
        # print("*" * 50)
        # print("Book metadata found:", book_metadata)
        # print("*" * 50)
        
        get_download_book(book_metadata, open_browser=False)
    
    except Exception as e:
        print(f"An unexpected error occurred in the main workflow: {e}")