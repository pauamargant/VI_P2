from streamlit.components.v1 import html
import streamlit as st

st.title("Pregenerated HTML version of the visualization")
# write a disclaimer writing that this is a pregenerated html version of the chart, based on the chart shown on the jupyter notebook
st.write(
    "This is a pregenerated HTML version of the visualization. The visualization can also be found in the [link](https://ny-traffic-vi.streamlit.app/)"
)
with open("visualization.html", "r") as f:
    page = f.read()

html(page, width=1500, height=3000)
