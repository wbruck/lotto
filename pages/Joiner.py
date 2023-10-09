import streamlit as st
import streamlit.components.v1 as components

import pickle
from random import randint
import pandas as pd
import numpy as np

import datetime
import copy

from path_finder import PathFinder

import os


import logging
logger = logging.getLogger(__name__)


# create console handler and set level to debug
ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
logger.setLevel(logging.INFO)

st.markdown("# Joiner ❄️")
st.sidebar.markdown("# joiner ❄️")
st.sidebar.subheader("Select the week to join")
sport = st.sidebar.selectbox("Sport", ["NBA", "MLB", "NHL", "NFL"], 0)
week = st.sidebar.selectbox("Week", range(3,6))
site = st.sidebar.selectbox("Site", ["dk_dfs", "fd_dfs"],0)
slate = st.sidebar.selectbox("Start Time", ["early", "late"],0)

pf = PathFinder(sport=sport, site=site, date=str(week), slate_start_time=slate)


# upload a file and keep it in the curernt pf dir

uploaded_file_list = st.file_uploader("Upload a file", type=['csv', 'json', 'pkl'])

st.markdown(f"uploade files {uploaded_file_list}")

# defining to prevent errors later
merged_data = pd.DataFrame([])

if uploaded_file_list:
    if not isinstance(uploaded_file_list, list):
        uploaded_file_list = [uploaded_file_list]
    for uploaded_file in uploaded_file_list:
        with open(os.path.join(pf.uploaded_files_path, uploaded_file.name), 'wb') as f:
            logger.info(f"writing {uploaded_file.name} to {pf.uploaded_files_path}")
            f.write(uploaded_file.getbuffer())

file_choices = pf.check_uploaded_files()


st.markdown("## select the columns to join on")
join_keys = {}
join_key = {}
for file_name in file_choices:
    if 'config' in file_name:
        continue
    st.markdown(f"### {file_name}")
    df = pd.read_csv(os.path.join(pf.uploaded_files_path, file_name))
    #### for stats file from website
    if st.checkbox("Perform STATS cols tranforms", key=f"{file_name}_stats"):
        df.rename(columns={"YDS": "PassingYDS", 
                                "TD": "PassingTD", 
                                "YDS.1": "RushingYDS",
                                "TD.1": "RushingTD",
                                "YDS.2": "ReceivingYDS",
                                "TD.2": "ReceivingTD"}, inplace=True)
    # for DK file 
    if st.checkbox("Perform DK game time transform", key=f"{file_name}_dk"):
        df[['Game VS', 'Game Time']] = df['Game Info'].str.split(' ', 1,  expand=True)
        df['Game Day'] = df.apply(lambda x: datetime.datetime.strptime(x['Game Time'], '%m/%d/%Y %I:%M%p ET').strftime('%A'), axis=1)
    # for FD file
    if st.checkbox("Perform FD injury transform", key=f"{file_name}_fd"):
        cond = df['Injury Details'].str.contains('<NA>')
        df['Injured'] = np.where(cond, 0, 1)
    # salary_file = st.selectbox("Salaries File Options", file_choices)
    # pf.set_salaries_path(salary_file)
    # salary_df = pd.read_csv(pf.salaries_path)
    st.subheader(f'Raw Data')
    st.dataframe(df, height=200)
    cols = st.multiselect("column to join on", list(df.columns), key=file_name)
    suffix = st.text_input("suffix", key=f"{file_name}_suffix")
    if st.checkbox("include in join", key=f"{file_name}_include"):
        join_key["join_suffix"] = f"_{suffix}"
        join_key["join"] = cols
        join_key["dataframe"] = copy.deepcopy(df)
        join_keys[file_name] = copy.deepcopy(join_key)
    
# run all the other stuff from start_dfs

for data_set_num, data_set_name in enumerate(join_keys.keys()):

    if data_set_num == 0:
        # on first file set the dataset to the merged set
        merged_data = join_keys[data_set_name]["dataframe"]
        merged_join_col = join_keys[data_set_name]["join"]
        merged_suffix = join_keys[data_set_name]["join_suffix"]

    else:
        # if data_set_num == 2:
        #     merged_suffix = f"{merged_join_col}_{merged_suffix}"
        #     logger.info(f"merged suffix {merged_suffix}")

        data_set_2 = join_keys[data_set_name]["dataframe"]
        join_col_2 = join_keys[data_set_name]["join"]
        join_suffix_2 = join_keys[data_set_name]["join_suffix"]

        logger.info(f"merging {merged_join_col} with {join_col_2}")
        merged_data = pd.merge(merged_data, data_set_2, left_on=merged_join_col,
                                right_on=join_col_2, how="outer", 
                                suffixes=(None, join_suffix_2))


st.subheader('Joined Data')
if st.checkbox("Fill Position", key="fill_position"):
    merged_data['POS'].fillna(merged_data['Roster Position'], inplace=True)
st.write(f"merged_data length {merged_data.shape}")
st.write(merged_data)
if st.button('Save'):
    merged_data.to_csv(pf.joined_data_path, index=False)
    st.success('Saved!')