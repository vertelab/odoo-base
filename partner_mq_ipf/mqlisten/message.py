import sys
import xmltodict


def parse_message(message):
    xml = None
    try:
        xml = xmltodict.parse(message, dict_constructor=dict)

        if (
            not isinstance(xml, dict)
            or not "msg" in xml.keys()
            or not isinstance(xml["msg"], dict)
            or not "key" in xml["msg"].keys()
            or not "data" in xml["msg"].keys()
        ):
            print("Incorrect XML format: %s" % message)
    except:
        # log parse error
        # ex = sys.exc_info()
        # print("Oops! %s occurred: %s" % (ex[0], ex[1]))
        print("Illegal XML format: '%s'" % message)

    return xml

