import os
import re
import yt_dlp

class YouTubeDownloader:
    def __init__(self, progress_callback=None, status_callback=None):
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.current_video = None
        self.video_info = None
        # Add trackers to prevent duplicate messages
        self.last_percent_reported = -1
        self.last_status_message = ""
        # Add cancellation flag
        self.is_cancelled = False
    
    def get_video_info(self, url):
        """Fetch video information from YouTube URL"""
        try:
            # Clean the URL to ensure it's properly formatted
            url = self._clean_url(url)
            
            # Configure yt-dlp options for fetching info
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'ignoreerrors': True,
                'no_playlist': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
            if not info:
                if self.status_callback:
                    self._safe_status_update("Could not retrieve video information. The video might be private or region-restricted.")
                return None
                
            self.video_info = info
            
            # Calculate duration in seconds
            duration_seconds = info.get('duration', 0)
            
            return {
                'title': info.get('title', 'Unknown Title'),
                'author': info.get('uploader', 'Unknown Author'),
                'length': duration_seconds,
                'thumbnail': info.get('thumbnail', ''),
                'views': info.get('view_count', 0)
            }
        except Exception as e:
            if self.status_callback:
                self._safe_status_update(f"Error fetching video info: {str(e)}")
            return None
    
    def _clean_url(self, url):
        """Clean and validate YouTube URL"""
        # Extract video ID using regex
        video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
        if video_id_match:
            video_id = video_id_match.group(1)
            # Return a clean URL with just the video ID
            return f'https://www.youtube.com/watch?v={video_id}'
        return url

    def _safe_status_update(self, message):
        """Update status without duplicating messages"""
        if message != self.last_status_message:
            self.last_status_message = message
            if self.status_callback:
                self.status_callback(message)
    
    def cancel_download(self):
        """Cancel the current download process"""
        self.is_cancelled = True
        self._safe_status_update("Download cancelled by user.")
    
    def download_video(self, url, quality, download_path):
        """Download the video with the specified quality"""
        try:
            # Reset tracking variables at the start of a new download
            self.last_percent_reported = -1
            self.last_status_message = ""
            self.is_cancelled = False
            
            # Clean the URL
            url = self._clean_url(url)
            
            # Create the download path if it doesn't exist
            os.makedirs(download_path, exist_ok=True)
            
            # Set up progress hook
            def progress_hook(d):
                # Check if download was cancelled
                if self.is_cancelled:
                    raise Exception("Download cancelled by user")
                    
                if d['status'] == 'downloading':
                    if 'total_bytes' in d and d['total_bytes'] > 0:
                        percent = d['downloaded_bytes'] / d['total_bytes']
                        if self.progress_callback:
                            self.progress_callback(percent)
                        
                        # Update status every 10% but prevent duplicates
                        percent_int = int(percent * 100)
                        if percent_int % 10 == 0 and percent_int > 0 and percent_int != self.last_percent_reported:
                            self.last_percent_reported = percent_int
                            self._safe_status_update(f"Downloaded {percent_int}%")
                    elif 'total_bytes_estimate' in d and d['total_bytes_estimate'] > 0:
                        percent = d['downloaded_bytes'] / d['total_bytes_estimate']
                        if self.progress_callback:
                            self.progress_callback(percent)
                
                elif d['status'] == 'finished':
                    self._safe_status_update("Download finished, now processing...")
                    if self.progress_callback:
                        self.progress_callback(1.0)
            
            # Configure yt-dlp options with more robust settings
            ydl_opts = {
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [progress_hook],
                'ignoreerrors': True,
                'no_playlist': True,
                'verbose': False,
                'quiet': True,
                'no_warnings': True,
                'retries': 10,  # Retry up to 10 times
                'fragment_retries': 10,
                'skip_unavailable_fragments': True,
                'geo_bypass': True,  # Try to bypass geo-restrictions
            }
            
            # Set format based on quality
            if quality == "Audio Only":
                ydl_opts.update({
                    'format': 'bestaudio',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            elif quality == "Highest":
                ydl_opts.update({
                    'format': 'bestvideo+bestaudio/best',
                })
            elif quality == "1080p":
                ydl_opts.update({
                    'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
                })
            elif quality == "720p":
                ydl_opts.update({
                    'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
                })
            elif quality == "480p":
                ydl_opts.update({
                    'format': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
                })
            elif quality == "360p":
                ydl_opts.update({
                    'format': 'bestvideo[height<=360]+bestaudio/best[height<=360]',
                })
            
            # Download the video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self._safe_status_update(f"Starting download with quality: {quality}")
                
                try:
                    info = ydl.extract_info(url, download=True)
                    
                    if not info:
                        raise Exception("Failed to extract video information")
                    
                    # Get the downloaded file path
                    if 'requested_downloads' in info and info['requested_downloads']:
                        filepath = info['requested_downloads'][0].get('filepath')
                        if filepath:
                            return filepath
                    
                    # Fallback to constructing the path
                    title = info.get('title', 'video')
                    ext = 'mp3' if quality == "Audio Only" else info.get('ext', 'mp4')
                    return os.path.join(download_path, f"{title}.{ext}")
                    
                except yt_dlp.utils.DownloadError as e:
                    if "Requested format is not available" in str(e):
                        self._safe_status_update("The requested quality is not available. Trying with best available format...")
                        
                        # Try again with 'best' format
                        return self._fallback_download(url, download_path)
                    else:
                        # Try fallback for other errors too
                        self._safe_status_update(f"Download error: {str(e)}. Trying fallback method...")
                        return self._fallback_download(url, download_path)
            
        except Exception as e:
            self._safe_status_update(f"Error during download: {str(e)}")
            self._safe_status_update("Attempting fallback download method...")
            
            # Try fallback download for any error
            try:
                return self._fallback_download(url, download_path)
            except Exception as fallback_error:
                self._safe_status_update(f"Fallback download failed: {str(fallback_error)}")
            
            return None
    
    def _fallback_download(self, url, download_path):
        """Fallback download with most basic settings"""
        try:
            # Check if already cancelled
            if self.is_cancelled:
                return None
                
            # Reset tracking variables
            self.last_percent_reported = -1
            
            # Set up progress hook
            def progress_hook(d):
                # Check if download was cancelled
                if self.is_cancelled:
                    raise Exception("Download cancelled by user")
                    
                if d['status'] == 'downloading':
                    if 'total_bytes' in d and d['total_bytes'] > 0:
                        percent = d['downloaded_bytes'] / d['total_bytes']
                        if self.progress_callback:
                            self.progress_callback(percent)
                            
                        # Only show progress updates at 10% intervals and avoid duplicates
                        percent_int = int(percent * 100)
                        if percent_int % 10 == 0 and percent_int > 0 and percent_int != self.last_percent_reported:
                            self.last_percent_reported = percent_int
                            self._safe_status_update(f"Downloaded {percent_int}%")
                    elif 'total_bytes_estimate' in d and d['total_bytes_estimate'] > 0:
                        percent = d['downloaded_bytes'] / d['total_bytes_estimate']
                        if self.progress_callback:
                            self.progress_callback(percent)
                
                elif d['status'] == 'finished':
                    self._safe_status_update("Download finished, now processing...")
                    if self.progress_callback:
                        self.progress_callback(1.0)
            
            # Use the most basic settings possible
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
                'progress_hooks': [progress_hook],
                'ignoreerrors': True,
                'no_playlist': True,
                'retries': 10,
                'geo_bypass': True,
            }
            
            self._safe_status_update("Attempting fallback download with basic settings...")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if not info:
                    self._safe_status_update("Fallback download failed: Could not extract video information")
                    return None
                
                # Get the downloaded file path
                if 'requested_downloads' in info and info['requested_downloads']:
                    filepath = info['requested_downloads'][0].get('filepath')
                    if filepath:
                        return filepath
                
                # Fallback to constructing the path
                title = info.get('title', 'video')
                ext = info.get('ext', 'mp4')
                return os.path.join(download_path, f"{title}.{ext}")
                
        except Exception as e:
            self._safe_status_update(f"Fallback download failed: {str(e)}")
            return None