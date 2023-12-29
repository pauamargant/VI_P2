from graphs import *
import altair as alt
import streamlit as st

st.set_page_config(layout="centered", page_title="NYC Traffic Accidents")


@st.cache_data
def get_data():
    data = get_accident_data(fname="dataset_v1.csv", sample=False)
    accident_data = get_weather_data(data, fname="weather2018.csv")

    return accident_data


#@st.cache_data
def get_graph(data):
    vis = make_visualization(data)
    return vis


# make sidebar with instructions
with st.sidebar:
    if st.button("Clear Selection"):
        st.write("Clearing selection")
    with st.expander("How to use"):
        st.write(
            """This app allows you to explore the relationship between weather and traffic accidents in NYC.
            Throughout the visualization you can click on specific items in  order to select them, which will update the rest of the visualization to show only the data that matches your selection.
            You can also hover over the data to see more information about it.
            At the bottom of the graph, dropwdown menus are also included to further filter the data.

            """
        )
    with st.expander("About"):
        st.write(
            """This app was created as part of the second project for the course Data Visualization at UPC.
            It was created by David Gallardo and Pau Amargant, and the code is available [here](github.com/pauamargant/VI_P2).
            """
        )

    with st.expander("Troubleshooting"):
        st.write(
            """
            - If the graph is not showing, try clicking on the 'Clear graph' button.
            - **IMPORTANT**: In some cases the interactions may not work as expected. If this happens, please refresh the page and try again.
            For further help, more detailed instructions on how to use it are available by going to the instructions page"""
        )
accident_data = get_data()
vis = get_graph(accident_data)
st.title("NYC Traffic Accidents")


st.altair_chart(vis)
print("done")
