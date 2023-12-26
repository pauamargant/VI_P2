import streamlit as st

# open readme.md file
with open("readme.md", "r") as f:
    readme = f.read()
st.title("Instructions")
st.markdown(readme)
