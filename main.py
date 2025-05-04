import streamlit as st
import os
import time
from langchain_community.document_loaders import YoutubeLoader
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import TokenTextSplitter
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from streamlit_extras.buy_me_a_coffee import button
from langchain.schema import Document

# Initialize session state for language
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = 'en'

# Lade Umgebungsvariablen
load_dotenv()

st.title("🧵 Anything To Thread")

# Füge Abstand hinzu
st.write("")
st.write("")

st.write("Ever wanted to create a thread from a YouTube video? Now you can!")
st.write("Just paste ur openai key and paste the youtube url and let the magic happen.")




# Füge Divider hinzu
st.divider()


# URL Eingabe
video_url = st.text_input("Enter YouTube Video URL:")
st.write("")
openai_key_input = st.text_input("Enter Your OpenAI Key:")
st.write("")
# Language selection buttons
col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
with col1:
    st.write("Thread language:", unsafe_allow_html=True)
with col2:
    if st.button("🇺🇸", use_container_width=True):
        st.session_state.selected_language = 'en'
with col3:
    if st.button("🇩🇪", use_container_width=True):
        st.session_state.selected_language = 'de'
with col4:
    if st.button("🇪🇸", use_container_width=True):
        st.session_state.selected_language = 'es'
st.write("")
# Create container for button
button_container = st.container()

with button_container:
    submit_button = st.button("Submit")

# Füge Divider hinzu
st.divider()
st.write("")

#button(username="kguba", floating=False, width=221)

if submit_button and video_url:
    try:
        # Validate URL
        if not video_url.startswith(("https://www.youtube.com/", "https://youtu.be/")):
            st.error("Please enter a valid YouTube URL")
            st.stop()

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
        
        # System Prompt für die Thread-Erstellung
        system_prompt = """You are an expert at creating viral X (Twitter) threads that engage and inform your audience.
Your task is to create a compelling thread based on the summary of a YouTube video.

Thread Requirements:
1. Structure:
   - First tweet: Start with a powerful hook or thought-provoking question, end with "…🧵"
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

5. Language:
   - Create the thread in {language}

Here is the summary of the video:
{summary}

Create a thread that makes people want to watch the video while providing genuine value."""

        # Summarize
        with st.spinner("Generating summary and thread..."):
            # Erste Zusammenfassung
            summarize_chain = load_summarize_chain(llm=llm, chain_type="refine", verbose=True)
            
            # Process chunks with progress updates
            for i, chunk in enumerate(chunks):
                # Update progress
                progress = (i + 1) / total_chunks
                progress_bar.progress(progress)
                
                # Update status text
                status_text.text(f"Processing chunk {i + 1} of {total_chunks}")
                
                # Process chunk
                if i == 0:
                    summary = summarize_chain.run([chunk])
                else:
                    # Create a new document with the previous summary
                    summary_doc = Document(page_content=summary)
                    summary = summarize_chain.run([chunk, summary_doc])

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
            thread = llm.predict(thread_prompt)

            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()

            # Display summary and thread
            st.subheader("Summary")
            st.write(summary)
            
            st.subheader("Generated Thread")
            st.write(thread)

            # Option to download both
            combined_text = f"Summary:\n\n{summary}\n\nThread:\n\n{thread}"
            st.download_button(
                label="Download Summary and Thread",
                data=combined_text,
                file_name="summary_and_thread.txt",
                mime="text/plain"
            )

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
