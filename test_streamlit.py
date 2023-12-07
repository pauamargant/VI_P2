import streamlit as st
import altair as alt
import pandas as pd

data = pd.DataFrame(
    {
        "BoroName": ["Brooklyn", "Queens", "Manhattan", "Bronx", "Staten Island"],
        "Area": [69.5, 108.5, 22.8, 42.1, 58.5],
    }
)

