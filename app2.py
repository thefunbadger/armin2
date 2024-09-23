import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
import re
import os

# Function to get YouTube video ID from a link
def get_video_id(url):
    # Regex to extract video ID
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    if video_id_match:
        return video_id_match.group(1)
    return None

# Function to fetch transcript using YouTube Transcript API
def fetch_transcript(video_id, languages=['en']):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        transcript_text = "\n".join([entry['text'] for entry in transcript])
        return transcript_text
    except Exception as e:
        return f"Error: {e}"

# Function to download YouTube video as audio (mp3) using yt-dlp
def download_audio_yt_dlp(video_url, cookies_path=None):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloaded_audio.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
    }
    if cookies_path and os.path.exists(cookies_path):
        ydl_opts['cookiefile'] = cookies_path
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return "downloaded_audio.mp3"
    except yt_dlp.utils.DownloadError as e:
        return f"Error while downloading audio: {str(e).split(':', 1)[1].strip()}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

# Function to download YouTube video with selectable quality using yt-dlp
def download_video_yt_dlp(video_url, resolution, cookies_path=None):
    ydl_opts = {
        'format': f'bestvideo[height<={resolution}]+bestaudio/best',
        'outtmpl': f'downloaded_video_{resolution}p.%(ext)s',
        'merge_output_format': 'mp4',
        'quiet': True,
        'no_warnings': True,
    }
    if cookies_path and os.path.exists(cookies_path):
        ydl_opts['cookiefile'] = cookies_path
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return f"downloaded_video_{resolution}p.mp4", None
    except yt_dlp.utils.DownloadError as e:
        return None, f"Error while downloading video: {str(e).split(':', 1)[1].strip()}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

# Optional: Function to check video restrictions
def check_video_restriction(video_url, cookies_path=None):
    ydl_opts = {
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
    }
    if cookies_path and os.path.exists(cookies_path):
        ydl_opts['cookiefile'] = cookies_path
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            # Check for age restriction or other flags
            if info.get('age_limit', 0) > 0:
                return True, "This video is age-restricted."
            if info.get('is_live'):
                return True, "Live videos cannot be downloaded."
            return False, None
    except yt_dlp.utils.DownloadError as e:
        return True, f"Download error: {str(e).split(':', 1)[1].strip()}"
    except Exception as e:
        return True, f"Unexpected error: {str(e)}"

# Streamlit UI
st.title("YouTube Downloader and Transcription Tool")

# Input field for the YouTube video URL
youtube_url = st.text_input("Enter the YouTube video link:")

# Optional: Upload cookies file for authentication
st.sidebar.header("Optional: Provide YouTube Cookies")
cookies_file = st.sidebar.file_uploader("Upload your cookies.txt file", type=["txt"])

# Save uploaded cookies to a temporary file
cookies_path = None
if cookies_file:
    with open("cookies.txt", "wb") as f:
        f.write(cookies_file.getbuffer())
    cookies_path = "cookies.txt"

# Section 1: Download Transcript or Subtitles
st.subheader("1. Download Transcript")

languages = st.multiselect("Select language(s) for transcript", ["en", "es", "fr", "de", "zh", "ja"], default=["en"])
download_type = st.radio("Download Type", ('Transcript', 'Subtitles'))

if st.button("Download Transcript/Subtitles"):
    if youtube_url:
        video_id = get_video_id(youtube_url)
        if video_id:
            if download_type == 'Transcript':
                transcript_text = fetch_transcript(video_id, languages)
                if transcript_text.startswith("Error:"):
                    st.error(transcript_text)
                else:
                    st.text_area("Transcript", transcript_text, height=300)
                    st.download_button(
                        label="Download Transcript as TXT",
                        data=transcript_text,
                        file_name=f"{video_id}_transcript.txt",
                        mime="text/plain",
                    )
            else:
                st.warning("Subtitles downloading is not implemented in this version.")
        else:
            st.error("Invalid YouTube URL.")
    else:
        st.error("Please enter a YouTube URL.")

# Section 2: Download Audio as MP3
st.subheader("2. Download Audio (MP3)")

if st.button("Download MP3"):
    if youtube_url:
        # Optional: Check for video restrictions
        is_restricted, restriction_error = check_video_restriction(youtube_url, cookies_path)
        if is_restricted:
            st.error(restriction_error)
        else:
            audio_file = download_audio_yt_dlp(youtube_url, cookies_path)
            if os.path.exists(audio_file):
                with open(audio_file, "rb") as file:
                    st.download_button(
                        label="Download MP3",
                        data=file,
                        file_name=audio_file,
                        mime="audio/mpeg"
                    )
                # Clean up the downloaded file after download
                os.remove(audio_file)
            else:
                st.error(audio_file)  # Display error message if download fails
    else:
        st.error("Please enter a YouTube URL.")

# Section 3: Download Video with Selectable Quality
st.subheader("3. Download Video")

video_quality = st.selectbox("Select video quality", ['144p', '360p', '720p', '1080p'])

if st.button("Download Video"):
    if youtube_url:
        resolution = int(video_quality.replace('p', ''))
        # Optional: Check for video restrictions
        is_restricted, restriction_error = check_video_restriction(youtube_url, cookies_path)
        if is_restricted:
            st.error(restriction_error)
        else:
            video_file, error_message = download_video_yt_dlp(youtube_url, resolution, cookies_path)
            if video_file and os.path.exists(video_file):
                with open(video_file, "rb") as file:
                    st.download_button(
                        label="Download Video",
                        data=file,
                        file_name=video_file,
                        mime="video/mp4"
                    )
                # Clean up the downloaded file after download
                os.remove(video_file)
            else:
                st.error(error_message)
    else:
        st.error("Please enter a YouTube URL.")
