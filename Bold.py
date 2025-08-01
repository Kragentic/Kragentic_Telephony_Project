import streamlit as st

st.title("User Input Form")

with st.form(key='my_form'):
    name = st.text_input(label="Enter your name")
    email = st.text_input(label="Enter your email")
    
    submit_button = st.form_submit_button(label='Submit')

if submit_button:
    st.write(f"Hello {name}!")
    st.write(f"Your email is {email}")
