import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image
from downloader import YouTubeDownloader
import webbrowser
import urllib.request

# Set appearance mode and default color theme
ctk.set_appearance_mode("Dark")  # Use Dark mode for better contrast with the colors
ctk.set_default_color_theme("blue")

# Define app colors
APP_ACCENT_COLOR = "#22AAFD"  # Main blue color
APP_HOVER_COLOR = "#1B88CC"   # Darker blue for hover
APP_TEXT_COLOR = {
    "dark": "#FFFFFF",        # White text in dark mode
    "light": "#000000"        # Black text in light mode
}

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("YouTube Downloader")
        self.geometry("900x600")
        self.minsize(900, 600)
        
        # Set icon if exists
        self.ensure_assets_exist()
        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "app_icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Could not set icon: {e}")
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header row
        self.grid_rowconfigure(1, weight=0)  # URL entry row
        self.grid_rowconfigure(2, weight=0)  # Buttons row
        self.grid_rowconfigure(3, weight=0)  # Quality options row
        self.grid_rowconfigure(4, weight=0)  # Progress bar row
        self.grid_rowconfigure(5, weight=1)  # Status row
        
        # Create UI elements
        self.create_widgets()
        
        # Initialize downloader
        self.downloader = YouTubeDownloader(self.update_progress, self.update_status)
        
        # Default download path
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads")

    def get_text_color(self):
        """Get the appropriate text color based on appearance mode"""
        mode = ctk.get_appearance_mode().lower()
        return APP_TEXT_COLOR.get(mode, APP_TEXT_COLOR["dark"])

    def ensure_assets_exist(self):
        """Download and create necessary assets if they don't exist"""
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        os.makedirs(assets_dir, exist_ok=True)
        
        # Dictionary of assets to download: filename, url
        assets = {
            "youtube_logo.png": "https://www.iconpacks.net/icons/2/free-youtube-logo-icon-2431-thumb.png",
            "download_icon.png": "https://www.iconpacks.net/icons/2/free-download-icon-3296-thumb.png",
            "search_icon.png": "https://www.iconpacks.net/icons/2/free-search-icon-3076-thumb.png",
            "folder_icon.png": "https://www.iconpacks.net/icons/2/free-folder-icon-1484-thumb.png",
            "app_icon.ico": "https://www.iconpacks.net/icons/2/free-youtube-logo-icon-2431-thumb.png"
        }
        
        for filename, url in assets.items():
            file_path = os.path.join(assets_dir, filename)
            if not os.path.exists(file_path):
                try:
                    urllib.request.urlretrieve(url, file_path)
                except Exception as e:
                    print(f"Failed to download asset {filename}: {e}")

    def create_widgets(self):
        # Load images
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        
        try:
            self.youtube_logo = ctk.CTkImage(
                light_image=Image.open(os.path.join(assets_dir, "youtube_logo.png")), 
                dark_image=Image.open(os.path.join(assets_dir, "youtube_logo.png")),
                size=(40, 40)
            )
            
            self.download_icon = ctk.CTkImage(
                light_image=Image.open(os.path.join(assets_dir, "download_icon.png")), 
                dark_image=Image.open(os.path.join(assets_dir, "download_icon.png")),
                size=(18, 18)
            )
            
            self.search_icon = ctk.CTkImage(
                light_image=Image.open(os.path.join(assets_dir, "search_icon.png")), 
                dark_image=Image.open(os.path.join(assets_dir, "search_icon.png")),
                size=(18, 18)
            )
            
            self.folder_icon = ctk.CTkImage(
                light_image=Image.open(os.path.join(assets_dir, "folder_icon.png")), 
                dark_image=Image.open(os.path.join(assets_dir, "folder_icon.png")),
                size=(18, 18)
            )
        except Exception as e:
            print(f"Failed to load images: {e}")
            self.youtube_logo = self.download_icon = self.search_icon = self.folder_icon = None
        
        # Header frame with logo
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        if self.youtube_logo:
            self.logo_label = ctk.CTkLabel(self.header_frame, image=self.youtube_logo, text="")
            self.logo_label.pack(side="left", padx=10)
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="YouTube Downloader", 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.get_text_color()
        )
        self.title_label.pack(side="left", padx=10)
        
        # Theme switcher
        self.appearance_mode_menu = ctk.CTkOptionMenu(
            self.header_frame, 
            values=["Light", "Dark", "Theme Default"],
            command=self.change_appearance_mode,
            fg_color=APP_ACCENT_COLOR,
            button_color=APP_HOVER_COLOR,
            button_hover_color=APP_HOVER_COLOR,
            text_color=self.get_text_color(),
            dropdown_text_color=self.get_text_color()
        )
        self.appearance_mode_menu.pack(side="right", padx=10)
        self.appearance_mode_menu.set("Theme Default")
        
        # URL Entry
        self.url_frame = ctk.CTkFrame(self)
        self.url_frame.grid(row=1, column=0, padx=20, pady=(10, 10), sticky="ew")
        self.url_frame.grid_columnconfigure(0, weight=0)
        self.url_frame.grid_columnconfigure(1, weight=1)
        
        self.url_label = ctk.CTkLabel(self.url_frame, text="YouTube URL:", text_color=self.get_text_color())
        self.url_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.url_entry = ctk.CTkEntry(
            self.url_frame, 
            placeholder_text="https://www.youtube.com/watch?v=...", 
            height=36, 
            text_color=self.get_text_color(),
            placeholder_text_color="#777777"
        )
        self.url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        # Buttons Frame
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.fetch_btn = ctk.CTkButton(
            self.button_frame, 
            text="Fetch Video Info", 
            command=self.fetch_video, 
            image=self.search_icon,
            height=40,
            fg_color=APP_ACCENT_COLOR,
            hover_color=APP_HOVER_COLOR,
            text_color="#FFFFFF"
        )
        self.fetch_btn.grid(row=0, column=0, padx=10, pady=10)
        
        self.browse_btn = ctk.CTkButton(
            self.button_frame, 
            text="Browse", 
            command=self.browse_location,
            image=self.folder_icon,
            height=40,
            fg_color=APP_ACCENT_COLOR,
            hover_color=APP_HOVER_COLOR,
            text_color="#FFFFFF"
        )
        self.browse_btn.grid(row=0, column=1, padx=10, pady=10)
        
        self.download_btn = ctk.CTkButton(
            self.button_frame, 
            text="Download", 
            command=self.download_video, 
            image=self.download_icon,
            height=40,
            fg_color=APP_ACCENT_COLOR,
            hover_color=APP_HOVER_COLOR,
            text_color="#FFFFFF"
        )
        self.download_btn.grid(row=0, column=2, padx=10, pady=10)
        
        # Quality Options Frame
        self.quality_frame = ctk.CTkFrame(self)
        self.quality_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        self.quality_frame.grid_columnconfigure(0, weight=0)
        self.quality_frame.grid_columnconfigure(1, weight=1)
        
        self.quality_label = ctk.CTkLabel(self.quality_frame, text="Quality:", text_color=self.get_text_color())
        self.quality_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.quality_var = ctk.StringVar(value="Highest")
        self.quality_option = ctk.CTkOptionMenu(
            self.quality_frame, 
            values=["Highest", "1080p", "720p", "480p", "360p", "Audio Only"],
            variable=self.quality_var,
            width=200,
            fg_color=APP_ACCENT_COLOR,
            button_color=APP_HOVER_COLOR,
            button_hover_color=APP_HOVER_COLOR,
            text_color="#FFFFFF",
            dropdown_text_color=self.get_text_color()
        )
        self.quality_option.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Progress Frame
        self.progress_frame = ctk.CTkFrame(self)
        self.progress_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        self.progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, progress_color=APP_ACCENT_COLOR, height=15)
        self.progress_bar.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        self.progress_bar.set(0)
        
        # Status Frame
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=5, column=0, padx=20, pady=(10, 20), sticky="nsew")
        self.status_frame.grid_columnconfigure(0, weight=1)
        self.status_frame.grid_rowconfigure(0, weight=1)
        
        self.status_text = ctk.CTkTextbox(self.status_frame, height=150, wrap="word", text_color=self.get_text_color())
        self.status_text.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        self.status_text.insert("1.0", "Welcome to YouTube Downloader!\nEnter a YouTube URL and click 'Fetch Video Info' to start.\n")
        self.status_text.configure(state="disabled")
        
        # Footer with GitHub link
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.grid(row=6, column=0, padx=20, pady=(0, 10), sticky="ew")
        
        self.github_link = ctk.CTkButton(
            self.footer_frame, 
            text="My GitHub", 
            command=lambda: webbrowser.open("https://github.com/xcyberspy"),
            fg_color="transparent",
            text_color=self.get_text_color(),
            hover=True,
            hover_color=APP_ACCENT_COLOR
        )
        self.github_link.pack(side="right", padx=10)

    def change_appearance_mode(self, new_appearance_mode):
        if new_appearance_mode == "Theme Default":
            new_appearance_mode = "Dark"
        ctk.set_appearance_mode(new_appearance_mode)
        self._update_widget_colors()

    def _update_widget_colors(self):
        """Update text colors for all widgets when appearance mode changes"""
        text_color = self.get_text_color()
        
        # Update all labels
        for widget_name in ['title_label', 'url_label', 'quality_label', 'github_link', 'status_text', 'url_entry']:
            if hasattr(self, widget_name):
                widget = getattr(self, widget_name)
                widget.configure(text_color=text_color)
                
        # Update dropdown text colors
        if hasattr(self, 'quality_option'):
            self.quality_option.configure(dropdown_text_color=text_color)
            self.appearance_mode_menu.configure(dropdown_text_color=text_color)

    def fetch_video(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
            
        self.update_status("Fetching video information...")
        self.fetch_btn.configure(state="disabled")
        
        # Run in a separate thread to avoid freezing the UI
        threading.Thread(target=self._fetch_video_thread, args=(url,), daemon=True).start()
    
    def _fetch_video_thread(self, url):
        try:
            video_info = self.downloader.get_video_info(url)
            if video_info:
                self.update_status(f"Video Title: {video_info['title']}\nChannel: {video_info['author']}\nLength: {video_info['length']} seconds")
                self.download_btn.configure(state="normal")
            else:
                self.update_status("Failed to fetch video information.")
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
        finally:
            self.fetch_btn.configure(state="normal")
    
    def browse_location(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_path = folder
            self.update_status(f"Download location: {folder}")
    
    def download_video(self):
        url = self.url_entry.get().strip()
        quality = self.quality_var.get()
        
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
            
        self.download_btn.configure(state="disabled")
        self.fetch_btn.configure(state="disabled")
        self.progress_bar.set(0)
        
        # Run in a separate thread to avoid freezing the UI
        threading.Thread(
            target=self._download_video_thread, 
            args=(url, quality, self.download_path), 
            daemon=True
        ).start()
    
    def _download_video_thread(self, url, quality, download_path):
        try:
            result = self.downloader.download_video(url, quality, download_path)
            if result:
                self.update_status(f"Download completed: {result}")
                # Show success message
                self.show_download_complete_message(result)
            else:
                self.update_status("Download failed.")
        except Exception as e:
            self.update_status(f"Error during download: {str(e)}")
        finally:
            self.download_btn.configure(state="normal")
            self.fetch_btn.configure(state="normal")
    
    def show_download_complete_message(self, filepath):
        # Create a custom message window
        msg_window = ctk.CTkToplevel(self)
        msg_window.title("Download Complete")
        msg_window.geometry("400x200")
        msg_window.resizable(False, False)
        msg_window.grab_set()  # Make window modal
        
        # Configure grid
        msg_window.grid_columnconfigure(0, weight=1)
        
        # Add message
        message_label = ctk.CTkLabel(
            msg_window, 
            text="Download Completed Successfully!", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.get_text_color()
        )
        message_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Add filepath
        path_label = ctk.CTkLabel(
            msg_window,
            text=f"File saved to:\n{filepath}",
            wraplength=360,
            text_color=self.get_text_color()
        )
        path_label.grid(row=1, column=0, padx=20, pady=10)
        
        # Add buttons
        button_frame = ctk.CTkFrame(msg_window, fg_color="transparent")
        button_frame.grid(row=2, column=0, padx=20, pady=(10, 20))
        
        open_folder_btn = ctk.CTkButton(
            button_frame,
            text="Open Folder",
            command=lambda: os.startfile(os.path.dirname(filepath)),
            fg_color=APP_ACCENT_COLOR,
            hover_color=APP_HOVER_COLOR,
            text_color="#FFFFFF"
        )
        open_folder_btn.pack(side="left", padx=10)
        
        ok_btn = ctk.CTkButton(
            button_frame,
            text="OK",
            command=msg_window.destroy,
            fg_color=APP_ACCENT_COLOR,
            hover_color=APP_HOVER_COLOR,
            text_color="#FFFFFF"
        )
        ok_btn.pack(side="left", padx=10)
    
    def update_progress(self, progress):
        self.progress_bar.set(progress)
    
    def update_status(self, message):
        self.status_text.configure(state="normal")
        self.status_text.insert("end", f"\n{message}")
        self.status_text.see("end")
        self.status_text.configure(state="disabled")

if __name__ == "__main__":
    app = App()
    app.mainloop()