from pathlib import Path
import pprint
import json

import pandas as pd
import streamlit as st


# def load_data():
#     filename = Path("connectedness/dummy_data.csv")
#     df = pd.read_csv(filename).drop(columns=["Timestamp"])
    
#     name_order = {
#         "PERSON1":  1, 
#         "PERSON2":  2,
#         "PERSON3":  3,
#         "PERSON4":  4,
#         "PERSON5":  5,
#         "PERSON6":  6,
#         "PERSON7":  7,
#         "PERSON8":  8,
#         "PERSON9":  9,
#         "PERSON10": 10,
#     }

#     df["sort_by"] = df["What is your name?"].apply(lambda n: name_order[n])
#     df.set_index("What is your name?", inplace=True)
#     df.sort_values(axis=0, by="sort_by", inplace=True)
#     df.drop(columns=["sort_by"], inplace=True)
#     return df


# @st.cache
def load_data():
    filename = Path("src/connectedness/tsunagi_data.csv")
    # filename = Path("../src/connectedness/tsunagi_data.csv")

    df = pd.read_csv(filename)
    df.rename(columns={"Unnamed: 0": ""}, inplace=True)
    df.set_index("", inplace=True)

    df.sort_index(inplace=True)
    alphabetized_cols = sorted(df.columns)
    df_nan = df[alphabetized_cols]
    df_zeros = df.fillna(value=0)

    return df_nan, df_zeros


def make_network_graph_json(pairwise_df, min_link_strength=0):
    nodes = [{"id": name, "group": 1} for name in pairwise_df.index.tolist()]
    
    links = []
    for ind in pairwise_df.index.tolist():
        for col in pairwise_df.columns:
            if ind != col:
                links.append({
                    "source":   ind,
                    "target":   col,
                    "value":    pairwise_df.loc[ind][col] + pairwise_df.loc[col][ind]
                })

    links = [l for l in links if l["value"] >= min_link_strength]

    data = {"nodes": nodes, "links": links}
    with open("connectedness/connectedness.json", "w") as outfile:  
        json.dump(data, outfile) 

    # return data


def make_graphcommons_csv(pairwise_df, min_link_strength=0):
    edge_columns = [
        "From Type",
        "From Name",
        "Edge",
    	"To Type",
        "To Name",
        "Weight"
    ]
    edge_data = []

    node_columns = [
        "Type",
        "Name",
        "Description",
        "Image",
        "Reference",
    ]
    node_data = []

    for ind in pairwise_df.index.tolist():
        node_data.append({
                    "Type":         "Person",
                    "Name":         ind,
                    "Description":  "tktk",
                    "Image":        "tktk",
                    "Reference":    "tktk",
                })

        for col in pairwise_df.columns:
            if ind != col:
                edge_data.append({
                    "From Type":    "Person",
                    "From Name":    ind,
                    "Edge":         "Rated",
                    "To Type":      "Person",
                    "To Name":      col,
                    "Weight":       int(pairwise_df.loc[ind][col]), #graphcommons rejects floats
                })

    filepath = Path("src/connectedness/graphcommons")
    graphcommons_edges = pd.DataFrame(edge_data, columns=edge_columns)
    graphcommons_edges.to_csv(filepath / Path("graphcommons_edges.csv"), index=False)
    graphcommons_nodes = pd.DataFrame(node_data, columns=node_columns)
    graphcommons_nodes.to_csv(filepath / Path("graphcommons_nodes.csv"), index=False)


if __name__ == "__main__":
    df_nan, df_zeros = load_data()
    # make_network_graph_json(df, min_link_strength=8)
    make_graphcommons_csv(df_nan)

    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(data)