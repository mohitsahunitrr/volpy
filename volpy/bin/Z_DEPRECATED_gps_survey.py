import pandas as pd
from enum import Enum
from xml.dom.minidom import parse

import plotly
import plotly.offline as po
import plotly.graph_objs as go


class GpsDevice(Enum):
    """An enumeration of known GPS devices."""
    GARMIN_MONTANA_680 = 0

class GpsSurvey(object):

    def __init__(self, name, file_path, device=GpsDevice.GARMIN_MONTANA_680):
        """Constructor for GpsSurvey class
        @params:
        name: string identifier for the survey data
        file_path: the full path to the file containing XML data to
                   import.
        device: an enumeration related to the GPS brand and model since
                different devices can generate data with different
                structure and tags.
        """

        if type(device) != GpsDevice:
            raise TypeError("Invalid device type specified.")
        self.name = name
        self.file_path = file_path
        self.device = device
        self.data = self._read_gpx()

    def view_stats(self):
        """Displays statistical data from GPS survey
        @params:
        gps_data: a pandas DataFrame containing latitude, longitude
                  elevation and time of point capture
        """
        time_to_survey = self.data.index.max()-self.data.index.min()
        print("Time taken for survey completion: {}".format(time_to_survey))
        print("Points collected: {}".format(self.data.shape[0]))
        print("Elevation average: {}".format(self.data['elevation'].mean()))

        self._stats_print('elevation', 'meters')
        self._stats_print('latitude', 'degrees')
        self._stats_print('longitude', 'degrees')

    def _stats_print(self, variable, unit):
        """Prints statistics for given survey variable"""
        maximum = self.data[variable].max()
        minimum = self.data[variable].min()
        range = maximum - minimum
        print("{0} range: {1}. From {2} to {3} {4}.".format(
            variable.title(),
            range,
            minimum,
            maximum,
            unit))

    def _read_gpx(self):
        """Parses an xml file containing GPS data for a specific GPS device
        @params:
        Returns a pandas DataFrame containing the parsed GPS data if parse was
        successful and None otherwise.
        """
        # Note to future self: consider generalizing if other brand/model
        # devices generate similar XML structure.
        if self.device == GpsDevice.GARMIN_MONTANA_680:
            dom_tree = parse(self.file_path)
            collection = dom_tree.documentElement
            track_points = collection.getElementsByTagName("trkpt")

            points = []

            for point in track_points:
                # Parse from XML
                latitude = point.getAttribute("lat")
                longitude = point.getAttribute("lon")
                elevation = point.getElementsByTagName('ele')[0]\
                    .childNodes[0].data
                timestamp = point.getElementsByTagName('time')[0]\
                    .childNodes[0].data

                try:
                    # Data type conversion
                    latitude = pd.to_numeric(latitude)
                    longitude = pd.to_numeric(longitude)
                    elevation = pd.to_numeric(elevation)
                    timestamp = pd.to_datetime(timestamp)
                    entry = (timestamp, latitude, longitude, elevation)
                    points.append(entry)
                except Exception as exception:
                    print(exception)

            column_names = ["timestamp", "latitude", "longitude", "elevation"]
            return pd.DataFrame.from_records(
                points,
                columns=column_names,
                index="timestamp")
        return None

    def view_path_elevation(self):
        """Plots the elevation along the survey path."""
        layout = go.Layout(
            title=self.name,
            xaxis=dict(title='Time'),
            yaxis=dict(title='Elevation (m)'),
            autosize=True)
        trace = go.Scatter(
            x = self.data.index,
            y = self.data['elevation'],
            mode = 'lines+markers',
            name = 'Survey elevation profile'
        )
        po.plot({"data": [trace], "layout": layout})