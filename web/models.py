import datetime

from mongoengine import Document
from mongoengine import DateTimeField, StringField, BooleanField, ReferenceField, ListField, FileField, ImageField


# todo: need to update this to reflect reality. Used as placeholder for now.

class Robot(Document):
    title = StringField(max_length=60)
    text = StringField()
    done = BooleanField(default=False)
    pub_date = DateTimeField(default=datetime.datetime.now)

"""
class Contact(Document):
    name = StringField(max_length=60, required=True, unique=True)
    address = StringField(max_length=60)
    birthday = DateTimeField()
    personal_phone = StringField(max_length=20)
    personal_celphone = StringField(max_length=20)
    contact_group = ReferenceField(ContactGroup, required=True)
    gender = ReferenceField(Gender, required=True)
    tags = ListField(ReferenceField(Tags))

    def month_year(self):
        date = self.birthday or mindate
        return datetime.datetime(date.year, date.month, 1) or mindate

    def year(self):
        date = self.birthday or mindate
        return datetime.datetime(date.year, 1, 1)

    def __repr__(self):
        return "%s : %s\n" % (self.name, self.contact_group)
"""
