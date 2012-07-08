from iso8601 import parse_date


def convertStringToDateTime(input):
    return parse_date(input).replace(tzinfo=None)
