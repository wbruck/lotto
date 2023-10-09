
import pickle
from random import randint
import pandas as pd
import streamlit as st
import numpy as np

import plotly_express as px

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from scipy.stats import spearmanr, pearsonr

from streamlit_plotly_events import plotly_events

import datetime
import json
import os

st.sidebar.subheader("Select STuff here")
# sport = st.sidebar.selectbox("Sport", ["NBA", "MLB", "NHL", "NFL"], 0)
# week = st.sidebar.selectbox("Week", range(3,6))
# site = st.sidebar.selectbox("Site", ["dk_dfs", "fd_dfs"],0)
# slate = st.sidebar.selectbox("Start Time", ["early", "late"],0)

COLUMNS_TO_DROP = ['prizes_remaining_link', ]

# @st.cache(allow_output_mutation=True)
def load_remaining_prize_data()->pd.DataFrame:

    """Read the data from local."""

    STREAMFILEPATH = "ticket_data.csv"
    prize_data= pd.read_csv(STREAMFILEPATH, index_col=0)
    # join the columns name and price into 1 new column
    prize_data['name_price'] = prize_data['name'] + " " + prize_data['price'].astype(str)
    # create value coulmn that is the amount * remaining
    prize_data['value'] = prize_data['prize_amount'] * prize_data['prize_remaining_num']
    prize_data['prize_probability'] = prize_data['prize_remaining_num'] / prize_data['prize_start_num']
    
    basedate = pd.Timestamp('2023-10-05')
    prize_data['days_since_start'] = (basedate - pd.to_datetime(prize_data['game_start_date'])).dt.days
    #prize_data.apply(lambda x: (prize_data.game_start_date.to_datetime() - basedate).days, axis=1)#prize_data['game_start_date'].astype(datetime)
    # ticket_data = ticket_data.drop(columns=COLUMNS_TO_DROP)
    # drop index
    # ticket_data = ticket_data.drop(columns=['Unnamed: 0'])
    return pd.DataFrame(prize_data)

def main():


    # Load data and models

    remaining_prize_data = load_remaining_prize_data()
    # data['Game Day'] = data.apply(lambda x: datetime.datetime.strptime(x['Game Time'], '%m/%d/%Y %I:%M%p ET').strftime('%A'), axis=1)


    ### sidebar
    ticket_price = remaining_prize_data['price'].unique()
    ticket_price_choice = st.sidebar.multiselect("Game Time", ticket_price, default=ticket_price)

    remaining_prize_data = remaining_prize_data[remaining_prize_data['price'].isin(ticket_price_choice)]
       
    st.title("MD Lottery Analysis")

    ### show the remaining prizes data
    st.title("Remaining Prizes")
    if st.checkbox('Show prize data', key='prize_data'):
        st.subheader('Remaining Prizes data')
        st.data_editor(remaining_prize_data)

    days_since_start_values = np.sort(remaining_prize_data["days_since_start"].unique())
    days_since_start_min = min(days_since_start_values)
    days_since_start_max = max(days_since_start_values)
    days_to_filter = st.slider(f"Minimum Percent Remaining",
                                min_value=days_since_start_min, 
                                max_value=days_since_start_max, 
                                value=days_since_start_max)
    remaining_prize_data = remaining_prize_data[remaining_prize_data["days_since_start"] < days_to_filter]
    plot = px.bar(remaining_prize_data, x="name_price", y='prize_remaining_num', text='prize_amount',hover_data=['prize_start_num', 'prize_remaining_num', 'prize_probability'], color='days_since_start')
    st.plotly_chart(plot)
    # filters to get information
    # prize_remaining_columns = ['prize_amount', 'prize_start_num', 'prize_remaining_num','value', 'prize_probability']    
    # field_to_filter = st.selectbox("Filter by", prize_remaining_columns, index=0)

    # # get unique values out of the amount field
    # amount_values = np.sort(remaining_prize_data[field_to_filter].unique())
    
    # amount_filters = st.multiselect(f"Included {field_to_filter}", amount_values, default=amount_values)
    # amount_to_filter = min(amount_filters)
    # percent_to_filter = st.slider(f"Minimum Percent Remaining",
    #                             min_value=0.0, 
    #                             max_value=1.0, 
    #                             value=0.5)

    # groups = remaining_prize_data.groupby(['name_price'])
    # filter_data = groups.apply(lambda x: x[(x[field_to_filter] >= amount_to_filter) &
    #                                        (x['prize_remaining_num']/x['prize_start_num'] > percent_to_filter)][prize_remaining_columns]).reset_index()

    # prize_plot = px.bar(filter_data, x="name_price", y='value', text='prize_amount',hover_data=['prize_start_num', 'prize_remaining_num', 'prize_probability'], color='prize_amount')
    # st.plotly_chart(prize_plot)



if __name__ == "__main__":
    main()