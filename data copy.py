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
