import webbrowser
from tkinter import messagebox
from PIL import Image, ImageTk
import tkinter as tk
from bs4 import BeautifulSoup as bs
import requests
import re
import io

def fetch_libgen_results(book_name):
    """Fetch top 10 results from Library Genesis."""
    print(f"Searching Library Genesis for: {book_name}")
    search_url = f'https://libgen.is/search.php?req={book_name}&lg_topic=libgen&open=0&view=simple&res=25&phrase=1&column=def'
    response = requests.get(search_url)
    response.raise_for_status()
    src = response.content
    soup = bs(src, 'lxml')

    books_list = soup.find_all('tr', {'valign': "top"})
    results = []
    for i, tr in enumerate(books_list[:10]):  # Limit to top 10 results
        try:
            title = tr.contents[4].find('a').text.strip()
            author = tr.contents[2].find('a').text.strip()
            year = tr.contents[6].text.strip()
            download_link = tr.contents[4].find('a')['href']
            results.append({
                'title': title,
                'author': author,
                'year': year,
                'download_link': download_link
            })
        except Exception as e:
            print(f"Skipping a book due to error: {e}")
    return results

def fetch_book_details(book_link):
    """Parse metadata and cover image URL from the book detail page."""
    try:
        link = f'https://libgen.is/{book_link}'
        print(f"Fetching book detail page: {link}")
        response = requests.get(link)
        response.raise_for_status()
        soup = bs(response.content, 'lxml')

        # Parse metadata
        metadata = {}
        metadata_fields = soup.find_all('td')  # Locate all table cells for metadata
        for i in range(0, len(metadata_fields) - 1, 2):
            key = metadata_fields[i].text.strip()
            value = metadata_fields[i + 1].text.strip()
            metadata[key] = value
        
        # Parse cover image URL
        img_tag = soup.find('img')
        cover_url = f"https://libgen.is/{img_tag['src']}" if img_tag and img_tag['src'] else None
        metadata['cover_url'] = cover_url

        return metadata
    except Exception as e:
        print(f"Error fetching book details: {e}")
        return None

def open_book_popup(book):
    """Open a popup window for the selected book."""
    def download_book():
        """Handle the GET button click to download the book."""
        try:
            print(f"Fetching download page for book link: {book['download_link']}")
            link = f'https://libgen.is/{book["download_link"]}'
            download_page = requests.get(link)
            download_page.raise_for_status()
            source = download_page.content
            down_soup = bs(source, 'lxml')
            
            # Locate download link on the page
            downloads_list = down_soup.find_all('td', {'width': "17%"})
            download_link = None
            for tr in downloads_list:
                a = tr.find('a', string=re.compile('Libgen.li'))
                if a is not None and a.text == 'Libgen.li':
                    download_link = a['href']
                    print(f"Download link found: {download_link}")
                    break
            
            if download_link:
                webbrowser.open(download_link)  # Open the download link in the browser
                messagebox.showinfo("Download Started", "The download link has been opened in your browser.")
            else:
                print("Download link not found on the download page.")
                messagebox.showerror("Error", "Could not find a valid download link for this book.")
        except Exception as e:
            messagebox.showerror("Download Error", f"An error occurred: {e}")
            print(f"Error: {e}")

    # Fetch detailed metadata
    metadata = fetch_book_details(book['download_link'])
    if not metadata:
        messagebox.showerror("Error", "Failed to fetch book details.")
        return

    # Create a new popup window
    popup = tk.Toplevel()
    popup.title("Book Details")
    popup.geometry("500x700")

    # Display the cover image
    if 'cover_url' in metadata and metadata['cover_url']:
        try:
            img_response = requests.get(metadata['cover_url'])
            img_response.raise_for_status()
            img_data = io.BytesIO(img_response.content)
            img = Image.open(img_data)
            img = img.resize((200, 300))  # Resize the image
            img_tk = ImageTk.PhotoImage(img)

            cover_label = tk.Label(popup, image=img_tk)
            cover_label.image = img_tk  # Keep a reference to avoid garbage collection
            cover_label.pack(pady=10)
        except Exception as e:
            print(f"Error loading cover image: {e}")

    # Display all metadata
    for key, value in metadata.items():
        if key == 'cover_url':
            continue  # Skip the cover URL as it's already displayed
        tk.Label(popup, text=f"{key}: {value}", font=("Arial", 10), wraplength=480, justify="left").pack(anchor="w", padx=10, pady=2)

    # Add "GET" button
    tk.Button(popup, text="GET", font=("Arial", 12), bg="green", fg="white", command=download_book).pack(pady=20)

def show_book_options(results):
    """Show a UI with book options."""
    def on_select(book):
        """Open popup for the selected book."""
        open_book_popup(book)

    # Create the main window
    root = tk.Tk()
    root.title("Library Genesis Book Selector")

    # Create a scrollable frame
    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(frame)
    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Display books
    for book in results:
        frame = tk.Frame(scrollable_frame, bd=1, relief=tk.SOLID, padx=5, pady=5)
        frame.pack(fill=tk.X, padx=5, pady=5)
        
        title_label = tk.Label(frame, text=f"Title: {book['title']}", font=("Arial", 12, "bold"), anchor="w")
        title_label.pack(fill=tk.X)
        
        author_label = tk.Label(frame, text=f"Author: {book['author']}", anchor="w")
        author_label.pack(fill=tk.X)
        
        year_label = tk.Label(frame, text=f"Year: {book['year']}", anchor="w")
        year_label.pack(fill=tk.X)

        # Open details button
        select_button = tk.Button(frame, text="Details", command=lambda b=book: on_select(b))
        select_button.pack(side=tk.RIGHT)

    root.mainloop()

if __name__ == "__main__":
    try:
        book_name = input('Enter a book name: ').lower().replace(' ', '+')
        results = fetch_libgen_results(book_name)
        if results:
            show_book_options(results)
        else:
            print("No results found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")