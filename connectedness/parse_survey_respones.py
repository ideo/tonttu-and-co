from pathlib import Path

import pandas as pd


def load_data():
    filename = Path("connectedness/dummy_data.csv")
    df = pd.read_csv(filename).drop(columns=["Timestamp"])
    
    name_order = {
        "PERSON1":  1, 
        "PERSON2":  2,
        "PERSON3":  3,
        "PERSON4":  4,
        "PERSON5":  5,
        "PERSON6":  6,
        "PERSON7":  7,
        "PERSON8":  8,
        "PERSON9":  9,
        "PERSON10": 10,
    }

    df["sort_by"] = df["What is your name?"].apply(lambda n: name_order[n])
    df.set_index("What is your name?", inplace=True)
    df.sort_values(axis=0, by="sort_by", inplace=True)
    df.drop(columns=["sort_by"], inplace=True)
    return df


if __name__ == "__main__":
    df = load_data()
    print(df)