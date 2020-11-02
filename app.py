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
df, spec = vega_grouped_bar_chart(pairwise_df)
st.vega_lite_chart(df, spec)


st.header("Explore the Connections Among Your Team")
observers = observable("Force Graph",
    notebook="@gambingo/force-directed-graph",
    targets=["chart"],
    observe=["data"])

force_graph = observers.get("data")