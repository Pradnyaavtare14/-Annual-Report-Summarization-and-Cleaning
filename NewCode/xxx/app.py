import streamlit as st
from PyPDF2 import PdfReader
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# Define function to summarize text using Sumy
def summarize_text(text, num_sentences=3):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, num_sentences)
    summary_text = [str(sentence) for sentence in summary]
    return summary_text

# Function to create a well-organized PDF from the summary
def create_pdf(summary_data):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 40, "Summary of the PDF Document")
    c.setFont("Helvetica", 12)
    y_position = height - 80

    # Loop through the summary data and format it
    for page_num, summary in summary_data.items():
        c.setFont("Helvetica", 12)
        for sentence in summary:
            c.drawString(100, y_position, f"- {sentence}")
            y_position -= 15

        # Add space between pages
        y_position -= 20
        if y_position < 100:  # Check if we are running out of space on the page
            c.showPage()  # Start a new page
            y_position = height - 40
    
    c.save()
    buffer.seek(0)
    return buffer

def main():
    # Set page title and favicon
    st.set_page_config(page_title="PDF2Brain", page_icon=":brain:")

    # Sidebar contents
    with st.sidebar:
        st.title('🧠 PDF2Brain')
        st.markdown('''## Intelligent Document Data Extractor.''')

    # Use tabs for different sections of the app
    tab1, tab2 = st.tabs(["Upload PDF", "Summary of the PDF"])

    # Upload PDF tab
    with tab1:
        pdf = st.file_uploader("Upload your PDF", type='pdf', help="Click the button to upload your PDF file.")
        if pdf:
            # Read PDF and extract text
            pdf_reader = PdfReader(pdf)
            st.subheader("Extracted Data by Page")

            for page_num, page in enumerate(pdf_reader.pages):
                st.write(f"## Page {page_num + 1}")
                text = page.extract_text()
                st.write("### Text:")
                st.write(text)

    # Summary tab
    with tab2:
        if pdf:
            pdf_reader = PdfReader(pdf)
            st.subheader("Page-wise Summary")
            num_sentences = st.number_input("Number of sentences in the summary per page:", min_value=1, max_value=10, value=3, help="Choose the number of sentences to include in the summary.")
            
            summary_data = {}

            # Position the download button at the top of the summary section
           

            # Loop through the pages and generate summaries
            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()
                if text:
                    summary_sentences = summarize_text(text, num_sentences)
                    summary_data[page_num] = summary_sentences
                    
                    # Display summary in an organized and visually appealing way
                    st.markdown(f"#### **Page {page_num + 1}**")
                    st.write("Here is the summary for this page:")
                    for sentence in summary_sentences:
                        st.markdown(f"- {sentence}")

            # Provide the download button after the summary is displayed
            st.markdown("### 📥 Download the Summary as a PDF:")
            if summary_data:
                pdf_buffer = create_pdf(summary_data)
                st.download_button(
                    label="Download PDF Summary",
                    data=pdf_buffer,
                    file_name="summary.pdf",
                    mime="application/pdf"
                )

if __name__ == "__main__":
    main()
