'''
SI568 Mini Project
uniqname: wushiyu
In order to run the script, please run "pip install -r requirements.txt" first and run "streamlit run streamlit.py".
'''

import wave
import openai
import streamlit as st
import extra_streamlit_components as stx
import caching
from apiKey import key
from st_custom_components import st_audiorec
from streamlit_chat import message

# chat_history is a global Python object used to store chat history
chat_history = caching.openCache('history.json')


def realtimeAudio(channel, rate, filename):
    '''
    set up a real-time audio recorder component on Streamlit webapp.
    Store the recorded audio to a wav file and check whether the file is valid.

    Parameters:
    channel: int
        The number of channels to be used during recording.
    rate: int
        The sampling rate during recording.
    filename: string
        The name of the file which stores the recorded wav.

    Returns:
    bool
        Whether the wav file passed the checking and is stored.
    '''
    # Initialize a real-time recorder component. This component is found in a public Github repo whose owner is stefanrmmr.
    # URL: https://github.com/stefanrmmr/streamlit_audio_recorder
    # I used the complete component including the Python script and all the
    # frontend scripts
    wav_audio_data = st_audiorec()
    # If data is collected, save the data to a wav file
    if wav_audio_data is not None:
        waveFile = wave.open(filename, 'wb')
        waveFile.setnchannels(channel)
        waveFile.setsampwidth(2)
        waveFile.setframerate(rate)
        waveFile.writeframes(wav_audio_data)
        waveFile.close()
        # Check whether the wav file is valid
        checkFile = wave.open(filename, 'rb')
        if checkFile.getnframes() > 11:
            checkFile.close()
            return True
        checkFile.close()
    return False


def transcript(key, filename, ph):
    '''
    Using whisper, the transcribing model trained by OpenAi, get the transcription of the recorded audio.

    Parameters:
    key: string
        the OpenAI API authentication key.
    filename: string
        The name of the file which stores the recorded audio.
    ph: streamlit container
        The container that holds texts to be shown in the webapp.

    Returns:
    string
        The transcribed texts.
    '''
    ph.write('Processing...')
    audio_file = open(filename, "rb")
    # Implement OpenAI API to generate the transcription
    openai.api_key = key
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    # Show the transcribed text in the streamlit container
    ph.empty()
    ph.write(transcript['text'])
    return transcript['text']


def chat(key, message):
    '''
    Implement gpt-3.5-turbo model to build a chatbot with memory.

    Parameters:
    key: string
        The OpenAI API authentication key.
    message: string
        The message to be sent to the chatbot.

    Returns:
    string
        The response from the chatbot.
    '''
    # Append the message to be sent to the chat history to make a complete
    # conversation
    chat_history.append({'role': 'user', 'content': message})
    # Implement the OpenAI API to generate a chat response
    # Give the whole conversation to make the chatbot has memory
    # Set top_p to 0.5 to restrict the output so that the response has a
    # appearing probability of over 0.5
    openai.api_key = key
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        # Provide necessary prompts so the chatbot can react as an assistant
        # detective.
        messages=[{'role': 'user', 'content': 'Let us play a detective game!'},
                  {'role': 'assistant',
                   'content': 'Great idea! I am ready to play. What is the game about?'},
                  {'role': 'user', 'content': 'I will give you some information about the criminal\'s\
                    appearance provided by the witnesses. \
                   Your job is to request any detail you need to make a sketch of the criminal. \
                   After this, your job is to provide a summarize of all gathered information.'},
                  {'role': 'assistant', 'content': 'Sounds like a fun challenge! Let us get started. \
                    What information do you have about the criminal\'s appearance?'}]
        + chat_history,
        top_p=0.5
    )
    # Append the response to the chat history to make a complete conversation
    chat_history.append(
        {'role': 'assistant', 'content': response['choices'][0]['message']['content']})
    # Update the cache file
    caching.writeCache(chat_history, 'history.json')
    return response['choices'][0]['message']['content']


def image(text, key, ph):
    '''
    Using DALL-E model provided by OpenAI, generate an image based on given texts.

    Parameters:
    text: string
        The text used to generate the image.
    key: string
        The OpenAI API authentication key.
    ph: streamlit container
        The container that holds an image to be shown in the webapp.

    Returns:
    string
        The URL whose content is the generated image.
    '''
    # Implement the OpenAI API to generate the image
    # The number of image is set to be 1
    # The size of the generated image is set to be 512x512
    openai.api_key = key
    ph.write('generating image...')
    response = openai.Image.create(
        # Provide prompts so the AI generates a sketch of the suspect.
        prompt='Please give me a criminal sketch. ' + text,
        n=1,
        size="512x512"
    )
    return response['data'][0]['url']


