import os
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image, ImageTk

# For Pillow 10+:
# from PIL import Image
# Instead of Image.ANTIALIAS, use Image.Resampling.LANCZOS

# --------------------------------------------------------------------
# CONFIGURATION
# --------------------------------------------------------------------
# Use a currently working domain, e.g. https://libgen.rs
LIBGEN_DOMAIN = "https://libgen.rs"

SEARCH_URL = f"{LIBGEN_DOMAIN}/search.php"
BOOKS_DIR = os.path.join(os.path.expanduser("~"), "AlexandriaPy")  # local storage directory

# --------------------------------------------------------------------
# 1) Searching LibGen
# --------------------------------------------------------------------
def search_libgen(query, limit=50):
    """
    Searches LibGen for 'query' and returns up to 'limit' results (default=50).
    Returns a list of dictionaries like:
      [
        {
          'id': ..., 'title': ..., 'author': ..., 'year': ...,
          'extension': ..., 'size': ..., 'mirror1': ..., 'mirror2': ...
        }, ...
      ]
    """
    try:
        resp = requests.get(
            SEARCH_URL,
            params={"req": query, "res": limit},
            timeout=10
        )
        resp.raise_for_status()
    except requests.RequestException as e:
        print("[ERROR] Search failed:", e)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    tables = soup.find_all("table")
    if len(tables) < 3:
        return []

    # The 3rd table (index=2) typically contains search results
    result_table = tables[2]
    rows = result_table.find_all("tr")
    if not rows:
        return []

    books = []
    # Skip the header row (index 0)
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) < 11:
            continue

        # mirror1 => cols[9], mirror2 => cols[10]
        mirror1_tag = cols[9].find("a")
        mirror2_tag = cols[10].find("a")

        mirror1 = mirror1_tag["href"] if mirror1_tag else None
        mirror2 = mirror2_tag["href"] if mirror2_tag else None

        # Ensure full URL if missing scheme
        mirror1 = fix_url(mirror1)
        mirror2 = fix_url(mirror2)

        book = {
            "id":         cols[0].get_text(strip=True),
            "author":     cols[1].get_text(strip=True),
            "title":      cols[2].get_text(strip=True),
            "publisher":  cols[3].get_text(strip=True),
            "year":       cols[4].get_text(strip=True),
            "pages":      cols[5].get_text(strip=True),
            "language":   cols[6].get_text(strip=True),
            "size":       cols[7].get_text(strip=True),
            "extension":  cols[8].get_text(strip=True),
            "mirror1":    mirror1,
            "mirror2":    mirror2
        }
        books.append(book)

    return books


# --------------------------------------------------------------------
# 2) Fix URLs That Lack a Scheme
# --------------------------------------------------------------------
def fix_url(url):
    """
    If 'url' doesn't start with 'http', prepend LIBGEN_DOMAIN.
    Handles absolute or relative paths.
    """
    if not url:
        return None
    url = url.strip()
    if url.startswith("/"):
        return LIBGEN_DOMAIN + url
    if not url.startswith("http"):
        return LIBGEN_DOMAIN + "/" + url
    return url


