import json
import pickle
import pprint
from copy import copy
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st


# @st.cache
def load_saved_survey_results():
    filepath = Path("src/connectedness/data/")
    # df_nan = pd.read_pickle(filepath / Path("Moon_Connectedness_nan.pkl"))
    # df_zeros = pd.read_pickle(filepath / Path("Moon_Connectedness_zeros.pkl"))
    # free_response = pd.read_pickle(filepath / Path("Moon_free_responses.pkl"))

    df1_nan = pd.read_pickle(filepath / Path("WorkX_Connectedness_nan.pkl"))
    df1_zeros = pd.read_pickle(filepath / Path("WorkX_Connectedness_zeros.pkl"))
    free_response1 = pd.read_pickle(filepath / Path("WorkX_free_responses_round1.pkl"))

    dfA_nan = pd.read_pickle(filepath / Path("A_WorkX_Connectedness_nan.pkl"))
    dfA_zeros = pd.read_pickle(filepath / Path("A_WorkX_Connectedness_zeros.pkl"))
    dfB_nan = pd.read_pickle(filepath / Path("B_WorkX_Connectedness_nan.pkl"))
    dfB_zeros = pd.read_pickle(filepath / Path("B_WorkX_Connectedness_zeros.pkl"))
    free_response2 = pd.read_pickle(filepath / Path("WorkX_free_responses_round2.pkl"))

    # Only people who filled out both surveys.
    peeps = list(set(df1_nan.columns).intersection(set(dfA_nan.columns)))

    df1_nan.drop(index=[n for n in df1_nan.index.tolist() if n not in peeps], inplace=True)
    df1_nan = df1_nan[peeps]

    df1_zeros.drop(index=[n for n in df1_zeros.index.tolist() if n not in peeps], inplace=True)
    df1_zeros = df1_zeros[peeps]

    free_response1.drop(index=[n for n in free_response1.index.tolist() if n not in peeps], inplace=True)

    return df1_nan, df1_zeros, free_response1, dfA_nan, dfA_zeros, dfB_nan, dfB_zeros, free_response2


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


