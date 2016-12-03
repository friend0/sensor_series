import attr
import datetime

# todo: most of the decode methods are broken/do not reflect current objects.
@attr.s
class TimeSeries():

    id = attr.ib(default=None)
    robot = attr.ib(default='BIW{}-{}{}')
    series = attr.ib(attr.Factory(dict))


    def encode(self):
        return {'_id':self.id, 'robot': self.robot, 'series': self.series, 'type': 'TimeSeries'}


    @staticmethod
    def decode(document):
        assert document["_type"] == "time_series"
        return TimeSeries(robot=document['robot'], _type=document['type'], series_trackers=document['series_trackers'])

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

    current_segment_id = attr.ib(default=None)
    current_segment_ptr = attr.ib(default=180)
    first_segment_id = attr.ib(default=None)

    last_value = attr.ib(None)
    last_time = attr.ib(datetime.datetime(year=1989, month=6, day=13))
    # todo: figure out a simple way to get first_time to work. Time of instantiation, and time of first insertion are not the same.
    #first_time = attr.ib(year=1989, month=6, day=13)

    def encode(self):
        return {'current_segment_id': self.current_segment_id, 'current_segment_ptr':self.current_segment_ptr,
                'first_segment_id': self.first_segment_id, 'last_value': self.last_value, 'last_time': self.last_time}


    @staticmethod
    def decode(document):
        # todo: write the decoding function. The one below is not correct.
        assert document["_type"] == "time_series"
        return TimeSeries(robot=document['robot'], _type=document['type'], series_trackers=document['series_trackers'])


@attr.s
class ValueSegment():
    """
    Currently tuned to store segments of numeric values (long)
    """

    series_id = attr.ib(default=None) # ID for the ValueSeries that owns this segment
    segment_id = attr.ib(default=0)

    first_time = attr.ib(default=datetime.datetime.now())
    last_time = attr.ib(default=datetime.datetime.now())
    previous_id = attr.ib(default=int())
    next_id = attr.ib(default=int())
    times = attr.ib(default=[datetime.datetime(year=1989, month=6, day=13) for x in range(160)])
    values = attr.ib(default=[int(0)]*160)

    def encode(self):
        # todo: complete this encoding with all attributes
        return {'series_id': self.series_id,  'previous_id': self.previous_id, 'times': self.times,
                'values': self.values, 'first_time': self.first_time, 'last_time': self.last_time}