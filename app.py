# -*- coding: utf-8 -*-
"""
Created on Tue May  2 06:20:47 2023

@author: nicog
"""

import pandas as pd
import plotly.express as px
import streamlit as st

url = 'https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv'

@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    return df

# Load data
df = load_data(url)

# remove unwanted items from 'country' column
to_remove_from_country = list(df[df['iso_code'].isna() & df['gdp'].isna()]['country'].drop_duplicates())
to_remove_from_country.remove('Czechoslovakia')
to_remove_from_country.remove('Kosovo')
to_remove_from_country.remove('Yugoslavia')
to_remove_from_country.remove('USSR')

df.drop(df[df['country'].isin(to_remove_from_country)].index, axis=0, inplace=True)






# description columns
main_cols = df.columns[:5]

# subset of columns used in this analysis
consumption_cols = [col for col in df.columns if 'consumption' in col]
consumption_type_cols = consumption_cols.copy()
# consumption_type_cols.remove('fossil_fuel_consumption')
for item in ['fossil_fuel_consumption', 'low_carbon_consumption', 'other_renewable_consumption', 
                        'primary_energy_consumption', 'renewables_consumption']:
    consumption_type_cols.remove(item)
    
df_consumption = df[[*main_cols, *consumption_type_cols]]
# df_consumption
# # convert energy from terawatt-hour to kWatt-hour
# df_consumption[consumption_type_cols] *= 10e9
# df_consumption
df_consumption = df_consumption.assign(total_energy_consumption = df_consumption.loc[:, consumption_type_cols].sum(axis=1))

# streamlit setup
st.header('World Energy Consumption')
st.markdown('https://github.com/owid/energy-data/blob/master/owid-energy-codebook.csv')
st.sidebar.header('Plots Options') 
min_value=min(df_consumption['year'])
max_value=max(df_consumption['year'])
value = (min_value, max_value)
year_min, year_max = st.sidebar.slider('Year', min_value, max_value, value)
country = st.sidebar.multiselect('Select countries', 
                                 df_consumption['country'].unique(),
                                 default='United States')

# filter df by years and countries
plot_df01 = df_consumption.loc[(df_consumption['year'] >= year_min) &
                                (df_consumption['year'] <= year_max) &
                                (df_consumption['country'].isin(country))]

# filter df by years
plot_df02 = df_consumption.loc[(df_consumption['year'] >= year_min) &
                                (df_consumption['year'] <= year_max)]

# group filtered df 02 by country and mean
plot_df03 = plot_df02.groupby('country', as_index=False).mean()

# Total energy by country by Year
st.sidebar.subheader('Total Energy by Country per Capita by Year')
if not st.sidebar.checkbox('Hide', False, key='checkbox01'):
    st.subheader('Total Energy by Country per Capita by Year')

    fig01 = px.line(plot_df01, x='year', y=plot_df01['total_energy_consumption']/plot_df01['population']*10e6,
                    color = 'country')
    fig01.update_layout(
        # title="Plot Title",
        xaxis_title="Year",
        yaxis_title="Total Energy per Capita [MWh/person]",
        legend_title="Country",
        # font=dict(
        #     family="Courier New, monospace",
        #     size=18,
        #     color="RebeccaPurple"
        # )
    )
    st.plotly_chart(fig01)
    
# Population vs GDP
st.sidebar.subheader('Population vs GDP')
if not st.sidebar.checkbox('Hide', False, key='checkbox02'):
    st.subheader('Population vs GDP')

    fig02 = px.scatter(plot_df03,
                       x='gdp',
                       y='population',
                       hover_name='country')
    
    st.plotly_chart(fig02)
    
# Population vs Total Energy Consumption
st.sidebar.subheader('Population vs Total Energy Consumption')
if not st.sidebar.checkbox('Hide', False, key='checkbox03'):
    st.subheader('Population vs Total Energy Consumption')
    
    fig03 = px.scatter(plot_df03,
                       x='total_energy_consumption',
                       y='population',
                       hover_name='country')
    
    st.plotly_chart(fig03)
    
