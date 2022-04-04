from setup import *
import plotly.express as px

temp, humid, weight = readSQL()

# ------------------------------
# Create Variables 
# ------------------------------

# --- Current Value
current_temp1 = temp['temp1'].iloc[-1]
current_temp2 = temp['temp2'].iloc[-1]
current_temp3 = temp['temp3'].iloc[-1]
current_temp4 = temp['temp4'].iloc[-1]

current_humid1 = humid['humid1'].iloc[-1]
current_humid2 = humid['humid2'].iloc[-1]

current_weight = weight['weight'].iloc[-1]

# --- Reformat for Graph
temp_long = pd.melt(temp, id_vars=['datetime'], var_name='sensor', value_name='reading')
temp_long['date'] = pd.to_datetime(temp_long['datetime']).dt.date
temp_final = temp_long.groupby(['date', 'sensor'], as_index=False).mean()

humid_long = pd.melt(humid, id_vars=['datetime'], var_name='sensor', value_name='reading')
humid_long['date'] = pd.to_datetime(humid_long['datetime']).dt.date
humid_final = humid_long.groupby(['date', 'sensor'], as_index=False).mean()

weight['date'] = pd.to_datetime(weight['datetime']).dt.date
weight_final = weight.groupby('date', as_index=False).mean()

# ------------------------------
# Figure Setup 
# ------------------------------

fig = px.line(temp_final, x="date", y="reading", color='sensor', facet_row="sensor", facet_row_spacing=0.01, height=200, width=200)  
fig.update_xaxes(visible=False, fixedrange=True)
fig.update_yaxes(visible=False, fixedrange=True)
fig.update_layout(annotations=[], overwrite=True)
fig.update_layout(
    showlegend=False,
    plot_bgcolor="white",
    margin=dict(t=10,l=10,b=10,r=10)
)

hfig = px.line(humid_final, x="date", y="reading", color='sensor', facet_row="sensor", facet_row_spacing=0.01, height=200, width=200)  
hfig.update_xaxes(visible=False, fixedrange=True)
hfig.update_yaxes(visible=False, fixedrange=True)
hfig.update_layout(annotations=[], overwrite=True)
hfig.update_layout(
    showlegend=False,
    plot_bgcolor="white",
    margin=dict(t=10,l=10,b=10,r=10)
)

wfig = px.line(weight, x="datetime", y="weight", height=200, width=200)  
wfig.update_xaxes(visible=False, fixedrange=True)
wfig.update_yaxes(visible=False, fixedrange=True)
wfig.update_layout(annotations=[], overwrite=True)
wfig.update_layout(
    showlegend=False,
    plot_bgcolor="white",
    margin=dict(t=10,l=10,b=10,r=10)
)
