from __future__ import annotations

import streamlit as st

from utils.practice_page import render_practice_page


st.set_page_config(page_title="GATE DA Prep Hub | Artificial Intelligence", page_icon="🧠", layout="wide")
render_practice_page("artificial_intelligence")
