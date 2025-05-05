import streamlit as st
import os
import time
import pyperclip
import json
from datetime import datetime, timedelta
from langchain_community.document_loaders import YoutubeLoader
from langchain.chains.summarize import load_summarize_chain
from langchain_openai import ChatOpenAI
from langchain.text_splitter import TokenTextSplitter
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from streamlit_extras.buy_me_a_coffee import button
from langchain.schema import Document
from chuck_norris_jokes import get_random_joke
import requests

# Initialize session state for language, used jokes, and request tracking
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = 'en'
if 'used_jokes' not in st.session_state:
    st.session_state.used_jokes = set()

# Constants for request limiting
REQUESTS_FILE = 'user_requests.json'
MAX_REQUESTS = 5

def load_user_requests():
    try:
        if os.path.exists(REQUESTS_FILE):
            with open(REQUESTS_FILE, 'r') as f:
                data = json.load(f)
                # Convert any old format data to new format
                for ip in data:
                    if isinstance(data[ip], dict):
                        data[ip] = 0
                return data
        return {}
    except Exception as e:
        st.error(f"Error loading request data: {str(e)}")
        return {}

def save_user_requests(requests_data):
    try:
        with open(REQUESTS_FILE, 'w') as f:
            json.dump(requests_data, f)
    except Exception as e:
        st.error(f"Error saving request data: {str(e)}")

def get_user_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        return response.json()['ip']
    except Exception as e:
        st.warning("Could not determine IP address. Using session ID instead.")
        return f"session_{st.session_state.get('_session_id', 'unknown')}"

def check_request_limit():
    user_ip = get_user_ip()
    requests_data = load_user_requests()
    
    if user_ip not in requests_data:
        requests_data[user_ip] = 0
        save_user_requests(requests_data)
    
    return int(requests_data[user_ip]) < MAX_REQUESTS

def increment_request_count():
    user_ip = get_user_ip()
    requests_data = load_user_requests()
    
    if user_ip not in requests_data:
        requests_data[user_ip] = 0
    
    requests_data[user_ip] = int(requests_data[user_ip]) + 1
    save_user_requests(requests_data)

def get_unique_joke():
    joke = get_random_joke()
    while joke in st.session_state.used_jokes:
        joke = get_random_joke()
    st.session_state.used_jokes.add(joke)
    return joke

# Lade Umgebungsvariablen
load_dotenv()

st.title("🧵 Anything To Thread")

# Füge Abstand hinzu
st.write("")
st.write("")

st.write("Ever wanted to create a thread from a YouTube video? Now you can!")
st.write("Simply enter your OpenAI key and the YouTube URL—then sit back and let the magic happen.")




# Füge Divider hinzu
st.divider()


# URL Eingabe
video_url = st.text_input("Enter YouTube Video URL:").strip()
st.write("")
openai_key_input = st.text_input("Enter Your OpenAI Key:", disabled=True, type="password")
st.write("")
st.write("")
st.write("")
st.warning("🚨 Up to 5 requests are free for demo purposes. For more, please clone the repo and use your own OpenAI API key.")
st.write("")
st.write("")

# Language selection buttons
col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
with col1:
    language_display = {
        'en': " EN",
        'de': " DE",
        'es': " ES"
    }.get(st.session_state.selected_language, "ENG")
    st.write(f"Thread language:{language_display}", unsafe_allow_html=True)
with col2:
    if st.button("🇺🇸", use_container_width=True):
        st.session_state.selected_language = 'en'
        st.rerun()
with col3:
    if st.button("🇩🇪", use_container_width=True):
        st.session_state.selected_language = 'de'
        st.rerun()
with col4:
    if st.button("🇪🇸", use_container_width=True):
        st.session_state.selected_language = 'es'
        st.rerun()
st.write("")
# Create container for button
button_container = st.container()

with button_container:
    submit_button = st.button("Submit")

# Füge Divider hinzu
st.divider()
st.write("")

#button(username="kguba", floating=False, width=221)

# Remove the request counter display
# total_remaining, hourly_remaining = get_remaining_requests()
# st.info(f"Remaining requests: {total_remaining} total, {hourly_remaining} in the next hour")