# --------------------------------------------------------------------
# 3) Find the Final Download Link
# --------------------------------------------------------------------
def get_final_link(mirror_url):
    """
    Replicates logic from the Node code:
    1) GET the mirror page
    2) Look for an <a> containing 'Cloudflare' or possibly 'GET'
    3) Return that link as final
    """
    if not mirror_url:
        return None

    try:
        resp = requests.get(mirror_url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        print("[ERROR] Could not fetch mirror page:", e)
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Attempt 1: find <a> containing text 'Cloudflare'
    link_cloudflare = soup.find("a", string=lambda s: s and "Cloudflare" in s)
    if link_cloudflare and link_cloudflare.get("href"):
        return fix_url(link_cloudflare["href"])

    # Attempt 2: find <a> with text='GET'
    link_get = soup.find("a", string="GET")
    if link_get and link_get.get("href"):
        return fix_url(link_get["href"])

    return None


# --------------------------------------------------------------------
# 4) Download a File with Progress
# --------------------------------------------------------------------
def download_file(url, out_path, progress_callback=None):
    """
    Streams the file from 'url' to 'out_path'.
    'progress_callback(downloaded_bytes, total_bytes)' if provided.
    """
    try:
        with requests.get(url, stream=True, timeout=20) as r:
            r.raise_for_status()
            total_size = r.headers.get("Content-Length")
            total_size = int(total_size) if total_size else None

            downloaded = 0
            chunk_size = 8192

            with open(out_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, total_size)
    except Exception as e:
        print("[ERROR]", e)
        if progress_callback:
            progress_callback(-1, -1)  # indicates failure


# --------------------------------------------------------------------
# 5) Optional: Book Details & Cover
# --------------------------------------------------------------------
def get_book_cover_and_metadata(book):
    """
    Dummy function—In some code examples, we'd open a detail page,
    parse cover URL, etc. This script mostly uses the search table data.
    We'll show how you'd get a cover if we had a 'cover_url' field.
    """
    # For demonstration, we won't do a real 'details' fetch here,
    # but if you do, ensure you fix the domain for any cover URL.
    return None


# --------------------------------------------------------------------
# 6) The Tkinter Application
# --------------------------------------------------------------------
class LibgenApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LibGen Downloader (Python Demo)")
        self.geometry("800x600")

        # Top frame for the search bar
        top_frame = ttk.Frame(self)
        top_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(top_frame, text="Search Title/Keyword:").pack(side="left")

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(top_frame, textvariable=self.search_var, width=50)
        self.search_entry.pack(side="left", padx=5)

        self.search_button = ttk.Button(top_frame, text="Search", command=self.on_search_click)
        self.search_button.pack(side="left", padx=5)

        # Main frame for results listing
        self.results_frame = ttk.Frame(self)
        self.results_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Scrollable area
        self.canvas = tk.Canvas(self.results_frame, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.results_frame, orient="vertical", command=self.canvas.yview)
        self.results_inner = ttk.Frame(self.canvas)

        self.results_inner.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.results_inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Progress label & bar at bottom
        self.progress_label = ttk.Label(self, text="")
        self.progress_label.pack(side="bottom", pady=5)

        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=600, mode="determinate")
        self.progress_bar.pack(side="bottom", pady=5)

        # Ensure our local books directory exists
        if not os.path.exists(BOOKS_DIR):
            os.makedirs(BOOKS_DIR)

        self.current_download_thread = None

    # ----------------------------------------------------------------
    # Search
    # ----------------------------------------------------------------
    def on_search_click(self):
        query = self.search_var.get().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a search term.")
            return

        # Clear old results
        for widget in self.results_inner.winfo_children():
            widget.destroy()

        results = search_libgen(query, limit=50)
        if not results:
            ttk.Label(self.results_inner, text="No results found.").pack(pady=10)
            return

        # Show up to 10 results
        for i, book in enumerate(results[:10], start=1):
            row_frame = ttk.Frame(self.results_inner)
            row_frame.pack(fill="x", pady=5, padx=5)

            text_str = (
                f"{i}. {book['title']}\n"
                f"Author: {book['author']} | Year: {book['year']} | "
                f"Ext: {book['extension']} | Size: {book['size']}"
            )
            label = ttk.Label(row_frame, text=text_str, justify="left")
            label.pack(side="left", expand=True, fill="x")

            download_btn = ttk.Button(
                row_frame,
                text="Download",
                command=lambda b=book: self.start_download_flow(b)
            )
            download_btn.pack(side="right", padx=5)

    # ----------------------------------------------------------------
    # Download Flow
    # ----------------------------------------------------------------
    def start_download_flow(self, book):
        mirror = book.get("mirror1") or book.get("mirror2")
        if not mirror:
            messagebox.showerror("Error", "No mirror link found.")
            return

        def worker():
            # 1) final link
            final_url = get_final_link(mirror)
            if not final_url:
                self.update_progress_text("Could not find final link.")
                return

            # 2) Build local folder: "Title - Author"
            title_sanitized = "".join(c for c in book["title"] if c.isalnum() or c in " .-_")
            author_sanitized = "".join(c for c in book["author"] if c.isalnum() or c in " .-_")
            folder_name = f"{title_sanitized}"
            if author_sanitized:
                folder_name += f" - {author_sanitized}"

            book_dir = os.path.join(BOOKS_DIR, folder_name.strip())
            if not os.path.exists(book_dir):
                os.makedirs(book_dir)

            # 3) Name the file: "Title.extension"
            ext = book["extension"].lower() or "pdf"
            file_name = f"{title_sanitized}.{ext}"
            out_path = os.path.join(book_dir, file_name)

            # 4) Save metadata
            metadata_path = os.path.join(book_dir, "metadata.json")
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(book, f, indent=2)

            # 5) Download in chunks
            self.update_progress_text(f"Downloading {file_name} ...")
            self.set_progress_bar(0)

            def progress_callback(downloaded, total_size):
                if downloaded == -1:
                    # indicates error
                    self.update_progress_text("Download failed.")
                    self.set_progress_bar(0)
                    return
                if total_size and total_size > 0:
                    pct = int((downloaded / total_size) * 100)
                    self.set_progress_bar(pct)
                    self.update_progress_text(f"Downloading {file_name} ... {pct}%")
                else:
                    self.update_progress_text(f"Downloading {file_name} ... {downloaded} bytes")

            download_file(final_url, out_path, progress_callback=progress_callback)
            self.update_progress_text(f"Download complete: {file_name}")

        t = threading.Thread(target=worker, daemon=True)
        t.start()
        self.current_download_thread = t

    # ----------------------------------------------------------------
    # Progress Helpers
    # ----------------------------------------------------------------
    def update_progress_text(self, text):
        def _update():
            self.progress_label.config(text=text)
        self.after(0, _update)

    def set_progress_bar(self, value):
        def _update():
            self.progress_bar["value"] = value
        self.after(0, _update)


# --------------------------------------------------------------------
# RUN THE APP
# --------------------------------------------------------------------
if __name__ == "__main__":
    app = LibgenApp()
    app.mainloop()