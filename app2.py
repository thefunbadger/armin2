import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
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

# Function to download YouTube video subtitles if available
def download_captions(video_id, languages=['en']):
    try:
        yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')
        caption = yt.captions.get_by_language_code(languages[0])
        if caption:
            return caption.generate_srt_captions()
        else:
            return "No captions available for this video."
    except Exception as e:
        return f"Error: {e}"

# Function to download YouTube video as audio (mp3)
def download_audio(video_url):
    try:
        yt = YouTube(video_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        out_file = audio_stream.download(output_path=".")
        base, ext = os.path.splitext(out_file)
        new_file = base + ".mp3"
        os.rename(out_file, new_file)
        return new_file
    except Exception as e:
        return str(e)

# Function to download YouTube video with selectable quality
def download_video(video_url, resolution):
    try:
        yt = YouTube(video_url)
        # Filter streams based on the user's selected resolution
        video_stream = yt.streams.filter(res=resolution, progressive=True).first()
        if not video_stream:
            return None, f"No videos available at {resolution} resolution."
        out_file = video_stream.download(output_path=".")
        return out_file, None
    except Exception as e:
        return None, str(e)

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
                captions_text = download_captions(video_id, languages)
                st.text_area("Subtitles", captions_text, height=300)
                
                if captions_text and "Error" not in captions_text:
                    st.download_button(
                        label="Download Subtitles as SRT",
                        data=captions_text,
                        file_name=f"{video_id}_captions.srt",
                        mime="text/plain",
                    )
        else:
            st.error("Invalid YouTube URL.")
    else:
        st.error("Please enter a YouTube URL.")

# Section 2: Download Audio as MP3
st.subheader("2. Download Audio (MP3)")

if st.button("Download MP3"):
    if youtube_url:
        audio_file = download_audio(youtube_url)
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
        video_file, error_message = download_video(youtube_url, video_quality)
        if video_file:
            with open(video_file, "rb") as file:
                st.download_button(
                    label="Download Video",
                    data=file,
                    file_name=video_file,
                    mime="video/mp4"
                )
        else:
            st.error(error_message)
    else:
        st.error("Please enter a YouTube URL.")
