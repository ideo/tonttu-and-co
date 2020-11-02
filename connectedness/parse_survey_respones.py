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


@st.cache
def load_data():
    filename = Path("connectedness/tsunagi_data.csv")
    df = pd.read_csv(filename)
    df.rename(columns={"Unnamed: 0": ""}, inplace=True)
    df.set_index("", inplace=True)

    df.sort_index(inplace=True)
    alphabetized_cols = sorted(df.columns)
    df = df[alphabetized_cols]
    return df


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



if __name__ == "__main__":
    df = load_data()
    make_network_graph_json(df, min_link_strength=8)

    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(data)