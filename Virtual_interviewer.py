import time
import os
from pdfminer.high_level import extract_text
from gtts import gTTS
import streamlit as st
import speech_recognition as sr
import pyttsx3
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.exceptions import OutputParserException
from pydub import AudioSegment
from pydub.playback import play
# st.title("Groq Interviewer Chatbot with Voice Support")

# Set your Groq API key directly
GROQ_API_KEY = "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"
#st.title("Groq Interviewer Chatbot with Voice Support")
# Define the chatbot class
class GroqChatbot:
    def __init__(self):
        self.llm = ChatGroq(temperature=0, groq_api_key=GROQ_API_KEY, model_name="llama-3.1-70b-versatile")

    def get_response(self, user_input):
        st.session_state.conversation_history.append({"role": "user", "content": user_input})
        prompt_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.conversation_history[-5:]])

        prompt = PromptTemplate.from_template(
            f"""
            ### CONVERSATION HISTORY:
            {prompt_text}

            ### INSTRUCTION:
            Respond as a professional interviewer chatbot. Provide basic interview questions based on conversation history and ask questions to test the skills, asking one question at a time.
            """
        )
        
        retries = 3
        for attempt in range(retries):
            try:
                response = prompt | self.llm
                result = response.invoke(input={})
                bot_response = result.content.strip()

                # Append the bot's response to the conversation history
                st.session_state.conversation_history.append({"role": "Interviewer", "content": bot_response})
                return bot_response
            except OutputParserException as e:
                return f"Error: {str(e)}"
            except Exception as e:
                if 'Rate limit reached' in str(e):
                    wait_time = 60  # Wait for 60 seconds before retrying
                    st.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    return f"Error: {str(e)}"
# st.title("Groq Interviewer Chatbot with Voice Support")
def try2():
    # st.title("Groq Interviewer Chatbot with Voice Support")
    
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'user_input' not in st.session_state:
        st.session_state.user_input = ""
    if 'pdf_processed' not in st.session_state:
        st.session_state.pdf_processed = False
    
    if not st.session_state.pdf_processed:
        uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
        if uploaded_file is not None:
            extracted_text = extract_text(uploaded_file)
            # Set the flag to indicate that the PDF has been processed
            st.session_state.pdf_processed = True

            # Initialize the conversation history with extracted PDF text as user input
            # st.session_state.conversation_history.append({"role": "user", "content": extracted_text})

            # After processing the PDF, prompt the chatbot to start asking questions
            chatbot = GroqChatbot()
            initial_question = chatbot.get_response(extracted_text)  # Get the first question based on PDF content
            # st.session_state.conversation_history.append({"role": "Interviewer", "content": initial_question})
        if st.session_state.conversation_history:    
            for msg in st.session_state.conversation_history:
                if msg['role'] == 'user':
                    st.markdown(
                                f"""
                                <div style='text-align: right; background-color: #414A4C; padding: 10px; border-radius: 10px; margin: 5px 0;'>
                                    <strong>You:</strong> {msg['content']}
                                </div>
                                """, unsafe_allow_html=True
                            )
                else:
                                st.markdown(
                                f"""
                                <div style='text-align: left; background-color: #000000; padding: 10px; border-radius: 10px; margin: 5px 0;'>
                                    <strong>Inerviewer:</strong> {msg['content']}
                                </div>
                                """, unsafe_allow_html=True
                            )
            play_bot_response(bot_response=initial_question)
        

    st.write("Press the microphone button to record your response, or type your answer below.")
    if st.button("🎤 Record Voice"):
        voice_input = record_audio()
        if voice_input:
            st.session_state.user_input = voice_input
    st.text_input("Your Response:", key="user_input",on_change=send_message)
    
    
def send_message(): 
    if st.session_state.user_input:
        # Initialize the chatbot instance
        chatbot = GroqChatbot()
        # Get response from the chatbot with the latest user input
        bot_response = chatbot.get_response(st.session_state.user_input)
        st.title("Groq Interviewer Chatbot with Voice Support")
        if st.session_state.conversation_history:    
            for msg in st.session_state.conversation_history:
                if msg['role'] == 'user':
                        st.markdown(
                        f"""
                        <div style='text-align: right; background-color: #414A4C; padding: 10px; border-radius: 10px; margin: 5px 0;'>
                            <strong>You:</strong> {msg['content']}
                        </div>
                        """, unsafe_allow_html=True
                    )
                else:
                        st.markdown(
                        f"""
                        <div style='text-align: left; background-color: #000000; padding: 10px; border-radius: 10px; margin: 5px 0;'>
                            <strong>Inerviewer:</strong> {msg['content']}
                        </div>
                        """, unsafe_allow_html=True
                    )
        
        
        

        play_bot_response(bot_response)
        # Clear the input for the next question
        st.session_state.user_input = ""
    
def record_audio():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        
        audio = recognizer.listen(source)
    
    try:
        text = recognizer.recognize_google(audio)
        st.write("You said:", text)
        return text
    except sr.UnknownValueError:
        st.write("Sorry, I could not understand your voice.")
    except sr.RequestError:
        st.write("Could not request results; check your network connection.")
    return None

    

def play_bot_response(bot_response):
    audio_file = "temp_response.mp3"
    tts = gTTS(text=bot_response, lang='en')
    tts.save(audio_file)

    if os.path.exists(audio_file):
        audio_data = AudioSegment.from_file(audio_file, format="mp3")
        play(audio_data)
    else:
        st.error("Audio file not found.")
try2()