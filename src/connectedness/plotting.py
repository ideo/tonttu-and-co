from copy import copy
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns

from . import load_tsunagi_team_data
# from parse_survey_respones import load_tsunagi_team_data


sns.set_theme()


# def grouped_bar_chart():
#     pairwise_df, _ = load_tsunagi_team_data()

#     # Transform data
#     your_connectedness = pd.DataFrame(pairwise_df.sum(axis=1))
#     connections_to_you = pd.DataFrame(pairwise_df.sum(axis=0))

#     your_connectedness.rename(columns={0: "Your Perception"}, inplace=True)
#     connections_to_you.rename(columns={0: "Others' Perception"}, inplace=True)
#     df = your_connectedness.join(connections_to_you)

#     fig, ax = plt.subplots()

#     labels = df.index.tolist()
#     yours = df["Your Perception"]
#     to_you = df["Others' Perception"]

#     x = np.arange(len(labels))  # the label locations
#     width = 0.35  # the width of the bars

#     fig, ax = plt.subplots()
#     ax.bar(x - width/2, yours, width, label="Your Perception")
#     ax.bar(x + width/2, to_you, width, label="Others' Perception")

#     # Add some text for labels, title and custom x-axis tick labels, etc.
#     ax.set_ylabel("Sum of Ratings")
#     ax.set_title("Perceived Differences")
#     ax.set_xticks(x)
#     ax.set_xticklabels(labels)
#     ax.legend()
#     fig.tight_layout()

#     return fig, ax


# Do not cache this function. Seems to crash streamlit
def delta_plot(pairwise_df, question=None):
    # Transform data
    your_connectedness = pd.DataFrame(pairwise_df.sum(axis=1))
    connections_to_you = pd.DataFrame(pairwise_df.sum(axis=0))

    your_connectedness.rename(columns={0: "Your Perception"}, inplace=True)
    connections_to_you.rename(columns={0: "Others' Perception"}, inplace=True)
    df = your_connectedness.join(connections_to_you)
    df["Delta"] = df["Your Perception"] - df["Others' Perception"]

    df.sort_values(by="Delta", inplace=True)

    # Plot
    fig, ax = plt.subplots()
    names = df.index.tolist()
    deltas = [d if d != 0.0 else 0.1 for d in df.Delta.tolist()]
    y_pos = np.arange(len(names))

    ax.barh(y_pos, deltas, align="center")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names)
    ax.grid(False)
    ttl = "Difference Between Total Ratings By and For Each Person\n"
    if question:
        ttl = f"{question}: {ttl}"
    ax.set_title(ttl)
    ax.set_xlabel("\nHigher Ratings For You <–––––> Higher Ratings By You       ")
    plt.tight_layout()
    return fig, ax


# @st.cache
def vega_grouped_bar_chart(pairwise_df, question=None):
    # pairwise_df = load_data()
    your_connectedness = pd.DataFrame(pairwise_df.sum(axis=1))
    connections_to_you = pd.DataFrame(pairwise_df.sum(axis=0))

    your_connectedness.rename(columns={0: "Rating"}, inplace=True)
    connections_to_you.rename(columns={0: "Rating"}, inplace=True)

    yours = your_connectedness.reset_index().rename(columns={"": "Name"})
    others = connections_to_you.reset_index().rename(columns={"index": "Name"})

    useful_df = yours.rename(columns={"Rating": "Your Perception"}).set_index("Name").join(
        others.rename(columns={"Rating": "Others' Perception"}).set_index("Name")
    )
    useful_df["Difference"] = useful_df["Your Perception"] - useful_df["Others' Perception"]

    yours["Direction"] = pd.Series(["Your Ratings of Others"]*yours.shape[0])
    others["Direction"] = pd.Series(["Others' Ratings of You"]*others.shape[0])
    vega_df = yours.append(others, ignore_index=True)

    vega_df["Name"] = vega_df["Name"].apply(lambda n: n.split(" ")[-1])
    # print(vega_df)

    ttl = "Differences in Perceived Connectedness"
    if question:
        ttl = f"{question}: {ttl}"
    
    spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
        "mark": "bar",
        "encoding": {
            # "text": {"angle": -45},
            "column": {
                "field": "Name", "type": "nominal", "spacing": 10, "angle": -45,
                "title": ttl,
            },
            "y": {
                "aggregate": "sum", "field": "Rating",
                "title": "Sum of All Ratings",
                "axis": {"grid": False},
            },
            "x": {
                "field": "Direction",
                "axis": {"title": ""},
            },
            "color": {
                "field": "Direction",
                "scale": {"range": ["#675193", "#ca8861"]}
            }
        },
        "config": {
            "view": {"stroke": "transparent"},
            "axis": {"domainWidth": 1},
        }
    }

    return useful_df, vega_df, spec


