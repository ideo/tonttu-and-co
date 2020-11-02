import streamlit as st
from streamlit_observable import observable
# from streamlit_vega_lite import vega_lite_component
# import matplotlib.pyplot as plt

from connectedness import load_data, heatmap, vega_grouped_bar_chart


st.title("Tonttu & Co. is here to help!")
msg = """
A few months ago, a large IDEO attempted to measure how connected they were 
as a team. Each team member gave a rating on a scale from 1 to 10 on how close 
they felt to each other team member. Here is the data they collected:
"""
st.write(msg)

pairwise_df = load_data()
st.table(pairwise_df)
values, vega_light_spec = heatmap(pairwise_df)
st.vega_lite_chart(values, vega_light_spec)


st.header("Perceived Differences")
st.write("How do your perceptions differ from others' perctions of you?")
differences, vega_df, spec = vega_grouped_bar_chart(pairwise_df)
st.vega_lite_chart(vega_df, spec)

threshold = st.sidebar.slider("Threshold for Noticeable Difference", 
    min_value=0, 
    max_value=10,
    value=5)

# noticeable = differences[abs(differences["Difference"]) >= threshold]
# st.dataframe(noticeable)
# st.dataframe(differences)

name = st.selectbox("Please chooose your name.", differences.index.tolist())
individual = differences.loc[name]

if abs(individual["Difference"]) < threshold:
    msg = f"""
    {name}, your perception of your connectedness isnot noticeably different 
    than that of your collegues.
    """
elif individual["Difference"] >= threshold:
    msg = f"""
    {name}, you rated that you feel more connected to your collegues than 
    they did to you.
    """
else:
    msg = f"""
    {name}, your collegues feel more connected to you than you do to them.
    """

st.write(msg)


st.header("Explore the Connections Among Your Team")
observers = observable("Force Graph",
    notebook="@gambingo/force-directed-graph",
    targets=["chart"],
    observe=["data"])

force_graph = observers.get("data")