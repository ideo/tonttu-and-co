import pickle

import streamlit as st


st.title("Tonttu & Co. is here to help!")


df = pickle.load(open("airtable_data.pkl", "rb"))
st.dataframe(df)