# Average energy by country per Capita
st.sidebar.subheader('Average Energy by Country per Capita')
if not st.sidebar.checkbox('Hide', False, key='checkbox04'):
    st.subheader('Average Energy by Country per Capita')
    no_countries_04 = 10
    st.markdown(f"Average energy consumption of top {no_countries_04} countries between {year_min} and {year_max}")
    
    plot_df_fig04 = pd.DataFrame([plot_df03['country'], 
                      plot_df03['total_energy_consumption']/plot_df03['population']*10e6]).T
    plot_df_fig04.columns = ['Country', 'Energy_per_Capita_MWh']
    plot_df_fig04.sort_values(by='Energy_per_Capita_MWh', ascending=False, inplace=True)
    
    
    no_countries_04 = st.slider('How many Countries?', 
                                                   # min_value=0, 
                                                   max_value=int(plot_df_fig04.Country.count()),
                                                   value=no_countries_04,
                                                   key='slider04')
    
    # update df based on slider selection
    plot_df_fig04 = plot_df_fig04.head(no_countries_04)

    
    fig04 = px.scatter(plot_df_fig04, x='Energy_per_Capita_MWh',
                    y='Country',
                    color = 'Country')
    fig04.update_layout(
        # title="Plot Title",
        xaxis_title="Total Energy per Capita [MWh/person]",
        yaxis_title="Country",
        legend_title="Country",
        yaxis={'dtick':1},
        height = max(16*no_countries_04, 400),
        showlegend=False
        # font=dict(
        #     family="Courier New, monospace",
        #     size=18,
        #     color="RebeccaPurple"
        # )
    )
    st.plotly_chart(fig04)
    
# Average gdp by country per Capita
st.sidebar.subheader('Average GDP by Country per Capita')
if not st.sidebar.checkbox('Hide', False, key='checkbox05'):
    st.subheader('Average GDP by Country per Capita')
    no_countries_05 = 10
    st.markdown(f"Average energy consumption of top {no_countries_05} countries between {year_min} and {year_max}")
    
    plot_df_fig05 = pd.DataFrame([plot_df03['country'], plot_df03['gdp']/plot_df03['population']]).T
    plot_df_fig05.columns = ['Country', 'Avg_gdp_per_Capita']
    plot_df_fig05.sort_values(by='Avg_gdp_per_Capita', ascending=False, inplace=True)
    
    
    no_countries_05 = st.slider('How many Countries?', 
                                                   # min_value=0, 
                                                   max_value=int(plot_df_fig05.Country.count()),
                                                   value=no_countries_05,
                                                   key='slider05')
    
    # update df based on slider selection
    plot_df_fig05 = plot_df_fig05.head(no_countries_05)

    
    fig05 = px.scatter(plot_df_fig05, x='Avg_gdp_per_Capita',
                    y='Country',
                    color = 'Country')
    fig05.update_layout(
        # title="Plot Title",
        xaxis_title="Average GDP per Capita [USD]",
        yaxis_title="Country",
        legend_title="Country",
        yaxis={'dtick':1},
        height = max(400, 16*no_countries_05),
        showlegend=False
        # font=dict(
        #     family="Courier New, monospace",
        #     size=18,
        #     color="RebeccaPurple"
        # )
    )
    st.plotly_chart(fig05)
    
# Global Energy Consumption by Type and Year
st.sidebar.subheader('Global Energy Consumption by Type and Year')
if not st.sidebar.checkbox('Hide', False, key='checkbox06'):
    st.subheader('Global Energy Consumption by Type and Year')
    nl = '\n'
    st.markdown("Global energy consumption of:")
    st.markdown(f"   {', '.join(country)}")
    st.markdown(f" between {year_min} and {year_max} by type of energy")
   

    fig06 = px.bar(plot_df01,
                   x='year',
                   y=consumption_type_cols)
    fig06.update_layout(
        # title="Plot Title",
        xaxis_title="Year",
        yaxis_title="Energy COnsumption [MWh]",
        legend_title="Type of Energy",
        # yaxis={'dtick':1},
        # height = max(400, 16*no_countries_05),
        # showlegend=False
    )
    
    st.plotly_chart(fig06)