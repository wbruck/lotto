
from email.policy import default
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

st.sidebar.subheader("Select the week to join")
# sport = st.sidebar.selectbox("Sport", ["NBA", "MLB", "NHL", "NFL"], 0)
# week = st.sidebar.selectbox("Week", range(3,6))
# site = st.sidebar.selectbox("Site", ["dk_dfs", "fd_dfs"],0)
# slate = st.sidebar.selectbox("Start Time", ["early", "late"],0)

COLUMNS_TO_DROP = ['prizes_remaining_link', ]

# @st.cache(allow_output_mutation=True)
def load_data():
    """Read the data from local."""

    STREAMFILEPATH = "ticket_data.csv"
    ticket_data= pd.read_csv(STREAMFILEPATH, index_col=0)
    ticket_data = ticket_data.drop(columns=COLUMNS_TO_DROP)
    # drop index
    # ticket_data = ticket_data.drop(columns=['Unnamed: 0'])
    return pd.DataFrame(ticket_data)

def load_remaining_prize_data()->pd.DataFrame:

    """Read the data from local."""

    STREAMFILEPATH = "remaining_prize_data.csv"
    prize_data= pd.read_csv(STREAMFILEPATH, index_col=0)
    # join the columns name and price into 1 new column
    prize_data['name_price'] = prize_data['name'] + " " + prize_data['price'].astype(str)
    # create value coulmn that is the amount * remaining
    prize_data['value'] = prize_data['amount'] * prize_data['remaining']
    # ticket_data = ticket_data.drop(columns=COLUMNS_TO_DROP)
    # drop index
    # ticket_data = ticket_data.drop(columns=['Unnamed: 0'])
    return pd.DataFrame(prize_data)

