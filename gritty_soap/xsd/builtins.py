"""
    Primitive datatypes
     - string
     - boolean
     - decimal
     - float
     - double
     - duration
     - dateTime
     - time
     - date
     - gYearMonth
     - gYear
     - gMonthDay
     - gDay
     - gMonth
     - hexBinary
     - base64Binary
     - anyURI
     - QName
     - NOTATION

    Derived datatypes
     - normalizedString
     - token
     - language
     - NMTOKEN
     - NMTOKENS
     - Name
     - NCName
     - ID
     - IDREF
     - IDREFS
     - ENTITY
     - ENTITIES
     - integer
     - nonPositiveInteger
     - negativeInteger
     - long
     - int
     - short
     - byte
     - nonNegativeInteger
     - unsignedLong
     - unsignedInt
     - unsignedShort
     - unsignedByte
     - positiveInteger


"""
from __future__ import division

import base64
import math
import re
from decimal import Decimal as _Decimal

import isodate
import pytz
import six
from lxml import etree

from gritty_soap.utils import qname_attr
from gritty_soap.xsd.elements import Base
from gritty_soap.xsd.types import SimpleType
from gritty_soap.xsd.valueobjects import AnyObject



class ParseError(ValueError):
    pass


class _BuiltinType(SimpleType):
    def __init__(self, qname=None, is_global=False):
        super(_BuiltinType, self).__init__(
            qname or etree.QName(self._default_qname), is_global)

    def signature(self, depth=0):
        return 'xsd:%s' % self.name

##
# Primitive types


class String(_BuiltinType):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}string'

    def xmlvalue(self, value):
        return six.text_type(value if value is not None else '')

    def pythonvalue(self, value):
        return value


class Boolean(_BuiltinType):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}boolean'

    def xmlvalue(self, value):
        return 'true' if value else 'false'

    def pythonvalue(self, value):
        """Return True if the 'true' or '1'. 'false' and '0' are legal false
        values, but we consider everything not true as false.

        """
        return value in ('true', '1')


class Decimal(_BuiltinType):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}decimal'

    def xmlvalue(self, value):
        return str(value)

    def pythonvalue(self, value):
        return _Decimal(value)


class Float(_BuiltinType):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}float'

    def xmlvalue(self, value):
        return str(value).upper()

    def pythonvalue(self, value):
        return float(value)


class Double(_BuiltinType):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}double'

    def xmlvalue(self, value):
        return str(value)

    def pythonvalue(self, value):
        return float(value)


class Duration(_BuiltinType):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}duration'

    def xmlvalue(self, value):
        return isodate.duration_isoformat(value)

    def pythonvalue(self, value):
        return isodate.parse_duration(value)


class DateTime(_BuiltinType):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}dateTime'

    def xmlvalue(self, value):
        return isodate.isostrf.strftime(value, '%Y-%m-%dT%H:%M:%S%Z')

    def pythonvalue(self, value):
        return isodate.parse_datetime(value)


class Time(_BuiltinType):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}time'

    def xmlvalue(self, value):
        return isodate.isostrf.strftime(value, '%H:%M:%S%Z')

    def pythonvalue(self, value):
        return isodate.parse_time(value)


class Date(_BuiltinType):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}date'

    def xmlvalue(self, value):
        return isodate.isostrf.strftime(value, '%Y-%m-%d')

    def pythonvalue(self, value):
        return isodate.parse_date(value)


class gYearMonth(_BuiltinType):
    """gYearMonth represents a specific gregorian month in a specific gregorian
    year.

    Lexical representation: CCYY-MM

    """
    _default_qname = '{http://www.w3.org/2001/XMLSchema}gYearMonth'
    _pattern = re.compile(
        r'^(?P<year>-?\d{4,})-(?P<month>\d\d)(?P<timezone>Z|[-+]\d\d:?\d\d)?$')

    def xmlvalue(self, value):
        year, month, tzinfo = value
        return '%04d-%02d%s' % (year, month, _unparse_timezone(tzinfo))

    def pythonvalue(self, value):
        match = self._pattern.match(value)
        if not match:
            raise ParseError()
        group = match.groupdict()
        return (
            int(group['year']), int(group['month']),
            _parse_timezone(group['timezone']))