def vega_grouped_bar_chart_comparison(df1, df2, question=None):
    # Round 1
    your_connectedness1 = pd.DataFrame(df1.sum(axis=1))
    connections_to_you1 = pd.DataFrame(df1.sum(axis=0))

    your_connectedness1.rename(columns={0: "Rating"}, inplace=True)
    connections_to_you1.rename(columns={0: "Rating"}, inplace=True)

    your_connectedness1.index = [f"{n} (Round 1)" for n in your_connectedness1.index]
    connections_to_you1.index = [f"{n} (Round 1)" for n in connections_to_you1.index]

    yours1 = your_connectedness1.reset_index().rename(columns={"": "Name"})
    others1 = connections_to_you1.reset_index().rename(columns={"index": "Name"})

    # Round 2
    your_connectedness2 = pd.DataFrame(df2.sum(axis=1))
    connections_to_you2 = pd.DataFrame(df2.sum(axis=0))

    your_connectedness2.rename(columns={0: "Rating"}, inplace=True)
    connections_to_you2.rename(columns={0: "Rating"}, inplace=True)

    your_connectedness2.index = [f"{n} (Round 2)" for n in your_connectedness2.index]
    connections_to_you2.index = [f"{n} (Round 2)" for n in connections_to_you2.index]

    yours2 = your_connectedness2.reset_index().rename(columns={"": "Name"})
    others2 = connections_to_you2.reset_index().rename(columns={"index": "Name"})

    # print(yours1)
    # print(yours2)

    yours = yours1.append(yours2)
    others = others1.append(others2)

    yours.rename(columns={"index": "Name"}, inplace=True)

    # print(yours)
    # print(others)

    useful_df = yours.rename(columns={"Rating": "Your Perception"}).set_index("Name").join(
        others.rename(columns={"Rating": "Others' Perception"}).set_index("Name")
    )
    # useful_df["Difference"] = useful_df["Your Perception"] - useful_df["Others' Perception"]

    print("useful_df")
    print(useful_df)

    yours["Direction"] = pd.Series(["Your Ratings of Others"]*yours.shape[0])
    others["Direction"] = pd.Series(["Others' Ratings of You"]*others.shape[0])
    vega_df = yours.append(others, ignore_index=True)

    vega_df["Name"] = vega_df["Name"].apply(lambda n: f"{n.split(' ')[0]} {n.split(' ')[-1][-2]}")
    print(vega_df)
    print("vega_df")

    ttl = "Differences in Perceived Connectedness"
    if question:
        ttl = f"{question}: {ttl}"
    
    spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
        "mark": "bar",
        "encoding": {
            # "text": {"angle": -45},
            "column": {
                "field": "Name", "type": "nominal", "spacing": 10, "angle": -45,
                "title": ttl,
            },
            "y": {
                "aggregate": "sum", "field": "Rating",
                "title": "Sum of All Ratings",
                "axis": {"grid": False},
            },
            "x": {
                "field": "Direction",
                "axis": {"title": ""},
            },
            "color": {
                "field": "Direction",
                "scale": {"range": ["#675193", "#ca8861"]}
            }
        },
        "config": {
            "view": {"stroke": "transparent"},
            "axis": {"domainWidth": 1},
        }
    }

    return useful_df, vega_df, spec



# Do not cache this function. Seems to crash streamlit
def clustermap(pairwise_df, linkage_method, cmap):
    # fig, ax = plt.subplots()    
    clustergrid = sns.clustermap(
        pairwise_df, 
        method=linkage_method,    # linkage
        metric="euclidean",
    )

    row_index = clustergrid.dendrogram_row.reordered_ind
    col_index = clustergrid.dendrogram_col.reordered_ind
    new_df = reorder_dataframe(pairwise_df, row_index, col_index)
    
    filepath = Path("src/connectedness/data/")
    new_df.to_pickle(filepath / Path("clustered_df.pkl"))

    fig, ax = plt.subplots()
    ax = sns.heatmap(new_df, 
        ax=ax,
        cmap=cmap.lower().replace(" reverse", "_r")
    )
    ax.set_title("Explore the Natural Groupings in Your Team\n")
    plt.yticks(rotation=0)
    return fig, ax


# Don't cache this is fucks shit up
def load_clustermap(cmap):
    filepath = Path("src/connectedness/data/")
    new_df = pd.read_pickle(filepath / Path("clustered_df.pkl"))

    fig, ax = plt.subplots()
    ax = sns.heatmap(new_df, 
        ax=ax,
        cmap=cmap.lower().replace(" reverse", "_r")
    )
    ax.set_title("Explore the Natural Groupings in Your Team\n")
    plt.yticks(rotation=0)
    return fig, ax


def reorder_dataframe(df, row_index, col_index):
    # Reorder from clustering
    curr_positions = {pos:name for pos, name in enumerate(df.index)}
    new_row_index = [curr_positions[i] for i in row_index]

    curr_positions = {pos:name for pos, name in enumerate(df.columns)}
    new_col_index = [curr_positions[i] for i in col_index]

    new_df = pd.DataFrame(data=df, index=new_row_index, columns=new_col_index)
    return new_df


if __name__ == "__main__":
    pairwise_df = load_data()
    clustergrid = clustermap(pairwise_df)
    pass
