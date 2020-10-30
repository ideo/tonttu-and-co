import streamlit as st
from streamlit_observable import observable

from connectedness import load_data


st.title("Tonttu & Co. is here to help!")

df = load_data()
st.dataframe(df)


# observers = observable("County Brush", 
#     notebook="d/4f9aa5feff9761c9",
#     targets=["viewof countyCodes"], 
#     observe=["selectedCounties"]
# )

# selectedCounties = observers.get("selectedCounties")


observers = observable("Force Graph",
    notebook="@d3/force-directed-graph",
    targets=["chart"],
    observe=["data"])

force_graph = observers.get("data")