import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
import re
import io
import webbrowser
from bs4 import BeautifulSoup as bs
import certifi

# ------------------------------------------------------------
#                   DATA FETCHING FUNCTIONS
# ------------------------------------------------------------

def fetch_libgen_results(book_name):
    """
    Fetch top 10 results from Library Genesis based on the provided book_name.
    """
    print(f"Searching Library Genesis for: {book_name}")
    search_url = (
        f"https://libgen.is/search.php?"
        f"req={book_name}&lg_topic=libgen&open=0&view=simple&res=25&phrase=1&column=def"
    )
    response = requests.get(search_url, verify=certifi.where())
    response.raise_for_status()

    soup = bs(response.content, "lxml")
    
    # Each book entry is in a <tr valign="top"> block
    books_list = soup.find_all("tr", {"valign": "top"})
    results = []
    
    for tr in books_list[:10]:  # Limit to top 10 results
        try:
            # It's safer to get all <td> cells:
            cells = tr.find_all("td")
            if len(cells) < 5:
                continue  # skip if not enough columns

            # Typical columns in LibGen search result table:
            # 0 => #
            # 1 => Author(s)
            # 2 => Title
            # 3 => Publisher
            # 4 => Year
            # 5 => Pages
            # 6 => Language
            # 7 => Size
            # 8 => Extension
            # 9 => Mirrors
            #
            # The 'Title' cell usually has the link to the book detail page.
            author = cells[1].get_text(strip=True)
            title_cell = cells[2]
            title = title_cell.get_text(strip=True)
            year = cells[4].get_text(strip=True)  # Some older entries might be blank or malformed
            download_link = title_cell.find("a")["href"]

            results.append({
                "title": title,
                "author": author,
                "year": year,
                "download_link": download_link
            })
        except Exception as e:
            print(f"Skipping a book due to error: {e}")
    
    return results

def fetch_book_details(book_link):
    """
    Parse metadata and cover image URL from the book detail page.
    """
    try:
        url = f"https://libgen.is/{book_link}"
        print(f"Fetching book detail page: {url}")
        response = requests.get(url, verify=certifi.where())
        print("Response status:", response.status_code)
        print("Response:", response)
        response.raise_for_status()

        soup = bs(response.content, "lxml")

        # Parse metadata from <td> blocks in the info table
        metadata = {}
        # We look for table rows that might contain 'Author(s):', 'Title:', 'Publisher:', etc.
        table_rows = soup.find_all("tr")
        for row in table_rows:
            cells = row.find_all("td")
            if len(cells) == 2:
                raw_key = cells[0].get_text()
                raw_val = cells[1].get_text()
                print(f"Raw key: {raw_key}, Raw value: {raw_val}")  # Print raw data
                key = cells[0].get_text(strip=True)
                val = cells[1].get_text(strip=True)
                metadata[key] = val

        # Attempt to find cover image
        # Some pages have <img id="cover"> or just <img> with src in the same table
        # We'll do a more general approach: search for the first <img> that has a 'src'
        img_tag = soup.find("img", src=True)
        if img_tag:
            cover_src = img_tag["src"]
            # Some cover_src might be an absolute URL or relative
            if cover_src.startswith("http"):
                cover_url = cover_src
            else:
                cover_url = f"https://libgen.is/{cover_src}"
        else:
            cover_url = None

        metadata["cover_url"] = cover_url
        return metadata

    except Exception as e:
        print(f"Error fetching book details: {e}")
        return None

# ------------------------------------------------------------
#                    MAIN APPLICATION
# ------------------------------------------------------------

class LibraryGenesisApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Library Genesis Search")
        self.geometry("800x600")

        # Top Frame - search bar + button
        top_frame = tk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        label = tk.Label(top_frame, text="Enter Book Title:", font=("Arial", 12))
        label.pack(side=tk.LEFT, padx=(0, 10))

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(top_frame, textvariable=self.search_var, width=40, font=("Arial", 12))
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))

        search_button = tk.Button(top_frame, text="Search", command=self.search_books, font=("Arial", 12))
        search_button.pack(side=tk.LEFT)

        # Frame for results
        self.results_frame = tk.Frame(self)
        self.results_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas + Scrollbar for the results
        self.canvas = tk.Canvas(self.results_frame, bg="#fafafa")
        self.scrollbar = tk.Scrollbar(self.results_frame, orient=tk.VERTICAL, command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Layout the canvas and scrollbar
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # ------------------------------------------------------------
    #               SEARCH and DISPLAY RESULTS
    # ------------------------------------------------------------

    def search_books(self):
        """
        Trigger the search and display the results in the scrollable frame.
        """
        book_name = self.search_var.get().strip()
        if not book_name:
            messagebox.showwarning("No Input", "Please enter a book title to search.")
            return

        # Convert spaces to '+' for the search
        query = book_name.lower().replace(' ', '+')
        try:
            results = fetch_libgen_results(query)
            self.display_results(results)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while searching:\n{e}")

    def display_results(self, results):
        """
        Clear the previous results and display the new list of books in scrollable_frame.
        """
        # Clear previous content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not results:
            no_results_label = tk.Label(
                self.scrollable_frame, text="No Results Found.", font=("Arial", 14)
            )
            no_results_label.pack(pady=10)
            return

        # Display each result
        for book in results:
            book_frame = tk.Frame(self.scrollable_frame, bd=1, relief=tk.RIDGE, padx=5, pady=5)
            book_frame.pack(fill=tk.X, padx=10, pady=5)

            # Title
            title_label = tk.Label(
                book_frame,
                text=f"Title: {book['title']}",
                font=("Arial", 12, "bold"),
                anchor="w"
            )
            title_label.pack(fill=tk.X, pady=2)

            # Author
            author_label = tk.Label(
                book_frame,
                text=f"Author(s): {book['author']}",
                font=("Arial", 10),
                anchor="w"
            )
            author_label.pack(fill=tk.X, pady=2)

            # Year
            year_label = tk.Label(
                book_frame,
                text=f"Year: {book['year']}",
                font=("Arial", 10),
                anchor="w"
            )
            year_label.pack(fill=tk.X, pady=2)

            # Details Button
            detail_button = tk.Button(book_frame, text="Details", command=lambda b=book: self.open_book_popup(b))
            detail_button.pack(side=tk.RIGHT, padx=5)

    # ------------------------------------------------------------
    #            DETAILS POPUP  (WITH SCROLLING)
    # ------------------------------------------------------------

    def open_book_popup(self, book):
        """
        Open a popup window for the selected book, displaying metadata, cover, etc.
        """
        # Fetch detailed metadata
        metadata = fetch_book_details(book["download_link"])
        if not metadata:
            messagebox.showerror("Error", "Failed to fetch book details.")
            return

        # Popup window
        popup = tk.Toplevel(self)
        popup.title("Book Details")
        popup.geometry("550x700")

        # -- Make the popup scrollable --
        # Outer frame
        outer_frame = tk.Frame(popup)
        outer_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas & Scrollbar
        canvas = tk.Canvas(outer_frame)
        scrollbar = tk.Scrollbar(outer_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_popup_frame = tk.Frame(canvas)

        scrollable_popup_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_popup_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Display cover image if available
        if metadata.get("cover_url"):
            try:
                img_response = requests.get(metadata["cover_url"], timeout=10)
                img_response.raise_for_status()
                img_data = io.BytesIO(img_response.content)
                img = Image.open(img_data)
                # Resize the image for a nicer fit
                img.thumbnail((300, 400), Image.ANTIALIAS)
                img_tk = ImageTk.PhotoImage(img)

                cover_label = tk.Label(scrollable_popup_frame, image=img_tk)
                cover_label.image = img_tk  # Keep a reference to avoid GC
                cover_label.pack(pady=10)
            except Exception as e:
                print(f"Error loading cover image: {e}")

        # A frame to hold the metadata in a grid
        meta_frame = tk.Frame(scrollable_popup_frame)
        meta_frame.pack(fill=tk.X, padx=10, pady=10)

        # Show metadata in two columns: Key | Value
        # We'll skip the 'cover_url' key, as it's already handled
        row_idx = 0
        for key, value in metadata.items():
            if key == "cover_url":
                continue

            # Key label
            key_label = tk.Label(meta_frame, text=f"{key}:", font=("Arial", 10, "bold"), anchor="w")
            key_label.grid(row=row_idx, column=0, sticky="w", padx=(0, 10), pady=3)

            # Value label
            val_label = tk.Label(meta_frame, text=value, font=("Arial", 10), wraplength=450, justify="left")
            val_label.grid(row=row_idx, column=1, sticky="w", pady=3)

            row_idx += 1

        # Download Button
        download_button = tk.Button(
            scrollable_popup_frame,
            text="Download Book",
            font=("Arial", 12, "bold"),
            bg="green",
            fg="white",
            command=lambda: self.download_book(book["download_link"])
        )
        download_button.pack(pady=20)

    def download_book(self, download_link):
        """
        Handle the "Download Book" button click for the selected book:
        - Opens the actual download link in the default browser, if found.
        """
        try:
            print(f"Fetching download page for book link: {download_link}")
            link = f"https://libgen.is/{download_link}"
            download_page = requests.get(link, verify=certifi.where())
            download_page.raise_for_status()
            down_soup = bs(download_page.content, "lxml")

            # Locate a Libgen mirror link on the page - e.g. "Libgen.li"
            td_list = down_soup.find_all("td", width="17%")
            actual_download_link = None
            for td in td_list:
                a = td.find("a", string=re.compile(r"Libgen\.li"))
                if a and a.text.strip() == "Libgen.li":
                    actual_download_link = a["href"]
                    print(f"Download link found: {actual_download_link}")
                    break

            if actual_download_link:
                webbrowser.open(actual_download_link)
                messagebox.showinfo("Download Started", "The download link has been opened in your browser.")
            else:
                print("Download link not found on the download page.")
                messagebox.showerror("Error", "Could not find a valid download link for this book.")
        except Exception as e:
            messagebox.showerror("Download Error", f"An error occurred: {e}")
            print(f"Error: {e}")


# ------------------------------------------------------------
#               RUN THE APPLICATION
# ------------------------------------------------------------
if __name__ == "__main__":
    app = LibraryGenesisApp()
    app.mainloop()