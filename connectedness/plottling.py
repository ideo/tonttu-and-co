import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from . import load_data
# from parse_survey_respones import load_data


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


@st.cache
def heatmap(pairwise_df):
    values = []
    for ind in pairwise_df.index.tolist():
        for col in pairwise_df.columns:
            values.append({
                "Your Perception":      ind,
                "Others Perception":   col,
                "Rating":               pairwise_df.loc[ind][col] 
                })

    vega_light_spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
        "mark": {"type": "rect", "strokeWidth": 2},
        "encoding": {
            "y": {
                "field": "Your Perception",
                "type": "nominal",
                # "sort": None,
                },
            "x": {
                "field": "Others Perception",
                "type": "nominal",
                # "sort": None,
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

    # print(pairwise_df, values)
    return values, vega_light_spec


@st.cache
def vega_grouped_bar_chart(pairwise_df):
    # pairwise_df = load_data()
    your_connectedness = pd.DataFrame(pairwise_df.sum(axis=1))
    connections_to_you = pd.DataFrame(pairwise_df.sum(axis=0))

    your_connectedness.rename(columns={0: "Rating"}, inplace=True)
    connections_to_you.rename(columns={0: "Rating"}, inplace=True)

    yours = your_connectedness.reset_index().rename(columns={"": "Name"})
    others = connections_to_you.reset_index().rename(columns={"index": "Name"})

    yours["Direction"] = pd.Series(["Your Ratings of Others"]*yours.shape[0])
    others["Direction"] = pd.Series(["Others' Ratings of You"]*others.shape[0])
    df = yours.append(others, ignore_index=True)
    
    spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v4.json",
        "mark": "bar",
        "mark": "bar",
        "encoding": {
            "column": {
                "field": "Name", "type": "nominal", "spacing": 10,
                "title": "How Do Your Perceptions Differ From Others' Perception of You?",
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

    return df, spec


if __name__ == "__main__":
    df, spec = vega_grouped_bar_chart()