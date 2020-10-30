import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from . import load_data
# from parse_survey_respones import load_data


from vega_datasets import data


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


if __name__ == "__main__":
    # grouped_bar_chart()
    source = data.barley()
    print(source)