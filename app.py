import streamlit as st
from streamlit_observable import observable
# from streamlit_vega_lite import vega_lite_component
# import matplotlib.pyplot as plt

from connectedness import load_data, heatmap, vega_grouped_bar_chart


st.title("Tsunagi Connectedness Survey")
msg = """
This survey is an attempt to allow you to easily check your teams' level of 
connectedness. Periodically, your team can take the simple survey you filled 
out. Then, here, you can explore the results and discuss.

First, here are the raw numbers from the survey.
"""
st.write(msg)

pairwise_df = load_data()
st.table(pairwise_df)

msg = """
And here is the data displayed in an hopefully more helpful way.
"""
st.write(msg)
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
    {name}, your perception of your connectedness is not noticeably different 
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
    observe=["data", "chart"])

force_graph = observers.get("data")