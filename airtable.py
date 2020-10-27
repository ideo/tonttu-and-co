import os
import json
import pickle
import requests

import pandas as pd


def get_data():
    url = "https://api.airtable.com/v0/app7o0CVsBtzgjnqb/GridLogger"

    headers = {
    "Authorization": f"Bearer {os.environ['AIRTABLE_API_KEY']}",
    }

    params = (
        # ("maxRecords", "3"),
        ("view", "Grid view"),
    )

    r = requests.get(url, headers=headers, params=params)
    content = json.loads(r.content)
    content = [r["fields"] for r in content["records"] if r["fields"]]
    print(content)
    df = pd.DataFrame(columns=content[0].keys())
    for row in content:
        df = df.append(pd.Series(row), ignore_index=True)

    df = df.set_index("Timestamp")
    print(df)

    pickle.dump(df, open("airtable_data.pkl", "wb"))


if __name__ == "__main__":
    get_data()