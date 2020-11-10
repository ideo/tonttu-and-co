from pathlib import Path
import pprint
import json

import pandas as pd
import streamlit as st


def load_mitsui_names_and_emails():
    # filepath = Path("src/connectedness/data/")
    filepath = Path("../src/connectedness/data/")
    filename = Path("WorkX Member Names and Emails.csv")
    df = pd.read_csv(filepath / filename).set_index("Mail Address")

    df["Name (JP)"] = df["Family Name"] + df["First Name"]
    df["Name (EN)"] = df["Name (EN)"].apply(lambda n: n.replace(",", ", "))
    
    name_to_email = df[["Name (EN)"]]
    name_to_email["Name (EN)"] = name_to_email["Name (EN)"].apply(
        lambda n: n.replace(",", ""))
    name_to_email.reset_index(inplace=True)
    name_to_email.set_index("Name (EN)", inplace=True)

    return df, name_to_email.to_dict(orient="index")


def parse_mitsui_survey_results():
    # filepath = Path("src/connectedness/data/")
    filepath = Path("../src/connectedness/data/")
    filename = Path("つなぎ – Connectedness Survey Results - 10-10-2020.csv")
    
    columns_to_drop = [
        "Timestamp", 
        "What is your name?",
        "How strong is your connection to Onogawa, Takashi?"
    ]
    
    df = pd.read_csv(filepath / filename).drop(columns=columns_to_drop)
    df.set_index("Email Address", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)

    free_rsp_col = [col for col in df.columns if "what makes you fe" in col][0]
    free_response = df[[free_rsp_col]]
    df.drop(columns=[free_rsp_col], inplace=True)

    df.rename(columns={col: col.split("connection to ")[1] \
            .replace(" last week?)", "") for col in df.columns},
            inplace=True)

    _, names_to_emails = load_mitsui_names_and_emails()

    df.rename(columns={
        name: names_to_emails[name]["Mail Address"] for name in df.columns
    }, inplace=True)

    # for col in df.columns:
    #     print(col)
    
    
    # df["sort_by"] = df["What is your name?"].apply(lambda n: name_order[n])
    # df.set_index("What is your name?", inplace=True)
    # df.sort_values(axis=0, by="sort_by", inplace=True)
    # df.drop(columns=["sort_by"], inplace=True)
    # return df
    return df, free_response


# @st.cache
def load_tsunagi_team_data():
    filename = Path("src/connectedness/data/tsunagi_data.csv")
    # filename = Path("../src/connectedness/data/tsunagi_data.csv")

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
    # df_nan, df_zeros = load_data()
    # make_network_graph_json(df, min_link_strength=8)
    # make_graphcommons_csv(df_nan)

    # pp = pprint.PrettyPrinter(indent=4)
    # pp.pprint(data)
    parse_mitsui_survey_results()