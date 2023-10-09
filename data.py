#%%
import pickle
from dataclasses import dataclass, asdict
import pandas as pd
from pprint import pprint
# read in the list of tickets from the pickle file
with open("tickets.pkl", "rb") as f:
    list_of_tickets = pickle.load(f)
pprint(list_of_tickets)
# %%
def my_dict_factory(data):
    return {k: (v if not isinstance(v, list) else [i.__dict__ for i in v]) for k, v in data.__dict__.items() }
# %%
def flattener(data):
    stuff = {}

data = []
for ticket in list_of_tickets:
    test = {k: v if not isinstance(v, list) else ({f"prize{x}":i.__dict__ for x, i in enumerate(v.copy())}) for k, v in ticket.__dict__.items() }
    # {f"prize{x}":i.__dict__ for x, i in enumerate(v.copy())}
    print(test)
    data.append(test)

#%%
data
#%%
ticket_data = pd.json_normalize(data, max_level=2)

ticket_data.to_csv("ticket_data.csv")


# %%
ticket_data

# %%
remaining_prize_data = []
for ticket in data:
    new_ticket = {}
    new_ticket['name'] = ticket['name']
    new_ticket['price'] = ticket['price']
    for _,remaining_prize in ticket['prizes_remaining'].items():
        new_ticket['amount'] = remaining_prize['amount']
        new_ticket['start'] = remaining_prize['start']
        new_ticket['remaining'] = remaining_prize['remaining']
        remaining_prize_data.append(new_ticket.copy())    
# %%
pd.DataFrame(remaining_prize_data).to_csv("remaining_prize_data.csv")
# %%
prizes = pd.read_csv("remaining_prize_data.csv")
prizes
# %%
# group data by name and price
# sum all the remaining prizes
# create a new column that is the sum of all the remaining prizes

prizes.groupby(['name', 'price'])['amount','start', 'remaining'].sum()

# %%
field_to_filter = 'amount'
amount_to_filter = 100
percent_to_filter = 0.5
field_to_sum = 'remaining'

groups = prizes.groupby(['name', 'price'])
groups.apply(lambda x: x[(x[field_to_filter] >= amount_to_filter) & 
                         (x['remaining']/x['start'] > percent_to_filter)][[field_to_sum, 'amount', 'start']]).reset_index()
# %%