def parse_second_mitsui_survey_results():
    # filepath = Path("../src/connectedness/data/")
    filepath = Path("src/connectedness/data/")
    filename = Path("つなぎ 2nd – Connectedness Survey (Responses) - 12-1-2020.csv")

    renames = {
        "小野川さん：11月17日(オフサイト実施日)から今日までを振り返って、あなたとのつながり度合いはどれくらいですか。前回のあなたの定義をもとに答えてください。 (How close was your connection since the offsite?...Onogawa-san)": "Question A: Onogawa Takashi",
        "先週1週間を振り返り、小野川さんが感じている業務上の課題をどれくらい把握できていると感じますか？": "Question B: Onogawa Takashi",
        "峰岸将之さん：11月17日(オフサイト実施日)から今日までを振り返って、あなたとのつながり度合いはどれくらいですか。前回のあなたの定義をもとに答えてください。 (How close was your connection since the offsite?...Minegishi-san)": "Question A: Minegishi Masayuki",
        "先週1週間を振り返り、峰岸将之さんが感じている業務上の課題をどれくらい把握できていると感じますか？（How much do you think you acknowledge the issues around their job in the last week?）": "Question B: Minegishi Masayuki",
        "桑原崇さん：11月17日(オフサイト実施日)から今日までを振り返って、あなたとのつながり度合いはどれくらいですか。前回のあなたの定義をもとに答えてください。 (How close was your connection since the offsite?...Kuwabara-san": "Question A: Kuwabara Takashi",
        "先週1週間を振り返り、桑原崇さんが感じている業務上の課題をどれくらい把握できていると感じますか？（How much do you think you acknowledge the issues around their job in the last week?）": "Question B: Kuwabara Takashi",
        "来代なつきさん：11月17日(オフサイト実施日)から今日までを振り返って、あなたとのつながり度合いはどれくらいですか。前回のあなたの定義をもとに答えてください。 (How close was your connection since the offsite?...Kitashiro-san": "Question A: Kitashiro Natsuki",
        "先週1週間を振り返り、来代さんが感じている業務上の課題をどれくらい把握できていると感じますか？（How much do you think you acknowledge the issues around their job in the last week?）": "Question B: Kitashiro Natsuki",
        "藤田宙汰さん：11月17日(オフサイト実施日)から今日までを振り返って、あなたとのつながり度合いはどれくらいですか。前回のあなたの定義をもとに答えてください。 (How close was your connection since the offsite?...Fujita-san": "Question A: Fujita Yuta",
        "先週1週間を振り返り、藤田宙汰さんが感じている業務上の課題をどれくらい把握できていると感じますか？（How much do you think you acknowledge the issues around their job in the last week?）": "Question B: Fujita Yuta",
        "多和田容子さん：11月17日(オフサイト実施日)から今日までを振り返って、あなたとのつながり度合いはどれくらいですか。前回のあなたの定義をもとに答えてください。 (How close was your connection since the offsite?...Tawada-san)": "Question A: Tawada Yoko",
        "先週1週間を振り返り、多和田容子さんが感じている業務上の課題をどれくらい把握できていると感じますか？（How much do you think you acknowledge the issues around their job in the last week?）": "Question B: Tawada Yoko",
        "木村庸平さん：11月17日(オフサイト実施日)から今日までを振り返って、あなたとのつながり度合いはどれくらいですか。前回のあなたの定義をもとに答えてください。 (How close was your connection since the offsite?...Kimura-san)": "Question A: Kimura Yohei",
        "先週1週間を振り返り、木村庸平さんが感じている業務上の課題をどれくらい把握できていると感じますか？（How much do you think you acknowledge the issues around their job in the last week?）": "Question B: Kimura Yohei",
        "前川哲也さん：11月17日(オフサイト実施日)から今日までを振り返って、あなたとのつながり度合いはどれくらいですか。前回のあなたの定義をもとに答えてください。 (How close was your connection since the offsite?...Maekawa-san)": "Question A: Maekawa Tetsuya",
        "先週1週間を振り返り、前川哲也さんが感じている業務上の課題をどれくらい把握できていると感じますか？（How much do you think you acknowledge the issues around their job in the last week?）": "Question B: Maekawa Tetsuya",
        "石井理央さん：11月17日(オフサイト実施日)から今日までを振り返って、あなたとのつながり度合いはどれくらいですか。前回のあなたの定義をもとに答えてください。 (How close was your connection since the offsite?...Ishii-san)": "Question A: Ishii Rio",
        "先週1週間を振り返り、石井理央さんが感じている業務上の課題をどれくらい把握できていると感じますか？（How much do you think you acknowledge the issues around their job in the last week?）": "Question B: Ishii Rio",
        "山本 佳弘さん：11月17日(オフサイト実施日)から今日までを振り返って、あなたとのつながり度合いはどれくらいですか。前回のあなたの定義をもとに答えてください。 (How close was your connection since the offsite?...Yamamoto-san)": "Question A: Yamamoto Yoshihiro",
        "先週1週間を振り返り、山本 佳弘さんが感じている業務上の課題をどれくらい把握できていると感じますか？（How much do you think you acknowledge the issues around their job in the last week?）": "Question B: Yamamoto Yoshihiro",
        "三上顕さん：11月17日(オフサイト実施日)から今日までを振り返って、あなたとのつながり度合いはどれくらいですか。前回のあなたの定義をもとに答えてください。 (How close was your connection since the offsite?...Mikami-san)": "Question A: Mikami Ken",
        "先週1週間を振り返り、三上顕さんが感じている業務上の課題をどれくらい把握できていると感じますか？（How much do you think you acknowledge the issues around their job in the last week?）": "Question B: Mikami Ken",
        "小西直之さん：11月17日(オフサイト実施日)から今日までを振り返って、あなたとのつながり度合いはどれくらいですか。前回のあなたの定義をもとに答えてください。 (How close was your connection since the offsite?...Konishi-san)": "Question A: Konishi Naoyuki",
        "先週1週間を振り返り、小西直之さんが感じている業務上の課題をどれくらい把握できていると感じますか？（How much do you think you acknowledge the issues around their job in the last week?）": "Question B: Konishi Naoyuki",
        "今井 恵理子さん：11月17日(オフサイト実施日)から今日までを振り返って、あなたとのつながり度合いはどれくらいですか。前回のあなたの定義をもとに答えてください。 (How close was your connection since the offsite?...Imai-san)": "Question A: Imai Eriko",
        "先週1週間を振り返り、今井 恵理子さんが感じている業務上の課題をどれくらい把握できていると感じますか？（How much do you think you acknowledge the issues around their job in the last week?）": "Question B: Imai Eriko",
        "木村和生さん：11月17日(オフサイト実施日)から今日までを振り返って、あなたとのつながり度合いはどれくらいですか。前回のあなたの定義をもとに答えてください。 (How close was your connection since the offsite?...Kimura-san)": "Question A: Kimura Kazuo",
        "先週1週間を振り返り、木村和生さんが感じている業務上の課題をどれくらい把握できていると感じますか？（How much do you think you acknowledge the issues around their job in the last week?）": "Question B: Kimura Kazuo",
        "勝岡大貴さん：11月17日(オフサイト実施日)から今日までを振り返って、あなたとのつながり度合いはどれくらいですか。前回のあなたの定義をもとに答えてください。 (How close was your connection since the offsite?...Katsuoka-san)": "Question A: Katsuoka Daiki",
        "先週1週間を振り返り、勝岡大貴さんが感じている業務上の課題をどれくらい把握できていると感じますか？（How much do you think you acknowledge the issues around their job in the last week?）": "Question B: Katsuoka Daiki",
        "渋谷孝洋さん：11月17日(オフサイト実施日)から今日までを振り返って、あなたとのつながり度合いはどれくらいですか。前回のあなたの定義をもとに答えてください。 (How close was your connection since the offsite?...Shibuya-san)": "Question A: Shibuya Takahiro",
        "先週1週間を振り返り、渋谷孝洋さんが感じている業務上の課題をどれくらい把握できていると感じますか？（How much do you think you acknowledge the issues around their job in the last week?）": "Question B: Shibuya Takahiro",
        "林邦彦さん：11月17日(オフサイト実施日)から今日までを振り返って、あなたとのつながり度合いはどれくらいですか。前回のあなたの定義をもとに答えてください。 (How close was your connection since the offsite?...Kunihiko Hayashi-san)": "Question A: Hayashi Kunihiko",
        "先週1週間を振り返り、林邦彦さんが感じている業務上の課題をどれくらい把握できていると感じますか？（How much do you think you acknowledge the issues around their job in the last week?）": "Question B: Hayashi Kunihiko",
        "林洋輔さん：11月17日(オフサイト実施日)から今日までを振り返って、あなたとのつながり度合いはどれくらいですか。前回のあなたの定義をもとに答えてください。 (How close was your connection since the offsite?...Yosuke Hayashi-san)": "Question A: Hayashi Yosuke",
        "先週1週間を振り返り、林洋輔さんが感じている業務上の課題をどれくらい把握できていると感じますか？（How much do you think you acknowledge the issues around their job in the last week?）": "Question B: Hayashi Yosuke",
        "伊吹 立さん：11月17日(オフサイト実施日)から今日までを振り返って、あなたとのつながり度合いはどれくらいですか。前回のあなたの定義をもとに答えてください。 (How close was your connection since the offsite?...Ibuki-san)": "Question A: Ibuki Ryu",
        "先週1週間を振り返り、伊吹 立さんが感じている業務上の課題をどれくらい把握できていると感じますか？（How much do you think you acknowledge the issues around their job in the last week?）": "Question B: Ibuki Ryu",
        "眺野 真太郎さん：11月17日(オフサイト実施日)から今日までを振り返って、あなたとのつながり度合いはどれくらいですか。前回のあなたの定義をもとに答えてください。 (How close was your connection since the offsite?...Chono-san)": "Question A: Chono Shintaro",
        "先週1週間を振り返り、眺野 真太郎さんが感じている業務上の課題をどれくらい把握できていると感じますか？（How much do you think you acknowledge the issues around their job in the last week?）": "Question B: Chono Shintaro",
    }

    # "第1回目と2回目で、「つながり合い」に変化があった場合、何がきっかけでしたか？": "Free Response",

    df = pd.read_csv(filepath / filename)
    df.rename(columns=renames, inplace=True)
    df.drop(columns=["Timestamp"], inplace=True)
    df["Email Address"] = df["Email Address"].apply(lambda e: e.lower())
    df.set_index("Email Address", inplace=True)

    A_columns = [col for col in df.columns if "Question A:" in col]
    B_columns = [col for col in df.columns if "Question B:" in col]

    dfA = df[A_columns]
    dfB = df[B_columns]
    free_response = df[["第1回目と2回目で、「つながり合い」に変化があった場合、何がきっかけでしたか？"]]

    dfA.rename(columns={col: col.replace("Question A: ", "") for col in dfA.columns}, inplace=True)
    dfB.rename(columns={col: col.replace("Question B: ", "") for col in dfB.columns}, inplace=True)

    _, emails = load_mitsui_names_and_emails()
    names_to_emails = emails.to_dict(orient="index")

    dfA.rename(columns={name: names_to_emails[name]["Mail Address"] for name in dfA.columns}, inplace=True)
    dfB.rename(columns={name: names_to_emails[name]["Mail Address"] for name in dfB.columns}, inplace=True)

    # Only return columns if those people filled out the survey
    dfA = dfA[dfA.index.tolist()]
    dfB = dfB[dfB.index.tolist()]

    emails.reset_index(inplace=True)
    emails.set_index("Mail Address", inplace=True)
    email_to_name = emails.to_dict(orient="index")
    email_to_name = {k:v["Name (EN)"] for k,v in email_to_name.items()}

    # dfA
    dfA.reset_index(inplace=True)
    dfA["Email Address"] = dfA["Email Address"].apply(lambda e: email_to_name[e])
    dfA.rename(columns={"Email Address": "Name"}, inplace=True)
    dfA.rename(columns=email_to_name, inplace=True)
    dfA.set_index("Name", inplace=True)

    # dfB
    dfB.reset_index(inplace=True)
    dfB["Email Address"] = dfB["Email Address"].apply(lambda e: email_to_name[e])
    dfB.rename(columns={"Email Address": "Name"}, inplace=True)
    dfB.rename(columns=email_to_name, inplace=True)
    dfB.set_index("Name", inplace=True)

    free_response.reset_index(inplace=True)
    free_response["Email Address"] = free_response["Email Address"].apply(lambda e: email_to_name[e])
    free_response.rename(columns={"Email Address": "Name"}, inplace=True)
    free_response.set_index("Name", inplace=True)

    # Fill diagonal
    np.fill_diagonal(dfA.values, -1)
    dfA_zeros = dfA.replace(-1, 0)
    dfA_nan = dfA.replace(-1, np.nan)

    np.fill_diagonal(dfB.values, -1)
    dfB_zeros = dfB.replace(-1, 0)
    dfB_nan = dfB.replace(-1, np.nan)

    # save the parsed data
    dfA_nan.to_pickle(filepath / Path("A_WorkX_Connectedness_nan.pkl"))
    dfA_zeros.to_pickle(filepath / Path("A_WorkX_Connectedness_zeros.pkl"))
    dfB_nan.to_pickle(filepath / Path("B_WorkX_Connectedness_nan.pkl"))
    dfB_zeros.to_pickle(filepath / Path("B_WorkX_Connectedness_zeros.pkl"))
    free_response.to_pickle(filepath / Path("WorkX_free_responses_round2.pkl"))
    # return dfA, dfB, free_response



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
    free_response.to_pickle(filepath / Path("WorkX_free_responses_round1.pkl"))
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


def make_graphcommons_csv(pairwise_df, question, min_link_strength=0):
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

    columns = copy(pairwise_df.columns.tolist())

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
    graphcommons_edges.to_csv(filepath / Path(f"graphcommons_workX_round2_{question}_edges_{min_link_strength}.csv"), index=False)
    graphcommons_nodes = pd.DataFrame(node_data, columns=node_columns)
    graphcommons_nodes.to_csv(filepath / Path(f"graphcommons_workX_round2_{question}_nodes.csv"), index=False)


if __name__ == "__main__":
    # parse_mitsui_survey_results()
    # parse_second_mitsui_survey_results()
    _, _, _, _, dfA_zeros, _, dfB_zeros, _ = load_saved_survey_results()
    make_graphcommons_csv(dfA_zeros, "A", min_link_strength=4)
    make_graphcommons_csv(dfA_zeros, "A", min_link_strength=6)
    make_graphcommons_csv(dfA_zeros, "A", min_link_strength=8)

    make_graphcommons_csv(dfB_zeros, "B", min_link_strength=4)
    make_graphcommons_csv(dfB_zeros, "B", min_link_strength=6)
    make_graphcommons_csv(dfB_zeros, "B", min_link_strength=8)