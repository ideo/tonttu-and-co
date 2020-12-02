import streamlit as st
# from streamlit_observable import observable
# from streamlit_vega_lite import vega_lite_component
import matplotlib.pyplot as plt
import seaborn as sns

from src.connectedness import load_saved_survey_results
from src.connectedness import load_tsunagi_team_data, vega_grouped_bar_chart 
from src.connectedness import clustermap, delta_plot, load_clustermap
from src.connectedness import vega_grouped_bar_chart_comparison


st.title("Tsunagi Connectedness Survey: Round 2!")
# st.subheader("First Survey")
# msg = """
# First, here are the raw numbers from the first survey.
# """
# st.write(msg)

# pairwise_nan, pairwise_zeros = load_tsunagi_team_data()
# pairwise_nan, pairwise_zeros, free_responses = load_saved_survey_results()
df1_nan, df1_zeros, free_response1, dfA_nan, dfA_zeros, dfB_nan, dfB_zeros, free_response2 = load_saved_survey_results()
# st.dataframe(df1_nan)

# fig, ax = plt.subplots()
# sns.heatmap(df1_zeros, cmap="viridis_r")
# ax.set_ylabel("Ratings given by\n")
# ax.set_xlabel("\nRatings given to")
# st.pyplot(fig)


# st.subheader("Second Survey")
msg = """
First, here are the raw numbers from the second survey. They second survey as 
two versions of each question. We'll refer to them as Question A and Question B.
"""
st.write(msg)
st.subheader("Question A")
question = """
Example:  
小野川さん：11月17日(オフサイト実施日)から今日までを振り返って、あなたとのつながり度合いはどれくらいですか。前回のあなたの定義をもとに答えてください。 (How close was your connection since the offsite?...Onogawa-san)
"""
st.write(question)
st.dataframe(dfA_nan)
fig, ax = plt.subplots()
sns.heatmap(dfA_zeros, cmap="viridis_r")
ax.set_ylabel("Ratings given by\n")
ax.set_xlabel("\nRatings given to")
st.pyplot(fig)


st.subheader("Question B")
question = """
Example:  
先週1週間を振り返り、小野川さんが感じている業務上の課題をどれくらい把握できていると感じますか？
"""
st.write(question)
st.dataframe(dfB_nan)
fig, ax = plt.subplots()
sns.heatmap(dfB_zeros, cmap="viridis_r")
ax.set_ylabel("Ratings given by\n")
ax.set_xlabel("\nRatings given to")
st.pyplot(fig)


st.header("What does Connectedness mean to you?")
msg = """
The survey asked each person to describe what connectedness meant to them. 
Here are those responses from each round.
"""
st.write(msg)
# st.table(free_responses.reset_index().drop(columns=["Email Address"]))
# st.table(free_response2)
st.table(free_response1.join(free_response2))


# st.header("Perceived Differences")
# msg = """
# How do your perceptions differ from others' perctions of you? Below, explore 
# differing levels of overal connectedness and also mismatches between how 
# people rated others and how others rated them.
# """
st.header("Total Ratings")
msg = """
Here you can see the cummulative ratings for each person, the sums of their 
ratings for people and peoples' ratings for them. You can also see the changes 
from round 1 to round 2.
"""
st.write(msg)

differences, vega_df, spec, ttl = vega_grouped_bar_chart_comparison(df1_zeros, dfA_zeros, question="Question A, Comparison to Previous Survey")
st.subheader(ttl)
st.vega_lite_chart(vega_df, spec)

# differences, vega_df, spec = vega_grouped_bar_chart(dfA_zeros, question="Question A")
# st.vega_lite_chart(vega_df, spec)
# fig, ax = delta_plot(dfA_zeros, question="Question A")
# st.pyplot(fig)

differences, vega_df, spec, ttl = vega_grouped_bar_chart(dfA_zeros, question="Question B")
st.subheader(ttl)
st.vega_lite_chart(vega_df, spec)
# fig, ax = delta_plot(dfA_zeros, question="Question B")
# st.pyplot(fig)






st.header("Explore the Connections Among Your Team")
msg = """
This graph is based on the average ratings between two people. To keep the 
graph readable, we've only inluded mutual connections that averaged to a *score 
of at least 6*. The numbers beneath each name indicate the team that person 
belongs to.
# """
st.write(msg)
st.subheader("Question A")
st.image("src/connectedness/data/graphcommons/workX_questionA_network_graph_6.png")

st.subheader("Question B")

st.image("src/connectedness/data/graphcommons/workX_questionB_network_graph_6.png")

# msg = """
# Perhaps this network is more clear if we only visualize strong connnections. 
# This network only inludes mutual connections that averaged to a *score 
# of at least 8*.
# """
# st.write(msg)
# st.image("src/connectedness/data/graphcommons/moon_network_graph_8.png")


# st.header("Groups")
# msg = """
# Below is an attempt explore the natural groups that form within your team. 
# Darker colors represent more closely connected people. Your team may be too 
# interconneted for clear groups to be visible.
# """
# st.write(msg)

# msg = """
# Hey, Team! Play with the settings for this prototype here. We can pick what 
# we like and then disable this sidebar when we deliver it to WorkX.
# """
# st.sidebar.write(msg)

# linkage_method = "single"
# linkage_method = st.sidebar.selectbox(
#     label="Select the sorting method used by the clustered heatmap",
#     options=["single", "complete", "average", "ward"]
# )

# cmap = "Viridis Reverse"
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

# fig, ax = clustermap(pairwise_zeros, linkage_method, cmap)
# fig, ax = load_clustermap(cmap)
# st.pyplot(fig)



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