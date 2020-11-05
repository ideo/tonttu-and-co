from copy import copy

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns

from . import load_data
# from parse_survey_respones import load_data


sns.set_theme()


def grouped_bar_chart():
    pairwise_df = load_data()

    # Transform data
    your_connectedness = pd.DataFrame(pairwise_df.sum(axis=1))
    connections_to_you = pd.DataFrame(pairwise_df.sum(axis=0))

    your_connectedness.rename(columns={0: "Your Perception"}, inplace=True)
    connections_to_you.rename(columns={0: "Others' Perception"}, inplace=True)
    df = your_connectedness.join(connections_to_you)

    fig, ax = plt.subplots()

    labels = df.index.tolist()
    yours = df["Your Perception"]
    to_you = df["Others' Perception"]

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    ax.bar(x - width/2, yours, width, label="Your Perception")
    ax.bar(x + width/2, to_you, width, label="Others' Perception")

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel("Sum of Ratings")
    ax.set_title("Perceived Differences")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    fig.tight_layout()

    return fig, ax


def delta_plot(pairwise_df):
    # Transform data
    your_connectedness = pd.DataFrame(pairwise_df.sum(axis=1))
    connections_to_you = pd.DataFrame(pairwise_df.sum(axis=0))

    your_connectedness.rename(columns={0: "Your Perception"}, inplace=True)
    connections_to_you.rename(columns={0: "Others' Perception"}, inplace=True)
    df = your_connectedness.join(connections_to_you)
    df["Delta"] = df["Your Perception"] - df["Others' Perception"]

    # Plot
    fig, ax = plt.subplots()
    names = df.index.tolist()
    deltas = [d if d != 0.0 else 0.1 for d in df.Delta.tolist()]
    y_pos = np.arange(len(names))

    ax.barh(y_pos, deltas, align="center")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names)
    ax.grid(False)
    ax.set_title("Difference Between Total Ratings By and For Each Person\n")
    ax.set_xlabel("\nHigher Ratings For You <–––––> Higher Ratings By You       ")
    plt.tight_layout()
    return fig, ax



# @st.cache
def heatmap(df):
    # Format plot
    values = []
    for ind in df.index.tolist():
        for col in df.columns:
            values.append({
                "Your Perception":      ind,
                "Others Perception":   col,
                "Rating":               df.loc[ind][col] 
                })

    vega_light_spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
        "mark": {"type": "rect", "strokeWidth": 2},
        "encoding": {
            "y": {
                "field": "Your Perception",
                "type": "nominal",
                "sort": None,
                },
            "x": {
                "field": "Others Perception",
                "type": "nominal",
                "sort": None,
                },
            "fill": {
                "field": "Rating",
                "type": "quantitative"
                },
        },
        "config": {
            "scale": {
                "bandPaddingInner": 0,
                "bandPaddingOuter": 0
                },
            "view": {"step": 40},
            "range": {"ramp": {"scheme": "yellowgreenblue"}},
            "axis": {"domain": False}
        },
    }

    # print(df, values)
    return values, vega_light_spec


# @st.cache
def vega_grouped_bar_chart(pairwise_df):
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
    
    spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
        "mark": "bar",
        "mark": "bar",
        "encoding": {
            "column": {
                "field": "Name", "type": "nominal", "spacing": 10,
                "title": "Differences in Perceived Connectedness",
            },
            "y": {
                "aggregate": "sum", "field": "Rating",
                "title": "Sum of All Ratings",
                "axis": {"grid": False}
            },
            "x": {
                "field": "Direction",
                "axis": {"title": ""}
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


# @st.cache
# def sorted_heatmap(pairwise_nan, row_index, col_index):
#     row_df = reorder_dataframe(pairwise_nan, row_index)
#     col_df = reorder_dataframe(pairwise_nan, col_index)

#     fig, ax = plt.subplots(1, 2)
#     ax[0] = sns.heatmap(row_df, ax=ax[0], cmap="mako")
#     ax[1] = sns.heatmap(col_df, ax=ax[1], cmap="mako")
#     return fig, ax


def sorted_heatmap(df, new_index):
    new_df = reorder_dataframe(df, new_index)

    fig, ax = plt.subplots()
    ax = sns.heatmap(new_df, ax=ax, cmap="mako")
    return fig, ax


if __name__ == "__main__":
    pairwise_df = load_data()
    clustergrid = clustermap(pairwise_df)
