import streamlit as st
import random
import tempfile
import time
import os
from agent import create_agent  

st.title("Simple chat")

# Initialize necessary stuff 
if "file_path" not in  st.session_state:
    st.session_state.file_path = None

if "file_name" not in  st.session_state:
    st.session_state.file_name = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "agent" not in st.session_state:
    st.session_state.agent = None

    
#file upload 
data = st.file_uploader(label="Upload file", type='xlsx')

if data is not None:
    file_path = os.path.join("./files", data.name)
    #storing to session state
    st.session_state.file_name = data.name
    st.session_state.file_path = file_path    
    with open(file_path, "wb") as f: 
      f.write(data.getbuffer())  



if st.session_state.file_name:
    st.markdown(f"*Currently working with* **{st.session_state.file_name}**")
else:
    st.markdown("There is no file to work with :(")

#initialize agent 
if st.session_state["file_path"]:
    agent = create_agent(temperature=0, file_path=file_path)
    st.session_state.agent = agent

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        if st.session_state.agent:
            for step in agent.iter(
                {"input": prompt, "file_path": st.session_state.file_path}
            ):
                if "intermediate_step" in step:
                    intermediate_step = step["intermediate_step"][0]
                    action, observation = intermediate_step
                    response = action.log + "\n" + f"```python:\n{observation}\n```\n\n"

                if "output" in step:
                    output = step["output"]
                    response = output
                for chunk in response:
                    full_response += chunk
                    time.sleep(0.001)
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)

        else:
            response = "Agent is not created yet I guess"
            for chunk in response.split():
                full_response += chunk + " "
                time.sleep(0.05)
                message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})