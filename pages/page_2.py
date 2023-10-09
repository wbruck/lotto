import streamlit as st
import streamlit.components.v1 as components

import datetime

st.markdown("# Page 2 DFS ❄️")
st.sidebar.markdown("# Page 2 DFS ❄️")

st.markdown("## list files possible for starting dfs")
st.markdown("## somehow show which players are in the selected file")

st.markdown("## start the DFS with the selected players")
# run all the other stuff from start_dfs

st.markdown("show the outputs of all the lineup gen here, re-use repeatable code for the above")
if st.button("Start DFS"):
    st.write(f"Starting DFS at {datetime.datetime.now()}")
    # do DFS here
    st.write(f"Finished DFS at {datetime.datetime.now()}")
    st.write("DFS results here # lineups")


if st.button("open sweet vis"):
    with open("SWEETVIZ_REPORT.html", 'r', encoding='utf-8') as f:
        components.html(f.read(), height=1000, width=1800, scrolling=True)