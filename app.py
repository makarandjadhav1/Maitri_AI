import streamlit as st
from maitri_agent import get_agent_response
import os
from dotenv import load_dotenv
import uuid

# Load environment variables from .env file
load_dotenv()

# Check for API keys
if not os.getenv("GROQ_API_KEY"):
    st.error("Please set the GROQ_API_KEY environment variable in the .env file.")
if not os.getenv("OPENWEATHERMAP_API_KEY"):
    st.error("Please set the OPENWEATHERMAP_API_KEY environment variable in the .env file.")

# Set up the Streamlit page
st.set_page_config(page_title="Maitri AI", page_icon="🧘‍♀️")
st.title("Maitri AI: Your Well-being Assistant")

# Initialize chat history and session ID in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "assistant", "content": "Hello there! I'm Maitri, your friendly AI assistant. How can I assist you today? 🧘‍♀️"})

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Ask Maitri..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response from the agent
    with st.chat_message("assistant"):
        with st.spinner("Maitri is thinking..."):
            response = get_agent_response(prompt, st.session_state.session_id)
        st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})