import streamlit as st
import os
import time
import pyperclip
import json
from datetime import datetime, timedelta
from langchain_community.document_loaders import YoutubeLoader
from langchain.chains.summarize import load_summarize_chain
from langchain_community.chat_models import ChatOpenAI
from langchain.text_splitter import TokenTextSplitter
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from streamlit_extras.buy_me_a_coffee import button
from langchain.schema import Document
from chuck_norris_jokes import get_random_joke
import requests
import logging

# Konfiguriere das Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize session state for language and used jokes
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = 'en'
if 'used_jokes' not in st.session_state:
    st.session_state.used_jokes = set()
if 'api_key' not in st.session_state:
    st.session_state.api_key = None

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

# API Key Handling
if not st.secrets["openai_api_key"]:
    openai_key_input = st.text_input("Enter Your OpenAI Key:", type="password")
    if openai_key_input:
        # Store the API key in session state
        st.session_state.api_key = openai_key_input
        st.success("API key stored in session!")
else:
    # Show option to change API key
    if st.button("Change API Key"):
        st.session_state.api_key = None
        st.rerun()
    
    # Use stored API key from session state or secrets
    st.session_state.api_key = st.session_state.api_key or st.secrets["openai_api_key"]
    st.success("Using stored API key")

st.write("")
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

if submit_button and video_url:
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

        # Load Transcript
        with st.spinner("Loading video transcript..."):
            try:
                logger.info(f"Attempting to load transcript for URL: {video_url}")
                loader = YoutubeLoader.from_youtube_url(
                    video_url,
                    language=["en", "en-US", "de", "de-DE", "es", "es-ES"]
                )
                transcript = loader.load()
                
                if not transcript:
                    logger.error("Could not load transcript. The video might not have captions available.")
                    st.error("Could not load transcript. The video might not have captions available.")
                    st.stop()
                    
            except Exception as e:
                logger.error(f"Error loading transcript: {str(e)}")
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
        if not st.session_state.api_key:
            st.error("Please provide an OpenAI API key")
            st.stop()
            
        llm = ChatOpenAI(
            openai_api_key=st.session_state.api_key,
            model="gpt-4o-mini",
            temperature=0.3
        )

        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        joke_placeholder = st.empty()
        
        # Summarize
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
            
            # First, split by newlines and clean up
            lines = [line.strip() for line in thread_part.split('\n') if line.strip()]
            
            for line in lines:
                # Check if this line starts a new tweet (either with a number or is the first tweet)
                if (line.startswith(('1/', '2/', '3/', '4/', '5/', '6/', '7/', '8/', '9/', '10/')) or 
                    (not current_tweet and not any(line.startswith(str(i)+'/') for i in range(1, 11)))):
                    # Save previous tweet if exists
                    if current_tweet:
                        tweets.append(current_tweet.strip())
                    current_tweet = line
                else:
                    # Continue with current tweet
                    current_tweet += " " + line
            
            # Add the last tweet if exists
            if current_tweet:
                tweets.append(current_tweet.strip())
            
            # Clean up tweets (remove numbering from the beginning)
            cleaned_tweets = []
            for tweet in tweets:
                # Remove numbering pattern like "1/5", "2/5", etc.
                if any(tweet.startswith(f"{i}/") for i in range(1, 11)):
                    tweet = ' '.join(tweet.split(' ')[1:])
                cleaned_tweets.append(tweet.strip())
            
            tweets = cleaned_tweets
            
        except Exception as e:
            # Fallback if the format is not as expected
            st.error(f"Error processing thread format: {str(e)}")
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
        for i, tweet in enumerate(tweets):
            # Calculate appropriate height based on tweet length
            # Assuming average of 50 characters per line and 20px per line
            num_lines = len(tweet) // 50 + 1
            height = max(68, min(200, num_lines * 20))  # Min 68px (Streamlit requirement), max 200px
            
            # Display tweet number and content
            if i == 0:
                st.markdown("**First Tweet:**")
            else:
                st.markdown(f"**Tweet {i+1}:**")
            
            st.text_area("", tweet, key=f"tweet_{i}", disabled=True, height=height)
            st.write("")  # Add spacing between tweets

        st.write("")
        st.divider()

        # Buy Me a Coffee button
        button(username="kguba", floating=False, width=221)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")