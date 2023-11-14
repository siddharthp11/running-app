import gpxpy
import gpxpy.gpx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from collections import defaultdict
from io import StringIO


def parse_gpx(file):
    gpx = StringIO(file.getvalue().decode("utf-8")).read()
    parsed_gpx = gpxpy.parse(gpx)
    return parsed_gpx


def format_data(gpx):
    data = defaultdict(list)
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                for ext in point.extensions:
                    data[ext.tag].append(float(ext.text))
    return data


# util functions
def mps_to_mins_per_km(mps): return (1 / 60) / (mps/1000)
def secs_to_mins(secs): return round(secs / 60, 3)

# Given a list of distance (in meters) covered each second, and an interval in meters, calculate the pace (mins/km) for each interval


def get_pace_for_intervals(speeds, interval=1000):
    def get_pace_for_interval(cum_seconds, interval_length):
        minutes = secs_to_mins(cum_seconds)
        adjusted_pace = minutes * (1000/interval_length)
        return round(adjusted_pace, 2)

    paces = []
    intervals = []

    cum_dist, cum_secs = 0, 0
    for mps in speeds:
        cum_dist += mps
        cum_secs += 1

        if cum_dist >= interval:
            adjusted_pace = get_pace_for_interval(cum_secs, interval)
            paces.append(adjusted_pace)
            intervals.append(len(intervals) + 1)
            cum_dist, cum_secs = 0, 0

    if cum_dist > 0:
        adjusted_pace = get_pace_for_interval(cum_secs, cum_dist)
        adjusted_interval = round(len(intervals) + cum_dist/interval, 2)

        paces.append(adjusted_pace)
        intervals.append(adjusted_interval)

    return pd.DataFrame.from_dict({
        'interval': intervals,
        'paces': paces
    })


def plot_paces(paces, interval_length):
    fig, ax = plt.subplots()
    adjusted_distance = np.arange(len(paces)) * interval_length/1000
    ax.plot(adjusted_distance, paces)
    ax.set_xlabel('distance (km)')
    ax.set_ylabel('pace (mins/km)')
    return fig


class Plotter:
    def create_pace_plot(filepath, interval):
        workout = parse_gpx(filepath)
        data = format_data(workout)
        df = get_pace_for_intervals(data['speed'], interval)

        return plot_paces(df['paces'], interval)
