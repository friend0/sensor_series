from collections import OrderedDict

from pyOPC.gritty_soap.xsd.valueobjects import CompoundValue


def serialize_object(obj):
    """Serialize gritty_soap objects to native python data structures"""
    if obj is None:
        return obj

    if isinstance(obj, list):
        return [serialize_object(sub) for sub in obj]

    result = OrderedDict()
    for key in obj:
        value = obj[key]
        if isinstance(value, (list, CompoundValue)):
            value = serialize_object(value)
        result[key] = value
    return result
