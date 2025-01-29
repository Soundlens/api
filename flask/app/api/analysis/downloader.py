import os
import yt_dlp
from typing import Optional
import time
from random import uniform

class AudioDownloader:
    """Component for downloading audio tracks from YouTube"""
    
    def __init__(self, downloads_dir: str):
        """Initialize the downloader with download directory"""
        self.downloads_dir = downloads_dir
        self.max_retries = 3
        self.base_delay = 5  # Base delay in seconds
        
        # Get absolute path to cookies file
        cookies_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../uploads/cookies.txt'))
        
        if not os.path.exists(cookies_path):
            print(f"Warning: Cookies file not found at {cookies_path}", flush=True)
            cookies_path = None
        else:
            print(f"Using cookies file from: {cookies_path}", flush=True)
        
        # Configure yt-dlp options
        self.ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            'extract_audio': True,
            'audio_format': 'mp3',
            'outtmpl': {
                'default': os.path.join(downloads_dir, '%(title)s.%(ext)s')
            },
            'writethumbnail': False,
            'verbose': True,
            'cookiefile': cookies_path,
            'socket_timeout': 30,
            'retries': 10,
        }

    def get_or_download_track(self, track_name: str) -> Optional[str]:
        """Get existing audio file or download if it doesn't exist"""
        output_path = self._get_audio_file_path(track_name)
        print(f"Checking if file exists at {output_path}", flush=True)
        if os.path.exists(output_path):
            return output_path
            
        return self._download_youtube_track(track_name)

    def _get_audio_file_path(self, track_name: str) -> str:
        """Get the audio file path for a track name"""
        safe_filename = "".join(x for x in track_name if x.isalnum() or x in [' ', '-', '_'])
        return os.path.join(self.downloads_dir, f"{safe_filename}.mp3")

    def _download_youtube_track(self, track_name: str) -> Optional[str]:
        """Download a track from YouTube with retries and exponential backoff"""
        for attempt in range(self.max_retries):
            try:
                search_opts = {
                    **self.ydl_opts,
                    'default_search': 'ytsearch',
                    'quiet': False,
                    'no_warnings': False,
                    'ignoreerrors': True,
                }
                
                with yt_dlp.YoutubeDL(search_opts) as ydl:
                    print(f"Searching for track: {track_name} (Attempt {attempt + 1}/{self.max_retries})", flush=True)
                    result = ydl.extract_info(f"ytsearch1:{track_name}", download=False)
                    
                    if not result or 'entries' not in result or not result['entries']:
                        print(f"No results found for track: {track_name}")
                        return None
                    
                    video = result['entries'][0]
                    safe_filename = "".join(x for x in track_name if x.isalnum() or x in [' ', '-', '_'])
                    
                    download_opts = {
                        **self.ydl_opts,
                        'outtmpl': {
                            'default': os.path.join(self.downloads_dir, f"{safe_filename}.%(ext)s")
                        },
                        'quiet': False,
                        'no_warnings': False,
                    }
                    
                    print(f"Downloading from URL: {video['webpage_url']}", flush=True)
                    with yt_dlp.YoutubeDL(download_opts) as ydl_download:
                        ydl_download.download([video['webpage_url']])
                    
                    mp3_path = os.path.join(self.downloads_dir, f"{safe_filename}.mp3")
                    if os.path.exists(mp3_path):
                        print(f"Successfully downloaded to: {mp3_path}")
                        return mp3_path
                    
                    video_title = video.get('title', '').replace('/', '_')
                    safe_title = "".join(x for x in video_title if x.isalnum() or x in [' ', '-', '_'])
                    alt_path = os.path.join(self.downloads_dir, f"{safe_title}.mp3")
                    
                    if os.path.exists(alt_path):
                        print(f"Successfully downloaded to: {alt_path}")
                        return alt_path
                    
                    print(f"Download completed but file not found at expected paths:")
                    print(f"Tried: {mp3_path}")
                    print(f"Tried: {alt_path}")
                    return None
                    
            except Exception as e:
                if 'HTTP Error 429' in str(e) or 'Too Many Requests' in str(e):
                    if attempt < self.max_retries - 1:
                        delay = self.base_delay * (2 ** attempt) + uniform(0, 1)
                        print(f"Rate limited. Waiting {delay:.2f} seconds before retry...", flush=True)
                        time.sleep(delay)
                        continue
                print(f"Error downloading track: {str(e)}")
                return None
                
        print(f"Failed to download after {self.max_retries} attempts")
        return None 