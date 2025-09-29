import streamlit as st
from maitri_agent import get_agent_response
import os
from dotenv import load_dotenv
import uuid
from audio_recorder_streamlit import audio_recorder

from faster_whisper import WhisperModel
from gtts import gTTS
import io
import base64

# --- Load Environment Variables ---
load_dotenv()

# Check for API keys
if not os.getenv("GROQ_API_KEY") or not os.getenv("OPENWEATHERMAP_API_KEY"):
    st.error("Please set the GROQ_API_KEY and OPENWEATHERMAP_API_KEY environment variables in the .env file.")
    st.stop()

# --- Page Configuration ---
st.set_page_config(page_title="Maitri AI", page_icon="👩‍🚀")
st.title("Maitri AI: Your Astronaut Assistant 👩‍🚀")
st.markdown("I can help with well-being tips, quick facts, jokes, and more. Ask me with your voice or type below!")

# --- State Management ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello, Astronaut! I'm Maitri. How can I assist you today?"}]
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# --- AI Models and Audio Functions ---

# Use st.cache_resource to load the STT model only once
@st.cache_resource
def load_stt_model():
    # Options: "tiny.en", "base.en", "small.en", "medium.en"
    # Larger models are more accurate but slower. "base.en" is a good balance.
    model = WhisperModel("base.en", device="cpu", compute_type="int8")
    return model

stt_model = load_stt_model()

def speech_to_text(audio_data):
    """Transcribes audio data using the Whisper model."""
    if not audio_data:
        return None
    # The audiorecorder returns a numpy array, which we convert to bytes
    audio_file = io.BytesIO(audio_data)
    segments, _ = stt_model.transcribe(audio_file, beam_size=5)
    transcribed_text = "".join(segment.text for segment in segments)
    return transcribed_text.strip()

def text_to_speech(text):
    """Converts text to speech using gTTS and returns audio bytes."""
    try:
        tts = gTTS(text=text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception as e:
        st.error(f"Error in text-to-speech conversion: {e}")
        return None

def autoplay_audio(audio_bytes: bytes):
    """Encodes audio bytes to base64 and embeds it in HTML for autoplay."""
    b64 = base64.b64encode(audio_bytes).decode()
    md = f"""
        <audio controls autoplay="true">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        Your browser does not support the audio element.
        </audio>
        """
    st.markdown(md, unsafe_allow_html=True)

# --- Chat Interface ---

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Main Interaction Logic ---
st.sidebar.header("Voice Input")
audio_bytes = audio_recorder("Start Recording", "Stop Recording")

# Combine voice and text input handling
prompt = st.chat_input("Or type your message here...")

# If there is a new voice recording, process it
if audio_bytes:
    with st.spinner("Transcribing your voice..."):
        prompt = speech_to_text(audio_bytes)
    if not prompt:
        st.warning("Could not understand the audio. Please try again.")

# If there's a prompt from either voice or text, run the agent
if prompt:
    # Add user message to state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get and display agent response
    with st.chat_message("assistant"):
        with st.spinner("Maitri is thinking..."):
            response_text = get_agent_response(prompt, st.session_state.session_id)
            
            # Generate and play audio response
            audio_response = text_to_speech(response_text)
            if audio_response:
                autoplay_audio(audio_response)

        # Display the text response
        st.markdown(response_text)
    
    # Add assistant response to state
    st.session_state.messages.append({"role": "assistant", "content": response_text})