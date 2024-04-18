# SPDX-FileCopyrightText: 2024 PNED G.I.E.
#
# SPDX-License-Identifier: Apache-2.0

import xml.etree.ElementTree as ET
import requests


def get_rdf_about(url):
    """
    Function that reads a XML file from url, and lists the attribute `rdf:about` of all `rdf:Description`.
    """
    response = requests.get(url)
    root = ET.fromstring(response.content)
    rdf_about = []
    for description in root.findall(
        ".//rdf:Description", {"rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"}
    ):
        rdf_about.append(
            description.attrib.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about")
        )
    return rdf_about


def get_rdf_prefLabel(url):
    """
    Function that reads a XML file from url, and retrieves all childs `skos:prefLabel` of `rdf:Description`, where the key is `xml:lang` and text of the tag as value.
    """
    response = requests.get(url)
    root = ET.fromstring(response.content)
    rdf_prefLabel = {}
    for description in root.findall(
        ".//rdf:Description", {"rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"}
    ):
        for prefLabel in description.findall(
            ".//skos:prefLabel", {"skos": "http://www.w3.org/2004/02/skos/core#"}
        ):
            rdf_prefLabel[
                prefLabel.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
            ] = prefLabel.text
    return rdf_prefLabel


def write_file(file_name, data):
    """
    Function that writes into a file a list of strings
    """
    with open(file_name, "w") as f:
        for line in data:
            f.write(line + "\n")


if __name__ == "__main__":
    url = "https://publications.europa.eu/resource/authority/country"
    rdf_about = get_rdf_about(url)
    lines = []
    for i in rdf_about:
        labels = get_rdf_prefLabel(i)
        for k, v in labels.items():
            if k == "en":
                lines.append(f'{i},"{v}",{k}')
    write_file("uri_labels.csv", lines)
