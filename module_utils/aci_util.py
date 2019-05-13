#
#
# Author: John McDonough (jomcdono@cisco.com)
#         Cisco Systems, Inc.
#

# pylint: disable=missing-docstring, no-member, global-statement

import json
import requests
requests.packages.urllib3.disable_warnings()

HTTP_HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

APIC_TOKEN = ""

def http_actions(http_method, http_url, http_data, http_resource):
    """ interact with aci REST api """

    if http_method == "GET":
        response = requests.request(
            http_method,
            http_url + "/api/" + http_resource,
            headers=HTTP_HEADERS,
            verify=False,
        )
        #print(response.text)

    if http_method == "POST":
        response = requests.request(
            http_method,
            http_url + "/api/" + http_resource,
            data=json.dumps(http_data),
            headers=HTTP_HEADERS,
            verify=False,
        )
        #print(response.text)

    if http_method == "DELETE":
        response = requests.request(
            http_method,
            http_url + "/api/" + http_resource,
            headers=HTTP_HEADERS,
            verify=False,
        )
        #print(response.text)

    return response.text


def aci_login(aci_hostname, aci_username, aci_password):
    """ login to aci retrieve cookie/token """

    global APIC_TOKEN, HTTP_HEADERS

    payload = {"aaaUser": {"attributes": {"name": "", "pwd": ""}}}

    payload["aaaUser"]["attributes"]["name"] = aci_username
    payload["aaaUser"]["attributes"]["pwd"] = aci_password

    url = "https://" + aci_hostname
    json_response = json.loads(http_actions("POST", url, payload, "aaaLogin.json"))

    APIC_TOKEN = json_response["imdata"][0]["aaaLogin"]["attributes"]["token"]

    HTTP_HEADERS["cookie"] = "APIC-Cookie=" + APIC_TOKEN


def aci_logout(aci_hostname):
    """ logout of aci """
    payload = {"aaaLogout": {"attributes": {"token": ""}}}

    payload["aaaLogout"]["attributes"]["token"] = APIC_TOKEN

    url = "https://" + aci_hostname
    json.loads(http_actions("POST", url, payload, "aaaLogout.json"))


def aci_query(aci_hostname, aci_resource):
    """ query aci object """
    payload = None
    url = "https://" + aci_hostname
    json_response = json.loads(http_actions("GET", url, payload, aci_resource))
    return json_response


def aci_update(aci_hostname, aci_payload, aci_resource):
    """ update aci object """
    url = "https://" + aci_hostname
    json_response = json.loads(http_actions("POST", url, aci_payload, aci_resource))
    return json_response


def aci_delete(aci_hostname, aci_resource):
    """ delete aci object """
    payload = None
    url = "https://" + aci_hostname
    json_response = json.loads(http_actions("DELETE", url, payload, aci_resource))
    return json_response
