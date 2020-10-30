import streamlit as st
from streamlit_observable import observable

from connectedness import load_data, load_tsunagi_demo_data


st.title("Tonttu & Co. is here to help!")
msg = """
A few months ago, a large IDEO attempted to measure how connected they were 
as a team. Each team member gave a rating on a scale from 1 to 10 on how close 
they felt to each other team member. Here is the data they collected:
"""
st.write(msg)

df = load_tsunagi_demo_data()
st.table(df)


msg = """
And here are several attempts at visualizing and understanding that data:
"""
st.write(msg)

observers = observable("Force Graph",
    notebook="@gambingo/force-directed-graph",
    targets=["chart"],
    observe=["data"])

force_graph = observers.get("data")