def submit():
    '''
    A procedure used to clear the chatbox on pressing enter and store the entered texts to another session container.
    '''
    # Store the chatbox texts to another session container
    st.session_state.something = st.session_state.input
    # Clear the chatbox texts
    st.session_state.input = ''


def get_text():
    '''
    Utilize streamlit chatbox component to get the user input.

    Returns:
    string
        the entered texts from the user.
    '''
    # Initialize the session container used to store the entered texts
    if 'something' not in st.session_state:
        st.session_state.something = ''

    # Utilize streamlit chatbox component
    # The session container will have the key of input, namely st.session_state.input or st.session_state['input']
    # The chatbox will run submit procedure on pressing enter
    st.text_input("Enter your message: ", key="input", on_change=submit)
    # If enter is pressed, the input session container will be cleared, and
    # the entered texts are stored in something session container
    input_text = st.session_state.something
    return input_text


def clear_history(filename, assistant, user, input_text):
    '''
    The procedure clears out the chat history including the cache file and the streamlit session containers.

    Parameters:
    filename: string
        The name of the cache file.
    assistant: string
        The name of the streamlit session container that stores the history response.
    user: string
        The name of the streamlit session container that stores the history user message.
    input_text: string
        The name of the streamlit session container that stores the current user input.
    '''
    del st.session_state[assistant]
    del st.session_state[user]
    del st.session_state[input_text]
    caching.clearCache(filename)


def chat_initialization(assistant, user):
    '''
    The procedure initialize two streamlit session container to store the history responses and user messages.

    Parameters:
    assistant: string
        The name of the streamlit session container that stores the history response.
    user: string
        The name of the streamlit session container that stores the history user message.
    '''
    if assistant not in st.session_state:
        st.session_state[assistant] = []
    if user not in st.session_state:
        st.session_state[user] = []


def print_message(assistant, user):
    '''
    The procedure prints out the chat conversations using streamlit message component.

    Parameters:
    assistant: string
        The name of the streamlit session container that stores the history response.
    user: string
        The name of the streamlit session container that stores the history user message.
    '''
    if st.session_state[assistant]:
        for i in range(len(st.session_state[assistant]) - 1, -1, -1):
            message(st.session_state[assistant][i], key=str(i))
            message(
                st.session_state[user][i],
                is_user=True,
                key=str(i) + '_user')


def tab1():
    '''
    The procedure executes the script when tab1 is selected.
    '''
    st.title('Chat with your assistant detective')
    # If button is clicked, history will be cleared
    # NOTICE: if the button is clicked when chatbox is filled and waiting to
    # be submitted, the texts in the chatbox will still be treated as submit
    if st.button('Clear chat history'):
        clear_history('history.json', 'generated', 'past', 'something')

    chat_initialization('generated', 'past')

    text = get_text()
    # If text is captured, chat function will be executed
    if text:
        response = chat(key, text)
        # record the conversation in the streamlit session container
        try:
            st.session_state['past'].append(text)
            st.session_state['generated'].append(response)
        except BaseException:
            pass
    # print the whole conversation
    try:
        print_message('generated', 'past')
    except BaseException:
        pass


def tab2():
    '''
    The procedure executes the script when tab2 is selected.
    '''
    st.title("Suspect sketch generation")
    st.write('Example: The suspect was a seven-feet tall male wearing a black hoodie with brown hair, black eyes, and a knife scar across the right eye.')
    st.write('The program currently supports an audio under 30 seconds.')
    # build a sidebar and put the recorder component in the sidebar
    with st.sidebar:
        st.title('Record audio here')
        st.write(
            'For Mac, click Start Recording to record audio and click Stop to stop recording.')
        st.write(
            'For Windows, click Start Recording and then click Stop to initialize the recorder.')
        st.write(
            'After initialization, click Start Recording to record. Click Stop to stop recording.')
        st.write(
            'Click reset to clear the recorded audio. Click Download to download the recorded audio.')
        # record real-time audio
        flag = realtimeAudio(2, 44100, 'output.wav')
    text = None
    img = None
    # initialize streamlit place holders
    ph1 = st.empty()
    ph2 = st.empty()
    # If audio is saved and checked, it will be transcribed
    if flag is True:
        text = transcript(key, 'output.wav', ph1)
    # If the transcription is generated, an image is generated based on the
    # transcription
    if text is not None:
        img = image(text, key, ph2)
        ph2.image(img)


if __name__ == '__main__':
    # Build a tab bar and store the current tab
    chosen_id = stx.tab_bar(data=[
                            stx.TabBarItemData(
                                id="tab1", title="Chat", description="Chat with your assistant detective"),
                            stx.TabBarItemData(id="tab2", title="Sketch generation", description="Voice to suspect sketch")],
                            default='tab1')
    # If current tab is tab1, execute chat
    if chosen_id == 'tab1':
        tab1()
    # If current tab is tab2, execute voice to image
    if chosen_id == 'tab2':
        tab2()