if submit_button and video_url:
    if not check_request_limit():
        st.error("You've reached your request limit.\nPlease clone the project and use your own OpenAI API key to continue.")
        st.stop()
        
    try:
        # Validate URL
        if not video_url.startswith(("https://www.youtube.com/", "https://youtu.be/")):
            st.error("Please enter a valid YouTube URL")
            st.stop()
            
        # Additional URL validation
        if len(video_url) > 100:  # Reasonable max length for YouTube URLs
            st.error("Invalid URL length")
            st.stop()
            
        # Check for common URL injection patterns
        if any(pattern in video_url.lower() for pattern in ['javascript:', 'data:', 'vbscript:', 'onload=']):
            st.error("Invalid URL format")
            st.stop()

        # Increment request count
        increment_request_count()

        # Load Transcript
        with st.spinner("Loading video transcript..."):
            try:
                loader = YoutubeLoader.from_youtube_url(
                    video_url,
                    language=["en", "en-US", "de", "de-DE", "es", "es-ES"]
                )
                transcript = loader.load()
                
                if not transcript:
                    st.error("Could not load transcript. The video might not have captions available.")
                    st.stop()
                    
            except Exception as e:
                st.error(f"Error loading transcript: {str(e)}")
                st.stop()

        # Split Transcript with smaller chunks
        with st.spinner("Splitting transcript into chunks..."):
            splitter = TokenTextSplitter(chunk_size=500, chunk_overlap=50)
            chunks = splitter.split_documents(transcript)
            total_chunks = len(chunks)

            if not chunks:
                st.error("Could not process the transcript. Please try a different video.")
                st.stop()

        # Set up LLM
        llm = ChatOpenAI(
            openai_api_key=openai_key_input or os.getenv("OPENAI_API_KEY"),
            model="gpt-4",
            temperature=0.3
        )

        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        joke_placeholder = st.empty()
        
        # Summarize
        # Erste Zusammenfassung
        summarize_chain = load_summarize_chain(llm=llm, chain_type="refine", verbose=True)
        
        # Process chunks with progress updates
        for i, chunk in enumerate(chunks):
            # Update progress
            progress = (i + 1) / total_chunks
            progress_bar.progress(progress)
            
            # Update status text and joke
            status_text.text(f"Processing chunk {i + 1} of {total_chunks}")
            joke_placeholder.write(get_unique_joke())
            
            # Process chunk
            if i == 0:
                summary = summarize_chain.run([chunk])
            else:
                # Create a new document with the previous summary
                summary_doc = Document(page_content=summary)
                summary = summarize_chain.run([chunk, summary_doc])

        # Thread-Erstellung mit dem System-Prompt
        system_prompt = """You are an expert at creating viral X (Twitter) threads that engage and inform your audience.
Your task is to create a compelling thread based on the summary of a YouTube video.

First, provide a concise summary of the video in 2-3 sentences. Then create the thread.

Thread Requirements:
1. Structure:
   - First tweet: Start with a powerful hook or thought-provoking question, end with "…🧵"
   - First tweet: Doesnt have a number in the beginning
   - Second tweet onwards: Number them (2/5), (3/5), etc.
   - Last tweet: Strong call-to-action and video URL: {url}

2. Content Guidelines:
   - Extract and explain the main arguments
   - Include specific examples and key points
   - Highlight unique perspectives and insights
   - Add 3-5 practical takeaways
   - Discuss broader context and implications
   - Make it comprehensive for those who haven't seen the video

3. Technical Rules:
   - Each tweet must be ≤280 characters
   - Maximum 2 emojis total (use only when they add value)
   - Vary sentence structure
   - Keep every tweet attention-grabbing
   - Avoid filler content

4. Style:
   - Use an engaging, conversational tone
   - Include specific examples and data points
   - Make complex ideas accessible
   - Create a narrative flow between tweets
   - Dont write "the person", "write the youtuber"

5. Language:
   - Create the thread in {language}

Format your response exactly like this:
SUMMARY:
[Your 2-3 sentence summary here]

THREAD:
[Your thread here]

Here is the summary of the video:
{summary}"""

        # Thread-Erstellung mit dem System-Prompt
        prompt = PromptTemplate(
            input_variables=["summary", "url", "language"],
            template=system_prompt
        )
        
        # Set language for output
        output_language = {
            'en': "English",
            'de': "German",
            'es': "Spanish"
        }.get(st.session_state.selected_language, "English")
        
        thread_prompt = prompt.format(
            summary=summary, 
            url=video_url,
            language=output_language
        )
        response = llm.predict(thread_prompt)

        # Split response into summary and thread
        try:
            summary_part = response.split("THREAD:")[0].replace("SUMMARY:", "").strip()
            thread_part = response.split("THREAD:")[1].strip()
            
            # Split thread into individual tweets
            tweets = []
            current_tweet = ""
            
            for line in thread_part.split('\n'):
                line = line.strip()
                if line:  # Skip empty lines
                    if line.startswith(('1/', '2/', '3/', '4/', '5/', '6/', '7/', '8/', '9/', '10/')):
                        if current_tweet:  # Save previous tweet if exists
                            tweets.append(current_tweet.strip())
                        current_tweet = line
                    else:
                        current_tweet += " " + line
            
            if current_tweet:  # Add the last tweet
                tweets.append(current_tweet.strip())
            
        except:
            # Fallback if the format is not as expected
            summary_part = summary
            tweets = [thread_part]

        # Now that we have the results, clear the progress indicators
        progress_bar.empty()
        status_text.empty()
        joke_placeholder.empty()

        # Display summary
        st.subheader("Summary")
        st.write(summary_part)
        st.divider()
        
        # Display each tweet
        st.subheader("Generated Thread")
        for i, tweet in enumerate(tweets, 1):
            st.write(f"Tweet {i}:")
            st.text_area("", tweet, key=f"tweet_{i}", disabled=True, height=120)

        st.write("")
        st.divider()

        # Buy Me a Coffee button
        button(username="kguba", floating=False, width=221)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