class gYear(_BuiltinType):
    """gYear represents a gregorian calendar year.

    Lexical representation: CCYY

    """
    _default_qname = '{http://www.w3.org/2001/XMLSchema}gYear'
    _pattern = re.compile(r'^(?P<year>-?\d{4,})(?P<timezone>Z|[-+]\d\d:?\d\d)?$')

    def xmlvalue(self, value):
        year, tzinfo = value
        return '%04d%s' % (year, _unparse_timezone(tzinfo))

    def pythonvalue(self, value):
        match = self._pattern.match(value)
        if not match:
            raise ParseError()
        group = match.groupdict()
        return (int(group['year']), _parse_timezone(group['timezone']))


class gMonthDay(_BuiltinType):
    """gMonthDay is a gregorian date that recurs, specifically a day of the
    year such as the third of May.

    Lexical representation: --MM-DD

    """

    _default_qname = '{http://www.w3.org/2001/XMLSchema}gMonthDay'
    _pattern = re.compile(
        r'^--(?P<month>\d\d)-(?P<day>\d\d)(?P<timezone>Z|[-+]\d\d:?\d\d)?$')

    def xmlvalue(self, value):
        month, day, tzinfo = value
        return '--%02d-%02d%s' % (month, day, _unparse_timezone(tzinfo))

    def pythonvalue(self, value):
        match = self._pattern.match(value)
        if not match:
            raise ParseError()

        group = match.groupdict()
        return (
            int(group['month']), int(group['day']),
            _parse_timezone(group['timezone']))


class gDay(_BuiltinType):
    """gDay is a gregorian day that recurs, specifically a day of the month
    such as the 5th of the month

    Lexical representation: ---DD

    """
    _default_qname = '{http://www.w3.org/2001/XMLSchema}gDay'
    _pattern = re.compile(r'^---(?P<day>\d\d)(?P<timezone>Z|[-+]\d\d:?\d\d)?$')

    def xmlvalue(self, value):
        day, tzinfo = value
        return '---%02d%s' % (day, _unparse_timezone(tzinfo))

    def pythonvalue(self, value):
        match = self._pattern.match(value)
        if not match:
            raise ParseError()
        group = match.groupdict()
        return (int(group['day']), _parse_timezone(group['timezone']))


class gMonth(_BuiltinType):
    """gMonth is a gregorian month that recurs every year.

    Lexical representation: --MM

    """
    _default_qname = '{http://www.w3.org/2001/XMLSchema}gMonth'
    _pattern = re.compile(r'^--(?P<month>\d\d)(?P<timezone>Z|[-+]\d\d:?\d\d)?$')

    def xmlvalue(self, value):
        month, tzinfo = value
        return '--%d%s' % (month, _unparse_timezone(tzinfo))

    def pythonvalue(self, value):
        match = self._pattern.match(value)
        if not match:
            raise ParseError()
        group = match.groupdict()
        return (int(group['month']), _parse_timezone(group['timezone']))


class HexBinary(_BuiltinType):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}hexBinary'

    def xmlvalue(self, value):
        return value

    def pythonvalue(self, value):
        return value


class Base64Binary(_BuiltinType):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}base64Binary'

    def xmlvalue(self, value):
        return base64.b64encode(value)

    def pythonvalue(self, value):
        return base64.b64decode(value)


class AnyURI(_BuiltinType):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}anyURI'

    def xmlvalue(self, value):
        return value

    def pythonvalue(self, value):
        return value


class QName(_BuiltinType):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}QName'


class Notation(_BuiltinType):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}NOTATION'


##
# Derived datatypes

class NormalizedString(String):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}normalizedString'


class Token(NormalizedString):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}token'


class Language(Token):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}language'


class NmToken(Token):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}NMTOKEN'


class NmTokens(NmToken):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}NMTOKENS'


class Name(Token):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}Name'


class NCName(Name):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}NCName'


class ID(NCName):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}ID'


class IDREF(NCName):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}IDREF'


class IDREFS(IDREF):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}IDREFS'


class Entity(NCName):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}ENTITY'


class Entities(Entity):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}ENTITIES'


class Integer(Decimal):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}integer'

    def xmlvalue(self, value):
        return str(value)

    def pythonvalue(self, value):
        return int(value)


class NonPositiveInteger(Integer):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}nonPositiveInteger'


class NegativeInteger(Integer):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}negativeInteger'


