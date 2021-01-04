import streamlit as st
import numpy as np
import pandas as pd
import pydeck as pdk
import plotly.express as px
data_url=(
	"/Users/shiyuxiu/Desktop/new_york_collision_app/Motor_Vehicle_Collisions_-_Crashes.csv")


st.title("Motor vehicle collision in New York City")
st.markdown("This application is a streamlit dashboard to analyze the motor collision 🚙 🚨in NYC 🗽")


@st.cache(persist=True)
def load_data(nrows):
	data=pd.read_csv(data_url,nrows=nrows,parse_dates=[['CRASH_DATE','CRASH_TIME']])
	data.dropna(subset=['LATITUDE','LONGITUDE'],inplace=True)
	lowercase=lambda x:str(x).lower()
	data.rename(lowercase,axis='columns',inplace=True)
	data.rename(columns={'crash_date_crash_time':'date/time'},inplace=True)
	return data

data=load_data(100000)
original_data=data
original_data2=data


st.header("where are the most people injured in NYC?")
injured_people=st.slider("number of persons injured in vehicle collision",0,19)
st.map(data.query("injured_persons>= @injured_people")[["latitude","longitude"]].dropna(how='any'))


st.header("How many collisions occur during a given time of day?")
hour= st.slider("hour to choose",0,23)
data=data[data['date/time'].dt.hour == hour]


st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour,(hour+1) %24))
midpoint=(np.average(data['latitude']),np.average(data['longitude']))

#3d gragh using pydeck
st.write(pdk.Deck(map_style="mapbox://styles/mapbox/light-v9",
	initial_view_state=
	{
	"latitude":midpoint[0],
	"longitude":midpoint[1],
	"zoom":11,
	"pitch":50,
	},
	layers=[
	pdk.Layer(
		"HexagonLayer",
		data=data[['date/time','latitude','longitude']],
		get_position=['longitude','latitude'],
		radius=100,
		extruded=True,
		pickable=True,
		elevation_scale=4,
		elevation_range=[0,1000],
		),
],
))

#crash by minutes
st.subheader("Breakdown by minute between %i:00 and %i:00" %(hour,(hour+1)%24))
filtered=data[
(data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour <(hour +1))]

hist=np.histogram(filtered['date/time'].dt.minute,bins=60,range=(0,60))[0]
chart_data=pd.DataFrame({'minute':range(60),'crashes': hist})
#chart_data['crashes']

fig=px.bar(chart_data,x='minute',y='crashes',hover_data=['minute','crashes'],height=400)
st.write(fig)



st.subheader("Number of crashes of different districts between %i:00 and %i:00" %(hour,(hour+1)%24))
filtered=filtered[['borough']].dropna(how='any')
#filtered.loc[filtered["borough"]=="QUEENS"]
#hist2=np.histogram(filtered['date/time'],bins=[],range=(0,5))[0]
dis=['MANHATTAN','BROOKLYN','BRONX','QUEENS','STATEN ISLAND']
#count=[filtered.borough.value_counts()[i] for i in dis]
count=filtered['borough'].value_counts()
chart_data2=pd.DataFrame({'districts':dis,'crashes': count})
fig2=px.bar(chart_data2,y='districts',x='crashes',hover_data=['districts','crashes'],text='crashes',color='districts',height=400,orientation='h')
st.write(fig2)



st.header("Top 3 dangerous streets by different groups of people")
select=st.selectbox('groups of people',['Pedestrians','Cyclists','Motorists'])

if select=='Pedestrians':
	st.write(original_data.query("injured_pedestrians >=1")[["on_street_name","injured_pedestrians","CONTRIBUTING_FACTOR_VEHICLE_1".lower()]].sort_values(by=['injured_pedestrians'],ascending=False).dropna(how='any')[:3])

elif select=='Cyclists':
	st.write(original_data.query("injured_cyclists >=1")[["on_street_name","injured_cyclists","CONTRIBUTING_FACTOR_VEHICLE_1".lower()]].sort_values(by=['injured_cyclists'],ascending=False).dropna(how='any')[:3])

elif select=='Motorists':
	st.write(original_data.query("injured_motorists >=1")[["on_street_name","injured_motorists","CONTRIBUTING_FACTOR_VEHICLE_1".lower()]].sort_values(by=['injured_motorists'],ascending=False).dropna(how='any')[:3])


st.header("Top 3 dangerous streets by different district")
select=st.selectbox('select districts',['MANHATTAN','BROOKLYN','BRONX','QUEENS','STATEN ISLAND'])

if select=="QUEENS":
	QUEENS=original_data2.loc[original_data2["borough"]=="QUEENS"]
	st.write(QUEENS.query("injured_persons >=1")[["on_street_name","injured_persons","CONTRIBUTING_FACTOR_VEHICLE_1".lower()]].sort_values(by=['injured_persons'],ascending=False).dropna(how='any')[:3])
elif select=="BROOKLYN":
	BROOKLYN=original_data2.loc[original_data2["borough"]=="BROOKLYN"]
	st.write(BROOKLYN.query("injured_persons >=1")[["on_street_name","injured_persons","CONTRIBUTING_FACTOR_VEHICLE_1".lower()]].sort_values(by=['injured_persons'],ascending=False).dropna(how='any')[:3])
elif select=="MANHATTAN":
	MANHATTAN=original_data2.loc[original_data2["borough"]=="MANHATTAN"]
	st.write(MANHATTAN.query("injured_persons >=1")[["on_street_name","injured_persons","CONTRIBUTING_FACTOR_VEHICLE_1".lower()]].sort_values(by=['injured_persons'],ascending=False).dropna(how='any')[:3])
elif select=="BRONX":
	BRONX=original_data2.loc[original_data2["borough"]=="BRONX"]
	st.write(BRONX.query("injured_persons >=1")[["on_street_name","injured_persons","CONTRIBUTING_FACTOR_VEHICLE_1".lower()]].sort_values(by=['injured_persons'],ascending=False).dropna(how='any')[:3])
else:
	STATENISLAND=original_data2.loc[original_data2["borough"]=="STATEN ISLAND"]
	st.write(STATENISLAND.query("injured_persons >=1")[["on_street_name","injured_persons","CONTRIBUTING_FACTOR_VEHICLE_1".lower()]].sort_values(by=['injured_persons'],ascending=False).dropna(how='any')[:3])




#original_data['VEHICLE_TYPE_1'.lower()]=original_data['VEHICLE_TYPE_1'.lower()].str.lower()
st.header("Number of crashes by different vehicle type")
filtered=original_data[['VEHICLE_TYPE_3'.lower()]].dropna(how='any')
car_type=filtered['VEHICLE_TYPE_3'.lower()].unique()
count=filtered['VEHICLE_TYPE_3'.lower()].value_counts()
chart_data3=pd.DataFrame({'vehicle_type':car_type,'crashes': count})
fig3=px.bar(chart_data3,y='vehicle_type',x='crashes',hover_data=['vehicle_type','crashes'],text='crashes',color='vehicle_type',height=900,width=900,orientation='h')
st.write(fig3)

#max_injured=data['injured_persons'].max()
#st.markdown(max_injured)
if st.checkbox("Show Raw Data",False):
	st.subheader('Raw Data')
	st.write(data)