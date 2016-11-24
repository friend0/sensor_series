import attr
import datetime


@attr.s
class TimeSeries():


    robot = attr.ib(default='BIW{}-{}{}')
    series = attr.ib(attr.Factory(dict))


    def encode(self):
        return {'robot': self.robot, 'series_set': self.series, 'type': 'TimeSeries'}


    @staticmethod
    def decode(document):
        assert document["_type"] == "time_series"
        return TimeSeries(robot=document['robot'], _type=document['type'], series_trackers=document['series_trackers'])


@attr.s
class ValueSegment():
    """
    Currently tuned to store segments of numeric values (long)
    """

    segment_idx = attr.ib(default=0)

    times = attr.ib(default=[datetime.datetime(year=1989, month=6, day=13) for x in range(180)])
    values = attr.ib(default=[int(0)]*180)

    def encode(self):
        # todo: complete this encoding with all attributes
        return {'series_idx': self.segment_idx, 'times': self.times, 'values': self.values}

@attr.s
class Series():
    """
    A Value Series is a higher level object for managing ValueSegments.
    Since our data is not always updated periodically, e.g event based updates, and since our data
    will have unknown length, we use the ValueSeries object to track the currently active segment, and also the current
    index for that same segment. The series also stores information on the time of last update, and the latest value
    written to the ValueSegment.
    """

    #num_segments = attr.ib(default=0)
    #min_time = attr.ib(default=None)
    #first_segment = attr.ib(default=None)
    #last_segment = attr.ib(default=None)
    #last_value = attr.ib(default=None)

    # Which item are we maintainig a ValueSeries for?

    item = attr.ib()
    current_segment_idx = attr.ib(default=0)
    current_segment_ptr = attr.ib(default=180)
    value_segments = attr.ib(default=[ValueSegment(segment_idx=0)])

    last_value = attr.ib(None)
    last_time = attr.ib(datetime.datetime(year=1989, month=6, day=13))

    def encode(self):
        return {'current_segment_idx': self.current_segment_idx, 'current_segment_ptr':self.current_segment_ptr,
                'last_value': self.last_value, 'last_time': self.last_time, 'value_segments': [value_segment.encode() if isinstance(value_segment, ValueSegment) else None for value_segment in self.value_segments ]}


    @staticmethod
    def decode(document):
        # todo: write the decoding function. The one below is not correct.
        assert document["_type"] == "time_series"
        return TimeSeries(robot=document['robot'], _type=document['type'], series_trackers=document['series_trackers'])


