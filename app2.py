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
def download_audio_yt_dlp(video_url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloaded_audio.mp3',
        'cookies': 'cookies.txt',  # Add your cookies file here
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return "downloaded_audio.mp3"
    except Exception as e:
        return f"Error while downloading audio: {str(e)}"

# Function to download YouTube video with selectable quality using yt-dlp
def download_video_yt_dlp(video_url, resolution):
    ydl_opts = {
        'format': f'bestvideo[height<={resolution}]+bestaudio/best',
        'outtmpl': f'downloaded_video_{resolution}.mp4',
        'cookies': 'cookies.txt',  # Add your cookies file here
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        return f"downloaded_video_{resolution}.mp4", None
    except Exception as e:
        return None, f"Error while downloading video: {str(e)}"

# Streamlit UI
st.title("YouTube Downloader and Transcription Tool")

# Input field for the YouTube video URL
youtube_url = st.text_input("Enter the YouTube video link:")

# Section 1: Download Transcript or Subtitles
st.subheader("1. Download Transcript or Subtitles")

languages = st.multiselect("Select language(s) for transcript", ["en", "es", "fr", "de", "zh", "ja"], default=["en"])
download_type = st.radio("Download Type", ('Transcript', 'Subtitles'))

if st.button("Download Transcript/Subtitles"):
    if youtube_url:
        video_id = get_video_id(youtube_url)
        if video_id:
            if download_type == 'Transcript':
                transcript_text = fetch_transcript(video_id, languages)
                st.text_area("Transcript", transcript_text, height=300)
                
                if transcript_text and "Error" not in transcript_text:
                    st.download_button(
                        label="Download Transcript as TXT",
                        data=transcript_text,
                        file_name=f"{video_id}_transcript.txt",
                        mime="text/plain",
                    )
            else:
                st.error("Subtitles downloading is not yet supported.")
        else:
            st.error("Invalid YouTube URL.")
    else:
        st.error("Please enter a YouTube URL.")

# Section 2: Download Audio as MP3
st.subheader("2. Download Audio (MP3)")

if st.button("Download MP3"):
    if youtube_url:
        audio_file = download_audio_yt_dlp(youtube_url)
        if os.path.exists(audio_file):
            with open(audio_file, "rb") as file:
                st.download_button(
                    label="Download MP3",
                    data=file,
                    file_name=audio_file,
                    mime="audio/mpeg"
                )
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
        video_file, error_message = download_video_yt_dlp(youtube_url, resolution)
        if video_file:
            with open(video_file, "rb") as file:
                st.download_button(
                    label="Download Video",
                    data=file,
                    file_name=video_file,
                    mime="video/mp4"
                )
        else:
            st.error(f"Error downloading video: {error_message}")
    else:
        st.error("Please enter a YouTube URL.")
