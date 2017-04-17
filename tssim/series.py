"""This module contains the TimeSeries"""

import pandas as pd
import itertools

from bokeh.plotting import figure, show, save
from bokeh.palettes import Category10

from . import tracks


class TimeSeriesResult:
    """Contains the result of generated TimeTrack instance.

    """

    def __init__(self, tracks, values):
        self.values = values
        self.tracks = tracks

    def plot(self):
        p = figure(x_axis_type="datetime", width=800)
        p.line(self.values.index, self.values)
        show(p)

    def plot_tracks(self):
        p = figure(x_axis_type="datetime", width=800)
        colors = itertools.cycle(Category10[10])

        for (name, result), color in zip(self.tracks.items(), colors):
            values = result.values
            p.line(values.index, values, color=color, legend=name)
        show(p)


class TimeSeries:
    """Resembles a time series with defined DatetimeIndex. A TimeSeries is 
    defined by adding TimeTracks to it. Each TimeTrack may hold different 
    TimeFunctions which provide values per time interval.
    
    Summing up all time tracks yields the final result of the TimeSeries.
    
    """

    def __init__(self, *args, unit="h", **kwargs):
        """Initialize TimeSeries. All arguments except `unit` are passed to
        pd.DatetimeIndex  to create the actual time index. `unit` defines the
        final time interval.
        
        """

        self.index = pd.DatetimeIndex(*args, **kwargs)
        self.unit = unit
        self.tracks = {}

    def add(self, name, *args, **kwargs):
        """Add a TimeTrack to the current TimeSeries. A name must be given to
        uniquely identify the given track.
        
        """

        if name in self.tracks:
            raise ValueError("TimeTrack with name '{}' is already given.")

        self.tracks[name] = tracks.TimeTrack(self, *args, **kwargs)

    def generate(self):
        """Generate actual time series values for all TimeTracks. Return 
        TimeSeriesResult with TimeTracks definitions and summed time series
        values of all TimeTracks.
        
        """

        tracks = {name: track.generate() for name, track in self.tracks.items()}
        track_values = [x.values for x in tracks.values()]
        time_series_values = pd.concat(track_values, axis=1).sum(axis=1)

        return TimeSeriesResult(tracks, time_series_values)

    def __getitem__(self, item):
        """Provide convenient label access to TimeTracks of current TimeSeries.

        """

        return self.tracks[item]

    def __repr__(self):
        """Provide convenient print representation.
        
        """
        tpl = "{} ({})"

        return tpl.format(self.__class__.__name__, self.tracks)
