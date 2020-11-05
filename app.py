import streamlit as st
from streamlit_observable import observable
# from streamlit_vega_lite import vega_lite_component
import matplotlib.pyplot as plt
import seaborn as sns

from connectedness import (load_data, heatmap, vega_grouped_bar_chart, 
    clustermap, sorted_heatmap, delta_plot)


st.title("Tsunagi Connectedness Survey")
msg = """
This survey is an attempt to allow you to easily check your teams' level of 
connectedness. Periodically, your team can take the simple survey you filled 
out. Then, here, you can explore the results and discuss.

First, here are the raw numbers from the survey.
"""
st.write(msg)

pairwise_nan, pairwise_zeros = load_data()
st.table(pairwise_nan)

msg = """
Below, explore the natural groups that have formed within your team. Darker 
colors represent more closely connected people. **UPDATE**
"""
st.write(msg)


msg = """
Hey, Team! Play with the settings for this prototype here. We can pick what 
we like and then disable this sidebar when we deliver it to WorkX.
"""
st.sidebar.write(msg)

linkage_method = st.sidebar.selectbox(
    label="Select the sorting method used by the clustered heatmap",
    options=["single", "complete", "average", "ward"]
)

cmap = st.sidebar.selectbox(
    label="Select the color scheme used by the clustered heatmap",
    options=[
        "Viridis", 
        "Viridis Reverse", 
        "Rocket", 
        "Rocket Reverse", 
        "Magma", 
        "Magma Reverse"
        ]
)

msg = """
Read more about color palettes 
[here](https://seaborn.pydata.org/tutorial/color_palettes.html).
"""
st.sidebar.write(msg)

clustergrid = clustermap(pairwise_zeros, linkage_method, cmap)
st.pyplot(clustergrid)

st.header("Perceived Differences")
st.write("How do your perceptions differ from others' perctions of you?")
differences, vega_df, spec = vega_grouped_bar_chart(pairwise_nan)
st.vega_lite_chart(vega_df, spec)

fig, ax = delta_plot(pairwise_nan)
st.pyplot(fig)


threshold = 5
# threshold = st.sidebar.slider("Threshold for Noticeable Difference", 
#     min_value=0, 
#     max_value=10,
#     value=5)


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