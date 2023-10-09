import streamlit as st
import streamlit.components.v1 as components

import datetime
import os
dir = os.path.join('dk_dfs', 'week1', )
WEEK=1
STREAMFILEPATH = os.path.join(dir, f"joinedWeek{WEEK}.csv")

st.markdown("# Page Lineup Sweetviz alaysis")
st.sidebar.markdown("# Page 2 DFS ❄️")

st.markdown("show sweet vis, maybe button")
if st.button("open sweet vis"):
    lines_one_path = os.path.join(dir, "SWEETVIZ_REPORT.HTML")
    with open(lines_one_path, 'r', encoding='utf-8') as f:
        components.html(f.read(), height=1000, width=1800, scrolling=True)

st.markdown("## list of positions, ")
st.markdown("## list of players in each position after opening position")



st.markdown("##select players to remove from each position")


# run the de-dupe
# show the sweet viz

st.markdown("show sweet vis, maybe button")
if st.button("open sweet vis2"):
    with open("SWEETVIZ_REPORT2.html", 'r', encoding='utf-8') as f:
        components.html(f.read(), height=1000, width=1800, scrolling=True)