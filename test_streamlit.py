from p1_graphs import *
import altair as alt
import streamlit as st


@st.cache_data
def get_data():
    data = get_accident_data(fname="dataset_v1.csv", sample=False)
    accident_data = get_weather_data(data, fname="weather.csv")
    cols = [
        "CRASH DATE",
        "LATITUDE",
        "LONGITUDE",
        "date",
        "HOUR",
        "week",
        "weekday",
        "month",
        "name",
        "conditions",
        "VEHICLE TYPE CODE 1",
    ]

    # select only cols
    accident_data = accident_data[cols]
    return accident_data


data = get_data()
vis = make_visualizations(data)
# make sidebar with instructions
with st.sidebar:
    st.title("Instructions")
    st.write(
        "This app allows you to explore the relationship between weather and traffic accidents in NYC"
    )

st.altair_chart(vis)
