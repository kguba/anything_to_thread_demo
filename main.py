import streamlit as st
import os
import time
import pyperclip
import json
from datetime import datetime, timedelta
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.chat_models import ChatOpenAI
from langchain.text_splitter import TokenTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from dotenv import load_dotenv
from streamlit_extras.buy_me_a_coffee import button
from langchain.schema import Document
from chuck_norris_jokes import get_random_joke
import requests

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
st.write("")
# Add warning message
st.warning("""
⚠️ **Demo Version Warning**

This is only for demo purposes. For further usage please use your own OpenAI API key.

Every user has up to 10 free anything-to-tweet submissions.
""")

# Füge Divider hinzu
st.divider()

# URL Eingabe
video_url = st.text_input("Enter YouTube Video URL:").strip()
st.write("")

# API Key Handling
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

# API Key Input
openai_key_input = st.text_input("Enter Your OpenAI Key:", type="password")
if openai_key_input:
    # Store the API key in session state
    st.session_state.api_key = openai_key_input
    st.success("API key stored in session!")

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

        # Check for API key
        if not st.session_state.api_key:
            st.error("Please provide an OpenAI API key")
            st.stop()

        # Load Transcript
        with st.spinner("Loading video transcript..."):
            st.info("Attempting to load transcript...")
            video_id = None
            try:
                # Extract video ID from URL
                st.info(f"Extracting video ID from URL: {video_url}")
                if "youtu.be" in video_url:
                    video_id = video_url.split("/")[-1].split("?")[0]
                elif "youtube.com" in video_url:
                    video_id = video_url.split("v=")[1].split("&")[0]
                else:
                    st.error("Invalid YouTube URL format")
                    st.info("Error: Invalid YouTube URL format during video_id extraction.")
                    st.stop()
                st.info(f"Extracted video ID: {video_id}")

                # Try to load transcript with multiple language attempts using YoutubeLoader
                transcript = None
                languages_to_try = ["en", "en-US", "de", "de-DE", "es", "es-ES"] # More explicit naming
                st.info(f"Attempting to load with YoutubeLoader for languages: {languages_to_try}")
                
                for lang_code in languages_to_try: # More explicit naming
                    st.info(f"YoutubeLoader: Trying language '{lang_code}'...")
                    try:
                        loader = YoutubeLoader.from_youtube_url(
                            video_url,
                            language=[lang_code], # YoutubeLoader expects a list
                            add_video_info=True
                        )
                        transcript_docs = loader.load() # More explicit naming
                        if transcript_docs and len(transcript_docs) > 0:
                            st.info(f"YoutubeLoader: Successfully loaded transcript in '{lang_code}'. Content preview: {transcript_docs[0].page_content[:100]}")
                            transcript = transcript_docs # Assign if successful
                            break 
                    except Exception as e_loader:
                        st.info(f"YoutubeLoader: Failed for language '{lang_code}'. Error: {str(e_loader)}")
                        continue # Continue to next language
                
                if not transcript or len(transcript) == 0:
                    st.info("YoutubeLoader failed for all languages or returned empty transcript.")
                    st.info("Attempting fallback with youtube_transcript_api...")
                    try:
                        from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
                        
                        st.info(f"youtube_transcript_api: Fetching list of available transcripts for video ID: {video_id}")
                        transcript_list_api = YouTubeTranscriptApi.list_transcripts(video_id) # More explicit naming
                        st.info(f"youtube_transcript_api: Available transcripts: {[t.language for t in transcript_list_api]}")

                        fetched_transcript_data = None # More explicit naming
                        # Try to find and fetch in preferred order
                        for lang_code_api in languages_to_try:
                             st.info(f"youtube_transcript_api: Trying to find and fetch transcript for language '{lang_code_api}'...")
                             try:
                                 target_transcript = transcript_list_api.find_transcript([lang_code_api]) # find_transcript expects a list
                                 st.info(f"youtube_transcript_api: Found transcript for '{target_transcript.language}', fetching...")
                                 fetched_transcript_data = target_transcript.fetch()
                                 if fetched_transcript_data:
                                     st.info(f"youtube_transcript_api: Successfully fetched transcript in '{target_transcript.language}'.")
                                     break
                             except NoTranscriptFound:
                                 st.info(f"youtube_transcript_api: No transcript found for '{lang_code_api}'.")
                                 continue
                        
                        if fetched_transcript_data:
                            st.info(f"youtube_transcript_api: Converting fetched data to Document format. Preview: {str(fetched_transcript_data)[:200]}")
                            # Convert to Document format
                            transcript = [Document(page_content=t_item['text']) for t_item in fetched_transcript_data] # More explicit naming
                            if not transcript:
                                st.info("youtube_transcript_api: Conversion to Document format resulted in empty list.")
                        else:
                            st.info("youtube_transcript_api: Failed to fetch transcript in any of the preferred languages.")
                            # If specific languages failed, try to fetch any available generated transcript as a last resort
                            st.info("youtube_transcript_api: Attempting to fetch any available generated transcript as a last resort...")
                            try:
                                for available_transcript_obj in transcript_list_api:
                                    if available_transcript_obj.is_generated:
                                        st.info(f"youtube_transcript_api: Found generated transcript in '{available_transcript_obj.language}', fetching...")
                                        fetched_transcript_data = available_transcript_obj.fetch()
                                        if fetched_transcript_data:
                                            st.info(f"youtube_transcript_api: Successfully fetched generated transcript in '{available_transcript_obj.language}'.")
                                            transcript = [Document(page_content=t_item['text']) for t_item in fetched_transcript_data]
                                            break
                                if not transcript:
                                     st.info("youtube_transcript_api: No generated transcripts could be fetched.")
                            except Exception as e_generated_fallback:
                                st.info(f"youtube_transcript_api: Error during generated transcript fallback: {str(e_generated_fallback)}")


                    except TranscriptsDisabled:
                        st.error(f"Could not load transcript for video {video_url}. Subtitles are disabled for this video.")
                        st.info(f"youtube_transcript_api: TranscriptsDisabled error for video ID {video_id}.")
                        st.stop()
                    except NoTranscriptFound:
                        st.error(f"Could not load transcript for video {video_url}. No transcript found in the available languages.")
                        st.info(f"youtube_transcript_api: NoTranscriptFound error for video ID {video_id} in languages {languages_to_try}.")
                        st.stop()
                    except Exception as e_api_fallback:
                        st.error(f"Could not load transcript using youtube_transcript_api. Error: {str(e_api_fallback)}")
                        st.info(f"youtube_transcript_api: General error for video ID {video_id}. Error: {str(e_api_fallback)}")
                        st.stop()

                if not transcript or len(transcript) == 0:
                    st.error(f"Failed to load transcript for video {video_url} after all attempts.")
                    st.info("All transcript loading methods failed or returned empty.")
                    st.stop()
                
                st.info("Transcript loaded successfully.")

            except Exception as e_outer: # Outer try-except for unexpected errors
                st.error(f"An unexpected error occurred during transcript loading: {str(e_outer)}")
                st.info(f"Outer try-except block error during transcript loading: {str(e_outer)}")
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
            model_name="gpt-3.5-turbo",
            openai_api_key=st.session_state.api_key,
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
        system_prompt = """You are an expert at creating viral X (formerly Twitter) threads that engage and inform your audience.
Your task is to create a compelling thread based on the summary of a YouTube video.

First, provide a concise summary of the video in 2-3 sentences. This summary should be different from the input summary and act as an intro.
Then create the thread based on the **input summary** provided below.

Thread Requirements:
1. Structure:
   - First tweet: Start with a powerful hook or thought-provoking question. End with "…🧵" or a similar threading emoji.
   - First tweet: Must NOT have a number like (1/N) at the beginning.
   - Second tweet onwards: Number them clearly, e.g., (2/7), (3/7), etc. The total N should reflect the actual number of tweets in this segment.
   - Last tweet: Include a strong call-to-action and the placeholder for the video URL: {{url}} (the app will replace this).

2. Content Guidelines:
   - Extract and explain the main arguments from the input summary.
   - Include specific examples and key points if present in the input summary.
   - Highlight unique perspectives and insights.
   - Aim for 3-5 practical takeaways if applicable.
   - Discuss broader context and implications if relevant.
   - Make it comprehensive enough for someone who hasn't seen the video but read the input summary.

3. Technical Rules:
   - Each tweet must be STRICTLY ≤ 280 characters.
   - Use a maximum of 2-3 relevant emojis in the ENTIRE thread (use them only when they add significant value).
   - Vary sentence structure for better readability.
   - Ensure every tweet is attention-grabbing and adds value.
   - Avoid filler content or overly verbose sentences.

4. Style:
   - Use an engaging, conversational, yet informative tone.
   - If the video summary mentions "the YouTuber" or a specific name, use that. Otherwise, terms like "the creator" or "the video" are fine.
   - Make complex ideas accessible.
   - Create a clear narrative flow between tweets.

5. Language:
   - The ENTIRE output (summary and thread) must be in **{language}**.

Format your response EXACTLY like this, with "SUMMARY:" and "THREAD:" as markers:
SUMMARY:
[Your NEW 2-3 sentence introductory summary here]

THREAD:
[Tweet 1: Hook... 🧵]
[Tweet 2: (2/N) Content...]
[Tweet 3: (3/N) Content...]
...
[Tweet N: (N/N) Call to action with {{url}}]

Here is the input summary of the video to base your thread on:
{summary}
"""

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
            
            # Split by tweet markers (1/, 2/, etc.)
            parts = thread_part.split('(')
            for part in parts:
                if part.strip():
                    # Remove tweet numbering and clean up
                    tweet = part.split(')')[-1].strip()
                    if tweet:
                        # Replace {url} with actual video URL
                        tweet = tweet.replace("{url}", video_url)
                        tweets.append(tweet)
            
        except Exception as e:
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
        
        # Display each tweet in its own text field
        st.subheader("Generated Thread")
        for i, tweet in enumerate(tweets):
            # Create a text area for the tweet
            st.text_area(
                label=f"Tweet {i+1}",
                value=tweet,
                key=f"tweet_{i}",
                disabled=True,
                height=100
            )
            st.write("")  # Add spacing between tweets

        st.write("")
        st.divider()

        # Buy Me a Coffee button
        button(username="kguba", floating=False, width=221)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
