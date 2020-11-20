import json
import pickle
import pprint
from copy import copy
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st


@st.cache
def load_saved_survey_results():
    filepath = Path("src/connectedness/data/")
    df_nan = pd.read_pickle(filepath / Path("Moon_Connectedness_nan.pkl"))
    df_zeros = pd.read_pickle(filepath / Path("Moon_Connectedness_zeros.pkl"))
    free_response = pd.read_pickle(filepath / Path("Moon_free_responses.pkl"))
    return df_nan, df_zeros, free_response


def load_mitsui_names_and_emails():
    filepath = Path("src/connectedness/data/")
    # filepath = Path("../src/connectedness/data/")
    filename = Path("WorkX Member Names and Emails.csv")
    df = pd.read_csv(filepath / filename).set_index("Mail Address")

    df["Name (JP)"] = df["Family Name"] + df["First Name"]
    df["Name (EN)"] = df["Name (EN)"].apply(lambda n: n.replace(",", ", "))
    
    emails = copy(df[["Name (EN)"]])
    emails["Name (EN)"] = emails["Name (EN)"].apply(
        lambda n: n.replace(",", ""))
    emails.reset_index(inplace=True)
    emails["Mail Address"] = emails["Mail Address"].apply(lambda e: e.lower())
    
    emails.set_index("Name (EN)", inplace=True)

    return df, emails


def load_moon_names_and_emails():
    filepath = Path("src/connectedness/data/")
    # filepath = Path("../src/connectedness/data/")
    filename = Path("Moon Member Names and Emails.csv")
    df = pd.read_csv(filepath / filename).set_index("Email")

    # df["Name (JP)"] = df["Family Name"] + df["First Name"]
    # df["Name (EN)"] = df["Name (EN)"].apply(lambda n: n.replace(",", ", "))
    
    # emails = copy(df[["Name"]])
    # emails["Name"] = emails["Name"].apply(
    #     lambda n: n.replace(",", ""))
    # emails.reset_index(inplace=True)
    # emails["Email"] = emails["Email"].apply(lambda e: e.lower())
    
    # emails.set_index("Name", inplace=True)

    # return df, emails
    email_to_names = df.to_dict(orient="index")
    names_to_emails = df.set_index("Name").to_dict(orient="index")
    return email_to_names, names_to_emails


def parse_moon_survey_results():
    filepath = Path("src/connectedness/data/")
    filename = Path("Tsunagi Survey for Moon Lab Responses.csv")

    columns_to_drop = ["Timestamp"]
    df = pd.read_csv(filepath / filename).drop(columns=columns_to_drop)
    df["Email Address"] = df["Email Address"].apply(lambda e: e.lower())
    df.set_index("Email Address", inplace=True)
    # df.dropna(axis=1, how="all", inplace=True)

    # What does connectedness mean to you?
    free_rsp_col = [col for col in df.columns if "what makes you fe" in col][0]
    free_response = df[[free_rsp_col]]
    df.drop(columns=[free_rsp_col], inplace=True)

    # Rename columns from long questions to just names.
    df.rename(columns={col: col.split("feel with ")[1] \
            .replace("?", "").strip() for col in df.columns},
            inplace=True)

    email_to_name, _ = load_moon_names_and_emails()
    # Everyone filled out the survey. No need to check.

    # Change index from email to names
    df.reset_index(inplace=True)
    df["Name"] = df["Email Address"].apply(lambda e: email_to_name[e]["Name"])
    df.set_index("Name", inplace=True)
    df.drop(columns=["Email Address"], inplace=True)

    free_response.reset_index(inplace=True)
    free_response["Name"] = free_response["Email Address"].apply(lambda e: email_to_name[e]["Name"])
    free_response.set_index("Name", inplace=True)
    free_response.drop(columns=["Email Address"], inplace=True)
    print(free_response)
   
    # Make it triangular
    df = df[df.index.tolist()]
    
    # Fill diagonal
    np.fill_diagonal(df.values, -1)
    df_zeros = df.replace(-1, 0)
    df_nan = df.replace(-1, np.nan)

    # save the parsed data
    df_nan.to_pickle(filepath / Path("Moon_Connectedness_nan.pkl"))
    df_zeros.to_pickle(filepath / Path("Moon_Connectedness_zeros.pkl"))
    free_response.to_pickle(filepath / Path("Moon_free_responses.pkl"))
    # return df, free_response