def main():


    # Load data and models
    data = load_data()
    remaining_prize_data = load_remaining_prize_data()
    # data['Game Day'] = data.apply(lambda x: datetime.datetime.strptime(x['Game Time'], '%m/%d/%Y %I:%M%p ET').strftime('%A'), axis=1)


    ### sidebar
    ticket_price = data['price'].unique()
    ticket_price_choice = st.sidebar.multiselect("Game Time", ticket_price, default=ticket_price)

    data = data[data['price'].isin(ticket_price_choice)]
    remaining_prize_data = remaining_prize_data[remaining_prize_data['price'].isin(ticket_price_choice)]
       
    # games = data[['Game VS', 'Game Day', 'Game Time']].drop_duplicates(keep='first')
    # st.sidebar.subheader(f'Games: {len(games)}')
    # st.sidebar.write(games)

    # select positions
    # positions = data['POS'].unique()
    # position_choice = st.sidebar.selectbox("select symbols", positions, index=0)

    # data = data[data['POS'] == position_choice]

    # players_selected = st.sidebar.multiselect("Select Players", data['Name'].unique(), format_func=lambda x: f"{x} and farts")


    #### see raw data
    st.title("MD Lottery Analysis")
    if st.checkbox('Show raw data', key='raw_data'):
        st.subheader('Raw data')
        st.data_editor(data)
    st.write("start tracking price")

    # columns 
    # col1, col2 = st.columns(1)


    ### show the remaining prizes data
    #### see raw data
    st.title("Remaining Prizes")
    if st.checkbox('Show prize data', key='prize_data'):
        st.subheader('Remaining Prizes data')
        st.data_editor(remaining_prize_data)

    # filters to get information
    prize_remaining_columns = ['amount', 'start', 'remaining','value']    
    field_to_filter = st.selectbox("Filter by", prize_remaining_columns, index=0)

    # get unique values out of the amount field
    amount_values = np.sort(remaining_prize_data[field_to_filter].unique())
    
    amount_filters = st.multiselect(f"Included {field_to_filter}", amount_values, default=amount_values)
    amount_to_filter = min(amount_filters)
    percent_to_filter = st.slider(f"Minimum Percent Remaining",
                                min_value=0.0, 
                                max_value=1.0, 
                                value=0.5)

    groups = remaining_prize_data.groupby(['name_price'])
    filter_data = groups.apply(lambda x: x[(x[field_to_filter] >= amount_to_filter) &
                                           (x['remaining']/x['start'] > percent_to_filter)][prize_remaining_columns]).reset_index()

    prize_plot = px.bar(filter_data, x="name_price", y='value', text='amount')
    st.plotly_chart(prize_plot)



    #-------------------------
    # single select
    all_columns = data.columns
    stat_select = st.multiselect("Select Stats", options=all_columns, default=all_columns)

    # order by stat
    order_by = st.selectbox("Order by", stat_select)
    data = data.sort_values(by=order_by, ascending=False)

    # add a filter slider to only show players with a certain salary
    for stat_choice in stat_select:
        try:
            min_value=int(data[stat_choice].min())
            max_value=int(data[stat_choice].max())
        except ValueError:
            min_value=0
            max_value=0
        if min_value == max_value:
            max_value = max_value + 1
        starting_value = 0
        if max_value > 0:
            starting_value = min_value + 1
        min_choice = st.slider(f"Minimum {stat_choice}", 
                               min_value=min_value, 
                               max_value=max_value, 
                               value=starting_value)
        data = data[data[stat_choice] >= min_choice]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    y_position = 0.0
    r_position = 1.0
    l_position = 0.0
    y_axis_dict = {}
 
    for x, stat in enumerate(stat_select):
        color = color_chooser(x)
        if x % 2:
            side = "right"
            r_position -= 0.05
            y_position = r_position
        else:
            side = "left"
            l_position += 0.05
            y_position = l_position
        if x == 0:
            fig.add_trace(go.Scatter(
                x=data['Name'],
                y=data[stat],
                name=stat
            ))
            y_axis_dict['yaxis']=dict(
                title=stat,
                titlefont=dict(
                    color=color
                ),
                tickfont=dict(
                    color=color
                )
            )

        elif x > 0:
            fig.add_trace(go.Scatter(
                x=data['Name'],
                y=data[stat],
                name=stat,
                yaxis=f'y{x+1}'
            ))
            nn = f'yaxis{x+1}'
            print(nn)
            y_axis_dict[nn]=dict(
                title=stat,
                titlefont=dict(
                    color=color
                ),
                tickfont=dict(
                    color=color
                ),
                    anchor="free",
                    overlaying="y",
                    side=side,
                    position=y_position,
            )


        y_position += 0.05
    fig.update_layout(
        y_axis_dict,
        xaxis=dict(
            domain=[0,1]
        ),
        hovermode="x unified",
    )
    
    # out = Output()
    # @out.capture(clear_output=True)
    # def handle_click(trace, points, state):
    #     player_list.append(points.point_inds)
    #     st.write(player_list)

    # clicker = fig.data[0]
    # clicker.on_click(handle_click)
    selected_points = plotly_events(fig)
    
    # st.write(selected_points)
    if selected_points:
        selected_player = get_player_data_by_name(selected_points[0]['x'], data)
        added_player = st.session_state.players.add_player(selected_player, position_choice)
        st.write(added_player)
    st.write(st.session_state.players)
    # TODO - PLOTLY on click save player to another tab??

    # streamlit button to save players to json
    if st.button("Save Players"):
        st.write(st.session_state.players.write_to_json(pf.get_selected_players_path()))

    #### graph 2
    # KNN of players with the selected stats from the top
    st.header("KNN")
    st.subheader("KNN of players with the selected stats from the top")


    #### graph 3
    # correlation of selected stats

    st.header("Correlation")


    #### Select players
    # run DFS to create lines


    #### tab 2 
    # analize lineups generated
    # hold a list of generated lineups, maybe in a pickle files that are just listed to "load"

        # show the lines that use players in bar graphs format
        # 



    #     ta_plot = px.scatter(ta_data, x='TLV', y='APR', color='lookup')
    #     st.plotly_chart(ta_plot)

    #     p_corr, _ = pearsonr(ta_data['APR'], ta_data['TLV'])
    #     s_corr, _ = spearmanr(ta_data['APR'], ta_data['TLV'])

    #     st.header("Market")
    #     max_value = data['APR'].max()/4
    #     apr_to_filter = st.slider('Min APR to Display', 0, int(max_value), int(max_value/4))
    #     filtered_data = data[data['APR'] >= apr_to_filter]
        

    #     symbol_plot = px.line(filtered_data, x='date', y='APR', color='symbol')
    #     st.plotly_chart(symbol_plot)

    #     agree = st.button('click to see filtered data')
    #     if agree:
    #         st.write(filtered_data.sort_values(['symbol', 'date']))

    # ## container
    # owned_viz = st.container()


    # with col2:
    #     st.header("Multiple Stats")

    #     stats_to_show = st.multiselect("Owned Symbols", options=all_stats)

    #     owned_data = data[stats_to_show]

    #     symbol_plot = px.line(owned_data, x='Name', y=stats_to_show, color='symbol')
    #     st.plotly_chart(symbol_plot)

    #     agree = st.button('click to see owned data')
    #     if agree:
    #         st.write(owned_data.sort_values(['symbol', 'date']))

    
    
    # tlv_list = sorted(data['TLV'].drop_duplicates().tolist())

    # ## columns2
    # col_x1, col_x2 = st.columns(2)
    # ## container
    # tlv_vis = st.container()

    # with col_x1:
    #     st.header("Total Locked Value")
    #     tlv_filter = st.select_slider("TLV Range", options=tlv_list, value=(tlv_list[0],tlv_list[-1]))
    #     tlv_data = data[data['TLV'].between(tlv_filter[0], tlv_filter[1]) ]
    #     st.write("how to filter if the value EVER hits between...  filter, then get all symbols in list, then get all data for symbols")

    #     tlv_plot = px.line(tlv_data, x='date', y='TLV', color='symbol')
    #     st.plotly_chart(tlv_plot)

    #     agree = st.button('click to see tlv data')
    #     if agree:
    #         st.write(tlv_data.sort_values(['symbol', 'date']))

    # ## container
    # t_x_a_vis = st.container()

    # with col_x2:
    
    #     st.write(f"pearson: {p_corr}")
    #     st.write(f"spearman: {s_corr}")
    #     agree = st.button('click to see tlv tlv x apr')
    #     if agree:
    #         st.write(ta_data.sort_values(['symbol', 'date']))

    # # st.line_chart(time_data[['APR', 'symbol' ]])
    # # User search
    # # user_input = st.text_area("Search box", "covid-19 misinformation and social media")

    # # # Filters
    # # st.sidebar.markdown("**Filters**")
    # # filter_year = st.sidebar.slider("Publication year", 2010, 2021, (2010, 2021), 1)
    # # filter_citations = st.sidebar.slider("Citations", 0, 250, 0)
    # # num_results = st.sidebar.slider("Number of search results", 10, 50, 10)

    # # Fetch results
    # # if user_input:
    # #     # Get paper IDs
    # #     # D, I = vector_search([user_input], model, faiss_index, num_results)
    # #     # Slice data on year
    # #     frame = data[
    # #         (data.year >= filter_year[0])
    # #         & (data.year <= filter_year[1])
    # #         & (data.citations >= filter_citations)
    # #     ]
    # #     # Get individual results
    # #     for id_ in I.flatten().tolist():
    # #         if id_ in set(frame.id):
    # #             f = frame[(frame.id == id_)]
    # #         else:
    # #             continue

    # #         st.write(
    # #             f"""**{f.iloc[0].original_title}**  
    # #         **Citations**: {f.iloc[0].citations}  
    # #         **Publication year**: {f.iloc[0].year}  
    # #         **Abstract**
    # #         {f.iloc[0].abstract}
    # #         """
    # #         )


if __name__ == "__main__":
    main()