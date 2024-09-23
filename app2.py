import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
import re

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
        # Fetch transcript in specified language
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

# Streamlit UI
st.title("YouTube Video Transcription Downloader")

# Input field for the YouTube video URL
youtube_url = st.text_input("Enter the YouTube video link:")
languages = st.multiselect("Select language(s) for transcript", ["en", "es", "fr", "de", "zh", "ja"], default=["en"])

# Options for choosing between transcript or captions
download_type = st.radio("Download Type", ('Transcript', 'Subtitles'))

# Button to download the transcription or subtitles
if st.button("Download"):
    if youtube_url:
        video_id = get_video_id(youtube_url)
        
        if video_id:
            if download_type == 'Transcript':
                transcript_text = fetch_transcript(video_id, languages)
                st.text_area("Transcript", transcript_text, height=300)
                
                if transcript_text and "Error" not in transcript_text:
                    # Button to download the transcript as a text file
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
                    # Button to download the subtitles as an SRT file
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
