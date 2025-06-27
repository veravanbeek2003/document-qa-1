import streamlit as st
from together import Together

def chunk_text(text, chunk_size=4000):
    """Split text into chunks of a specified size."""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def summarize_chunk(client, chunk):
    """Summarize a chunk of text using the Together API."""
    messages = [
        {
            "role": "user",
            "content": f"Summarize the following text briefly: {chunk}",
        }
    ]

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        messages=messages,
        max_tokens=200  # Limit the response size for brevity
    )

    summary = response.choices[0].message.content
    return summary

# Streamlit app code
st.title("📄 Document Chatbot")
st.write(
    "Upload a document below and ask a question about it. This chatbot uses Together's API to generate responses."
)

api_key = st.text_input("Together API Key", type="password")

if not api_key:
    st.info("Please add your API key to continue.", icon="🗝️")
else:
    client = Together(api_key=api_key)
    uploaded_file = st.file_uploader("Upload a document (.txt or .md)", type=("txt", "md"))

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question about the document"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if uploaded_file:
            document = uploaded_file.read().decode()
            document_chunks = chunk_text(document)
            summaries = []

            for chunk in document_chunks:
                summary = summarize_chunk(client, chunk)
                summaries.append(summary)

            full_summary = " ".join(summaries)

            messages = [
                {
                    "role": "user",
                    "content": f"Here's a summary of the document: {full_summary}\n\n---\n\n{prompt}",
                }
            ]

            response = client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                messages=messages,
                stream=True
            )

            with st.chat_message("assistant"):
                full_response = ""
                response_placeholder = st.empty()
                for chunk in response:
                    if hasattr(chunk.choices[0], 'delta') and chunk.choices[0].delta.content is not None:
                        full_response += chunk.choices[0].delta.content
                        response_placeholder.markdown(full_response + "▌")
                response_placeholder.markdown(full_response)

            st.session_state.messages.append({"role": "assistant", "content": full_response})
        else:
            st.warning("Please upload a document to ask questions about it.")
