import geopandas as gpd
import geoplot
import geoplot.crs as gcrs
import matplotlib.pyplot as plt
import mapclassify
import pandas as pd
import json
from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import brewer
import numpy as np
import datetime


def get_data():
    # shapefile = 'ne_110m_states/ne_110m_admin_1_states_provinces.shp'
    # shapefile = 'cb_2018_us_cd116_500k/cb_2018_us_cd116_500k.shp'
    shapefile = 'cb_2018_us_state_5m/cb_2018_us_state_5m.shp'

    gdf = gpd.read_file(shapefile)[['NAME', 'geometry']]
    gdf.columns = ['name', 'geometry']
    #gdf_o = gdf.drop([39, 47, 48, 49, 51], axis=0)

    states_data = pd.read_csv('StatesData.csv', names=['abbr', 'name', '2010pop', '2019pop', 'LandArea'], skiprows=1)
    merged = gdf.merge(states_data, on='name', how='outer')

    gpd_plot(shapefile, merged)

    return merged


def gpd_plot(shapefile, data):
    us = gpd.read_file(shapefile)
    pop_density = data['2019pop']/data['LandArea']
    scheme = mapclassify.Quantiles(pop_density, k=10)
    geoplot.choropleth(us, hue=pop_density, scheme=scheme, cmap='Greens')
    plt.show()


def plot_map(data):
    merged_json = json.loads(data.to_json())
    json_data = json.dumps(merged_json)

    geosource = GeoJSONDataSource(geojson=json_data)

    palette = brewer['YlGnBu'][8]
    palette = palette[::-1]

    #Define custom tick labels for color bar.
    tick_labels = {'0': '0%', '5': '5%', '10':'10%', '15':'15%', '20':'20%', '25':'25%', '30':'30%','35':'35%', '40': '>40%'}

    color_mapper = LinearColorMapper(palette=palette, low=0, high=51)
    # color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, width=500, height=20, border_line_color=None,
    #                      location=(0, 0), orientation='horizontal', major_label_overrides=tick_labels)
    color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8, width=500, height=20, border_line_color=None,
                         location=(0, 0), orientation='horizontal')

    p = figure(title='Random Numbers', plot_height=600, plot_width=950, toolbar_location=None)

    # Add patch renderer to figure.
    p.patches(xs='xs', ys='ys', source=geosource, fill_color={'field': 'data', 'transform': color_mapper},
              line_color='black', line_width=0.25, fill_alpha=0.8)

    p.xgrid.grid_line_color = None
    p.ygrid.grid_line_color = None

    p.add_layout(color_bar, 'below')

    show(p)


def get_polling_data():
    pp = pd.read_csv('polls/president_polls.csv')
    # print(list(pp.columns))
    # print(pp['end_date'].head())
    date_after = datetime.datetime(2020, 3, 18)
    pp_now = pp[pd.to_datetime(pp['end_date']) > date_after]

    # Calculate National polling average (if president_polls['state'] == 'NaN')
    states, poll_avg = print_state_means(pp_now)

    return states, poll_avg


def print_state_means(pp):
    # Break into Republican and Democratic numbers
    pp_r = pp[pp['candidate_party'] == 'REP']
    pp_d = pp[pp['candidate_party'] == 'DEM']

    states = []
    poll_avg = []

    # For each state, calculate polling average
    for state in pp.state.unique():
        print('##########################################')

        if pd.isna(state):
            state = "Country"

        # print(state)
        d_means = []
        r_means = []
        dates = []
        for (date_after, date_before) in get_date_limits():
            pp_low_thresh = pp[pd.to_datetime(pp['end_date']) >= date_after]
            pp_bp = pp_low_thresh[pd.to_datetime(pp_low_thresh['end_date']) <= date_before]
            # print('Republican')
            pp_now_r = pp_bp[pp_bp['candidate_party'] == 'REP']
            r_mean = pp_now_r[pp_now_r['state'] == state]['pct'].mean()
            # print(r_mean)
            r_means.append(r_mean)
            # print('Democrat')
            pp_now_d = pp_bp[pp_bp['candidate_party'] == 'DEM']
            d_mean = pp_now_d[pp_now_d['state'] == state]['pct'].mean()
            # print(d_mean)
            d_means.append(d_mean)
            dates.append(date_before)

        # plt.plot(dates, d_means)
        # plt.plot(dates, r_means)
        # plt.title(state)
        # plt.show()

        d_mean_a = d_mean
        r_mean_a = r_mean
        if np.isnan(d_mean_a):
            d_mean_a = np.nanmean(d_means)
        if np.isnan(r_mean_a):
            r_mean_a = np.nanmean(r_means)

        print(state)
        print(d_mean_a - r_mean_a)

        if state == "Nebraska CD-2":
            state = "Nebraska"
            print(state)

        if state is not "Country":
            states.append(state)
            poll_avg.append(d_mean_a-r_mean_a)

    return states, poll_avg


def get_date_limits():
    start_date = datetime.datetime(2020, 3, 18)
    end_date = datetime.datetime(2020, 7, 28)
    day_iter = datetime.timedelta(days=1)
    while start_date < end_date-20*day_iter:
        start_date += day_iter
        yield start_date, start_date + 20*day_iter


def plot_vote(states, poll_avg):
    shapefile = 'cb_2018_us_state_5m/cb_2018_us_state_5m.shp'

    gdf = gpd.read_file(shapefile)[['NAME', 'geometry']]
    gdf.columns = ['name', 'geometry']

    poll_avg_df = pd.DataFrame({'name': states, 'poll_avg': poll_avg})

    data = gdf.merge(poll_avg_df, on='name', how='right')
    # data['poll_avg'].fillna(value=0)
    print(data)
    print(data['geometry'])

    scheme = mapclassify.Quantiles(data['poll_avg'], k=7)
    geoplot.choropleth(data, hue=data['poll_avg'], scheme=scheme, legend=True)
    plt.show()

    return


# data = get_data()
# plot_map(data)
states, poll_avg = get_polling_data()
plot_vote(states, poll_avg)
