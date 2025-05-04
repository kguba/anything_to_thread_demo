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

# Initialize session state for animation
if 'animation_running' not in st.session_state:
    st.session_state.animation_running = False

# Lade Umgebungsvariablen
load_dotenv()

st.title("🧵 Anything To Thread")

# Füge Abstand hinzu
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

# Create container for button and time estimate
button_container = st.container()

# Create two columns for the submit button and time estimate
col1, col2 = st.columns([1, 4])

with button_container:
    with col1:
        submit_button = st.button("Submit")

    with col2:
        time_text = st.markdown("", unsafe_allow_html=True)
        if submit_button and video_url:
            time_text.markdown("<div style='margin-top: 8px; text-align: right;'>Estimated time: Calculating...</div>", unsafe_allow_html=True)

# Füge Divider hinzu
st.divider()
st.write("")

#button(username="kguba", floating=False, width=221)

if submit_button and video_url:
    try:
        # Load Transcript
        with st.spinner("Loading video transcript..."):
            loader = YoutubeLoader.from_youtube_url(video_url, language=["en", "en-US", "de", "de-DE"])
            transcript = loader.load()

        # Split Transcript with smaller chunks
        with st.spinner("Splitting transcript into chunks..."):
            splitter = TokenTextSplitter(model_name="gpt-4", chunk_size=500, chunk_overlap=50)
            chunks = splitter.split_documents(transcript)
            total_chunks = len(chunks)

        # Set up LLM
        llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4",
            temperature=0.3
        )

        # Create progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Initialize time tracking
        start_time = time.time()
        chunk_times = []

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

Here is the summary of the video:
{summary}

Create a thread that makes people want to watch the video while providing genuine value."""

        # Summarize
        with st.spinner("Generating summary and thread..."):
            # Erste Zusammenfassung
            summarize_chain = load_summarize_chain(llm=llm, chain_type="refine", verbose=True)
            
            # Process chunks with progress updates
            for i, chunk in enumerate(chunks):
                chunk_start_time = time.time()
                
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
                
                # Calculate time for this chunk
                chunk_time = time.time() - chunk_start_time
                chunk_times.append(chunk_time)
                
                # Calculate average time per chunk and estimate remaining time
                avg_chunk_time = sum(chunk_times) / len(chunk_times)
                remaining_chunks = total_chunks - (i + 1)
                estimated_remaining_time = avg_chunk_time * remaining_chunks
                
                # Update time estimate
                with col2:
                    time_text.markdown(f"<div style='margin-top: 8px; text-align: right;'>Estimated time: {int(estimated_remaining_time)} seconds remaining</div>", unsafe_allow_html=True)

            # Thread-Erstellung mit dem System-Prompt
            prompt = PromptTemplate(
                input_variables=["summary", "url"],
                template=system_prompt
            )
            
            thread_prompt = prompt.format(summary=summary, url=video_url)
            thread = llm.predict(thread_prompt)

            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            time_text.empty()

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
