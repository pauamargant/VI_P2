from streamlit.components.v1 import html
import streamlit as st

st.title("Pregenerated HTML version of the visualization")
# write a disclaimer writing that this is a pregenerated html version of the chart, based on the chart shown on the jupyter notebook
st.write(
    "This is a pregenerated HTML version of the visualization. It is not interactive, but it is a good way to see the visualization in case there are technical issues. The code for this visualization can be found in the `pages` folder of the repository."
)
with open("chart.html", "r") as f:
    page = f.read()

html(page, width=1500, height=3000)