def parse_mitsui_survey_results():
    filepath = Path("src/connectedness/data/")
    # filepath = Path("../src/connectedness/data/")
    filename = Path("つなぎ – Connectedness Survey Results - 10-12-2020.csv")
    
    columns_to_drop = [
        "Timestamp", 
        "What is your name?",
        "How strong is your connection to Onogawa, Takashi?"
    ]
    
    df = pd.read_csv(filepath / filename).drop(columns=columns_to_drop)
    df["Email Address"] = df["Email Address"].apply(lambda e: e.lower())
    df.set_index("Email Address", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)

    free_rsp_col = [col for col in df.columns if "what makes you fe" in col][0]
    free_response = df[[free_rsp_col]]
    df.drop(columns=[free_rsp_col], inplace=True)

    df.rename(columns={col: col.split("connection to ")[1] \
            .replace(" last week?)", "") for col in df.columns},
            inplace=True)

    _, emails = load_mitsui_names_and_emails()
    names_to_emails = emails.to_dict(orient="index")

    df.rename(columns={
        name: names_to_emails[name]["Mail Address"] for name in df.columns
    }, inplace=True)

    # Only return columns if those people filled out the survey
    df = df[df.index.tolist()]

    # replace with names in romaji
    emails.reset_index(inplace=True)
    emails.set_index("Mail Address", inplace=True)
    email_to_name = emails.to_dict(orient="index")
    email_to_name = {k:v["Name (EN)"] for k,v in email_to_name.items()}

    df.reset_index(inplace=True)
    df["Email Address"] = df["Email Address"].apply(lambda e: email_to_name[e])
    df.rename(columns={"Email Address": "Name"}, inplace=True)
    df.rename(columns=email_to_name, inplace=True)
    df.set_index("Name", inplace=True)

    free_response.reset_index(inplace=True)
    free_response["Email Address"] = free_response["Email Address"].apply(lambda e: email_to_name[e])
    free_response.rename(columns={"Email Address": "Name"}, inplace=True)
    free_response.set_index("Name", inplace=True)


    # Fill diagonal
    np.fill_diagonal(df.values, -1)
    df_zeros = df.replace(-1, 0)
    df_nan = df.replace(-1, np.nan)

    # save the parsed data
    df_nan.to_pickle(filepath / Path("WorkX_Connectedness_nan.pkl"))
    df_zeros.to_pickle(filepath / Path("WorkX_Connectedness_zeros.pkl"))
    free_response.to_pickle(filepath / Path("WorkX_free_responses.pkl"))
    # return df, free_response


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

    columns = copy(df.columns.tolist())

    for ind in pairwise_df.index.tolist():
        node_data.append({
                    "Type":         "Person",
                    "Name":         ind,
                    "Description":  "tktk",
                    "Image":        "tktk",
                    "Reference":    "tktk",
                })

        for col in columns:
            if ind != col:
                weight = pairwise_df.loc[ind][col] + pairwise_df.loc[col][ind]
                weight = weight/2

                if weight >= min_link_strength:
                    edge_data.append({
                        "From Type":    "Person",
                        "From Name":    ind,
                        "Edge":         "Rated",
                        "To Type":      "Person",
                        "To Name":      col,
                        "Weight":       int(weight), #graphcommons rejects floats
                    })

        columns.remove(ind)

    filepath = Path("src/connectedness/data/graphcommons")
    graphcommons_edges = pd.DataFrame(edge_data, columns=edge_columns)
    graphcommons_edges.to_csv(filepath / Path(f"graphcommons_moon_edges_{min_link_strength}.csv"), index=False)
    graphcommons_nodes = pd.DataFrame(node_data, columns=node_columns)
    graphcommons_nodes.to_csv(filepath / Path("graphcommons_moon_nodes.csv"), index=False)


if __name__ == "__main__":
    # parse_moon_survey_results()
    _, df, _ = load_saved_survey_results()
    make_graphcommons_csv(df, min_link_strength=4)
    make_graphcommons_csv(df, min_link_strength=6)
    make_graphcommons_csv(df, min_link_strength=8)