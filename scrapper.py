import streamlit as st

st.title("🧪 Streamlit Test")
st.markdown("If you see this, your app is working!")

query = st.text_area("Enter something:")
if st.button("Submit"):
    st.write(f"You entered: {query}")
