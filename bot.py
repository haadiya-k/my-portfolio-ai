import requests
import streamlit as st
from streamlit import session_state
import openai

# Set the page configuration
st.set_page_config(page_title="my portfolio AI", layout="wide")

# Access API Key
try:
    openai.api_key = st.secrets["openai_key"]
    resume_api_key = st.secrets["resume_key"]
except KeyError as e:
    st.error(f"Failed to load keys from Streamlit secrets: {e}")
    st.stop()

# Define API URL
api_url = st.secrets["resume_api_url"]

# Header with API key
headers = {
    'x-api-key': resume_api_key
}

# Function to fetch resume data from the API
@st.cache_data
def get_resume_data(api_url, headers):
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()
    return response.json()

# Fetch resume data and store it in session state
if 'resume_data' not in st.session_state:
    try:
        st.session_state['resume_data'] = get_resume_data(api_url, headers)
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching resume data: {e}")
        st.session_state['resume_data'] = {}  # empty dictionary

# Initialise resume_data
resume_data = st.session_state['resume_data']


if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'portfolio AI'

# Sidebar Navigation
st.sidebar.title("navigation")
if st.sidebar.button("portfolio AI"):
    st.session_state["current_page"] = "portfolio AI"
if st.sidebar.button("about me"):
    st.session_state["current_page"] = "about me"
if st.sidebar.button("contact"):
    st.session_state["current_page"] = "contact"

if st.session_state['current_page'] == 'portfolio AI':
    # Function to generate chatbot response with streaming similar to ChatGPT
    def generate_response(chat_history, user_input):
        prompt = (
            "You are a chatbot that answers questions about Haadiya's portfolio **as if you are Haadiya herself**. "
            "Respond in the first person (e.g., 'I have experience in...')."
            "Use emojis when necessary. Keep responses engaging, friendly, and a little bit fun! "
            "If someone asks something unrelated to Haadiya's portfolio, politely decline."
            "DO NOT use AI phrases like 'Hey there! How can I assist you today?."
        )

        structured_data = "\n".join(
            f"**{key.capitalize()}**:\n" + (
                "\n- ".join([""] + [f"I {str(v)}" for v in value]) if isinstance(value, list) else f"I {str(value)}")
            for key, value in resume_data.items()
        )
        prompt += structured_data

        # Add chat history for context
        for role, content in chat_history:
            prompt += f"\n{role}: {content}"

        prompt += f"\nUser: {user_input}\nChatbot:"

        try:
            response_stream = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_input}
                ],
                stream=True
            )
            return response_stream
        except Exception as e:
            st.error(f"Failed to generate response: {str(e)}")
            return None

    # Streamlit UI
    st.title("portfolio AI")
    st.write("**ask me about my skills, projects, education, and experience!**")

    # Store chat history
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Show chat history
    for role, message in st.session_state["chat_history"]:
        with st.chat_message(role):
            st.write(message)

    # User input
    user_input = st.chat_input("ask me something! ")

    if user_input:
        with st.chat_message("User"):
            st.write(user_input)

        # Save user input
        st.session_state["chat_history"].append(("User", user_input))

        # Display chatbot response as it generates
        with st.chat_message("Chatbot"):
            typing_placeholder = st.empty()

            response_stream = generate_response(st.session_state["chat_history"], user_input)

            if response_stream and hasattr(response_stream, "__iter__"):  # Ensure response is iterable
                full_response = ""
                for chunk in response_stream:
                    if chunk.choices:
                        text_chunk = chunk.choices[0].delta.content or ""
                        full_response += text_chunk
                        typing_placeholder.write(full_response)  # Update UI in real-time

                st.session_state["chat_history"].append(("Chatbot", full_response))
            else:
                st.error("Failed to generate response. Please try again later.")

# About me page
elif session_state["current_page"] == 'about me' :
    st.title("about me")

    st.markdown("""######
    Hi there, I'm Haadiya! 👋
    I am a college student majoring in Computer Science with a minor in Business Analytics, 
    which fuels my enthusiasm for both technology and strategic data analysis. 
    My academic path is driven by a strong passion for leveraging technology to discover 
    innovative solutions and make data-driven decisions that influence real-world outcomes. 
    
    Alongside my studies, I actively participate in various projects, striving to apply 
    what I've learned in impactful ways.
    
    When I take a break from my studies, I enjoy playing video games and unwinding by watching a series. 
    These hobbies not only help me relax but also spark my creativity, enriching my personal and 
    professional life.
    
    Thank you for checking out my page! I’m always eager to connect with those who share a passion for 
    technology and innovation.
    """
    )

# Contact page
elif st.session_state["current_page"] == 'contact':
    st.title("let's connect!")

    st.markdown(
        """
        - **LinkedIn:** [linkedin.com/in/haadiyakhan](https://www.linkedin.com/in/haadiyakhan)  
        - **GitHub:** [github.com/haadiya-k](https://github.com/haadiya-k)  
        """
    )

    st.success("Feel free to reach out for professional opportunities, or just to chat about my interests!")