class Long(Integer):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}long'

    def pythonvalue(self, value):
        return long(value) if six.PY2 else int(value)


class Int(Long):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}int'


class Short(Int):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}short'


class Byte(Short):
    """A signed 8-bit integer"""
    _default_qname = '{http://www.w3.org/2001/XMLSchema}byte'


class NonNegativeInteger(Integer):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}nonNegativeInteger'


class UnsignedLong(NonNegativeInteger):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}unsignedLong'


class UnsignedInt(UnsignedLong):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}unsignedInt'


class UnsignedShort(UnsignedInt):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}unsignedShort'


class UnsignedByte(UnsignedShort):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}unsignedByte'


class PositiveInteger(NonNegativeInteger):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}positiveInteger'


##
# Other

class AnyType(_BuiltinType):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}anyType'

    def render(self, parent, value):
        if isinstance(value, AnyObject):
            value.xsd_type.render(parent, value.value)
        else:
            parent.text = self.xmlvalue(value)

    def parse_xmlelement(self, xmlelement, schema=None, allow_none=True,
                         context=None):
        xsi_type = qname_attr(
            xmlelement,
            '{http://www.w3.org/2001/XMLSchema-instance}type')
        if xsi_type and schema:
            xsd_type = schema.get_type(xsi_type)
            return xsd_type.parse_xmlelement(
                xmlelement, schema, context=context)

        if xmlelement.text is None:
            return
        return self.pythonvalue(xmlelement.text)

    def xmlvalue(self, value):
        return value

    def pythonvalue(self, value, schema=None):
        return value


class AnySimpleType(AnyType):
    _default_qname = '{http://www.w3.org/2001/XMLSchema}anySimpleType'


def _parse_timezone(val):
    """Return a pytz.tzinfo object"""
    if not val:
        return

    if val == 'Z' or val == '+00:00':
        return pytz.utc

    negative = val.startswith('-')
    minutes = int(val[-2:])
    minutes += int(val[1:3]) * 60

    if negative:
        minutes = 0 - minutes
    return pytz.FixedOffset(minutes)


def _unparse_timezone(tzinfo):
    if not tzinfo:
        return ''

    if tzinfo == pytz.utc:
        return 'Z'

    hours = math.floor(tzinfo._minutes / 60)
    minutes = tzinfo._minutes % 60

    if hours > 0:
        return '+%02d:%02d' % (hours, minutes)
    return '-%02d:%02d' % (abs(hours), minutes)


default_types = {
    cls._default_qname: cls() for cls in [
        # Primitive
        String,
        Boolean,
        Decimal,
        Float,
        Double,
        Duration,
        DateTime,
        Time,
        Date,
        gYearMonth,
        gYear,
        gMonthDay,
        gDay,
        gMonth,
        HexBinary,
        Base64Binary,
        AnyURI,
        QName,
        Notation,

        # Derived
        NormalizedString,
        Token,
        Language,
        NmToken,
        NmTokens,
        Name,
        NCName,
        ID,
        IDREF,
        IDREFS,
        Entity,
        Entities,
        Integer,
        NonPositiveInteger,  # noqa
        NegativeInteger,
        Long,
        Int,
        Short,
        Byte,
        NonNegativeInteger,  # noqa
        UnsignedByte,
        UnsignedInt,
        UnsignedLong,
        UnsignedShort,
        PositiveInteger,

        # Other
        AnyType,
        AnySimpleType,
    ]
}


class Schema(Base):
    name = 'schema'
    qname = '{http://www.w3.org/2001/XMLSchema}schema'

    def clone(self, qname, min_occurs=1, max_occurs=1):
        return self.__class__()

    def parse_kwargs(self, kwargs, name=None):
        if name in kwargs:
            value = kwargs.pop(name)
            return {name: value}, kwargs
        return {}, kwargs

    def parse(self, xmlelement, schema, context=None):
        from zeep.xsd.schema import Schema
        schema = Schema(xmlelement, schema._transport)
        context.schemas.append(schema)
        return schema

    def parse_xmlelements(self, xmlelements, schema, name=None, context=None):
        if xmlelements[0].tag == self.qname:
            xmlelement = xmlelements.pop(0)
            result = self.parse(xmlelement, schema, context=context)
            return result

    def resolve(self):
        return self


default_elements = {
    '{http://www.w3.org/2001/XMLSchema}schema': Schema(),
}
