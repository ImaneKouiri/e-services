import streamlit as st
from openai_utils import OpenAI_Chat
from agent import BaseAgent
from prompt import set_prompt
from key import gpt_key
import time

st.title("EchoLang")
caption_placeholder = st.empty()

def handle_chat():
    caption_placeholder.caption("🚀 A chatbot powered by artificial intelligence that helps you learn languages.")
    agent = st.session_state.agent
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Tapez votre message ici..."):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        response = agent.generate(prompt)
        def stream_data():
            for char in list(response):
                yield char
                time.sleep(0.01)
                
        # Display assistant response in chat message container
        with st.chat_message("assistant", avatar=st.session_state.bot_avatar):
            st.write_stream(stream_data)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})



    
# Initialize user name and avatar if not set
if "user_name" not in st.session_state or not st.session_state.user_name:
    caption_placeholder.caption("🚀 A chatbot powered by artificial intelligence that helps you learn languages.")
    with st.form(key='user_form'):
        user_name = st.text_input("Please enter your name:")
        user_avatar = st.radio(
            "Please choose an avatar:",
            ["🐼", "🐶", "🐱", "🦊", "🦄", "🌸", "⭐", "🌈", "❄️", "👻", "👾"],
            index=0,
            horizontal=True,
        )

        st.markdown("<p style='font-size: 14px;'>Please choose a language:</p>", unsafe_allow_html=True)
        en = st.checkbox("🇬🇧 English")
        es = st.checkbox("🇪🇸 Spanish")

        submit_button = st.form_submit_button(label='Start Chat')

    if submit_button and user_name:
        if en and es:
            st.error("Choose only one language.")
        elif not en and not es:
            st.warning("Please choose a language.")
        else:
            gpt = OpenAI_Chat(config={"model": "gpt-4o-2024-08-06", "api_key": gpt_key})
            st.session_state.bot_avatar = "🤖"
            st.session_state.user_name = user_name
            st.session_state.user_avatar = user_avatar
            st.session_state.lang = "anglais" if en else "espagnole"
            st.session_state.agent = BaseAgent(llm=gpt, system_prompt=set_prompt(lang=st.session_state.lang))
            caption_placeholder.caption(f"🚀 Hi {st.session_state.user_avatar} {st.session_state.user_name}, welcome to the chatbot powered by artificial intelligence.")
            st.rerun()

else:
    handle_chat()

