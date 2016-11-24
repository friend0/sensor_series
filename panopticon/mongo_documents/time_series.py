import pymongo

'''
class ValueSeries(EmbeddedDocument):
    """
    A Value Series is a higher level object for managing ValueSegments.
    Since our data is not always updated periodically, e.g event based updates, and since our data
    will have unknown length, we use the ValueSeries object to track the currently active segment, and also the current
    index for that same segment. The series also stores information on the time of last update, and the latest value
    written to the ValueSegment.
    """

    # Which item are we maintainnig a ValueSeries for?
    _id = LongField()
    item = StringField()
    first_segment_index = LongField()
    last_segment_index = LongField()
    lastValue = LongField(default=-1),
    current_segment_id = LongField("254795601416290304"),
    current_segment_ptr = LongField(default=[0]*160)

class TimeSeries(Document):
    """
    A document to manage all time series data for a robot. Stores a list of embedded Series documents,
    which are high level objects that reference ValueSegments. The Series objects also store information on last
    retrieved value
    """


    # Use the robot's hostname as the object id
    _id = StringField()
    series_trackers = EmbeddedDocumentListField(ValueSeries)
    ListField()

class ValueSegment(Document):
    """
    Currently tuned to store segments of numeric values (long)
    """

    series_id = LongField() # ID for the ValueSeries that owns this segment
    segment_index = LongField()
    first_time = DateTimeField()
    last_time = DateTimeField()
    previous_segment_id = LongField("1390410338000")
    next_segment_id = LongField("1390485108000")
    #time = [NumberLong("1390483902000"), NumberLong("1390483299000"), …],
    #value = [24.5, 26.32, …],
'''


if __name__ == '__main__':
    client = pymongo.MongoClient()

    print(client.database_names())
    for key in client.robots.kuka_robots.find():
        #print(key)
        pass
