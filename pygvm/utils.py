# coding: utf-8
import xml.etree.ElementTree as ET
import collections
import six


def str_to_lxml(Str):
    return ET.XML(Str)


def lxml_to_dict(tree):
    try:
        dct = {tree.tag: {} if tree.attrib else None}
    except AttributeError:
        raise TypeError("tree must be an XML ElementTree")

    children = list(tree)
    if children:
        default_dict = collections.defaultdict(list)
        for child in [lxml_to_dict(child) for child in children]:
            if child:
                for key, value in six.iteritems(child):
                    default_dict[key].append(value)
        dct = {tree.tag: {key: value[0] if len(value) == 1 else value
                          for key, value in six.iteritems(default_dict)}}
    if tree.attrib:
        dct[tree.tag].update(("@" + key, value)
                             for key, value in six.iteritems(tree.attrib))
    if tree.text:
        text = tree.text.strip()
        if children or tree.attrib:
            dct[tree.tag]["#text"] = text
        else:
            dct[tree.tag] = text
    return dct
