import streamlit as st
import os
from langchain_community.document_loaders import YoutubeLoader
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import TokenTextSplitter
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()

st.title("Anything To Thread")
st.write("YouTube Video Summarizer")

# URL Eingabe
video_url = st.text_input("Enter YouTube Video URL:")

if video_url:
    try:
        # Load Transcript
        loader = YoutubeLoader.from_youtube_url(video_url, language=["en", "en-US", "de", "de-DE"])
        transcript = loader.load()

        # Split Transcript
        splitter = TokenTextSplitter(model_name="gpt-3.5-turbo-16k", chunk_size=10000, chunk_overlap=100)
        chunks = splitter.split_documents(transcript)

        # Set up LLM
        llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-3.5-turbo-16k",
            temperature=0.3
        )

        # Summarize
        with st.spinner("Generating summary..."):
            summarize_chain = load_summarize_chain(llm=llm, chain_type="refine", verbose=True)
            summary = summarize_chain.run(chunks)

            # Display summary
            st.subheader("Summary")
            st.write(summary)

            # Option to download summary
            st.download_button(
                label="Download Summary",
                data=summary,
                file_name="summary.txt",
                mime="text/plain"
            )

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
