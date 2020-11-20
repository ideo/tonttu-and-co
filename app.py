import streamlit as st
# from streamlit_observable import observable
# from streamlit_vega_lite import vega_lite_component
import matplotlib.pyplot as plt
import seaborn as sns

from src.connectedness import load_saved_survey_results
from src.connectedness import load_tsunagi_team_data, vega_grouped_bar_chart 
from src.connectedness import clustermap, delta_plot, load_clustermap


st.title("Tsunagi Connectedness Survey")
msg = """
This survey is an attempt to allow you to easily check your teams' level of 
connectedness. Periodically, your team can take the simple survey you filled 
out. Then, here, you can explore the results and discuss.

First, here are the raw numbers from the survey.
"""
st.write(msg)

# pairwise_nan, pairwise_zeros = load_tsunagi_team_data()
pairwise_nan, pairwise_zeros, free_responses = load_saved_survey_results()
st.dataframe(pairwise_nan)

st.header("What does Connectedness mean to you?")
msg = """
The survey asked each person to describe what connectedness meant to them. 
Here are those responses.
"""
st.write(msg)
# st.table(free_responses.reset_index().drop(columns=["Email Address"]))
st.table(free_responses)


st.header("Groups")
msg = """
Below, explore the natural groups that have formed within your team. Darker 
colors represent more closely connected people.
"""
st.write(msg)

# msg = """
# Hey, Team! Play with the settings for this prototype here. We can pick what 
# we like and then disable this sidebar when we deliver it to WorkX.
# """
# st.sidebar.write(msg)

# linkage_method = "single"
linkage_method = st.sidebar.selectbox(
    label="Select the sorting method used by the clustered heatmap",
    options=["single", "complete", "average", "ward"]
)

cmap = "Viridis Reverse"
# cmap = st.sidebar.selectbox(
#     label="Select the color scheme used by the clustered heatmap",
#     options=[
#         "Viridis Reverse", 
#         "Viridis",  
#         "Rocket Reverse",
#         "Rocket",  
#         "Magma Reverse",
#         "Magma",
#         ]
# )

# msg = """
# Read more about color palettes 
# [here](https://seaborn.pydata.org/tutorial/color_palettes.html).
# """
# st.sidebar.write(msg)

fig, ax = clustermap(pairwise_zeros, linkage_method, cmap)
fig, ax = load_clustermap(cmap)
st.pyplot(fig)

st.header("Perceived Differences")
msg = """
How do your perceptions differ from others' perctions of you? Below, explore 
differing levels of overal connectedness and also mismatches between how 
people rated others and how others rated them.
"""
st.write(msg)
differences, vega_df, spec = vega_grouped_bar_chart(pairwise_zeros)
st.vega_lite_chart(vega_df, spec)

fig, ax = delta_plot(pairwise_zeros)
st.pyplot(fig)

# threshold = 5
# threshold = st.sidebar.slider("Threshold for Noticeable Difference", 
#     min_value=0, 
#     max_value=10,
#     value=5)


# noticeable = differences[abs(differences["Difference"]) >= threshold]
# st.dataframe(noticeable)
# st.dataframe(differences)

# name = st.selectbox("Please chooose your name.", differences.index.tolist())
# individual = differences.loc[name]

# if abs(individual["Difference"]) < threshold:
#     msg = f"""
#     {name}, your perception of your connectedness is not noticeably different 
#     than that of your collegues.
#     """
# elif individual["Difference"] >= threshold:
#     msg = f"""
#     {name}, you rated that you feel more connected to your collegues than 
#     they did to you.
#     """
# else:
#     msg = f"""
#     {name}, your collegues feel more connected to you than you do to them.
#     """

# st.write(msg)


st.header("Explore the Connections Among Your Team")
msg = """
This graph is based on the average ratings between two people. To keep the 
graph readable, we've only inluded mutual connections that averaged to a score 
of at least 6.
"""
st.write(msg)
st.image("src/connectedness/data/graphcommons/moon_network_graph_6.png")