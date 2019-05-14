#!/usr/bin/python

# pylint: disable=wrong-import-position, missing-docstring
# pylint: disable=global-statement, no-member, too-many-branches

DOCUMENTATION = '''
---
module: my_aci_tenant
author:  John McDonough (@movinalot)
short_description: Manage and ACI Tenant
description:
    - Manages an ACI Tenant.
options:
    name:
        description:
            - The name of the ACI Tenant.
    descr:
        description:
            - The description of the Tenant.
    state:
        description:
            - Whether the ACI Tenant should exist or not.
        default: present
        choices: ['present', 'absent']
'''

EXAMPLES = '''
- name: Ensure ACI Tenant is present
  my_aci_tenant:
    hostname: apic_host
    username: apic_user
    password: apic_pass
    name: TenantX
    descr: This is TenantX
    state: present

- name: Ensure ACI Tenant is present and/or update
  my_aci_tenant:
    hostname: apic_host
    username: apic_user
    password: apic_pass
    name: TenantX
    descr: TenantX is Awesome
    state: present

- name: Ensure ACI Tenant is absent
  my_aci_tenant:
    hostname: apic_host
    username: apic_user
    password: apic_pass
    name: TenantX
    state: absent
'''

RETURN = '''
original_state:
    description: The original state of the param that was passed in
    type: str
changed_state:
    description: The output state that the module generates
    type: str
'''

import json
import requests
requests.packages.urllib3.disable_warnings()

from ansible.module_utils.basic import AnsibleModule

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


def main():
    """ Process the module """

    # Manage the parameters
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(type="str", required=True),
            username=dict(type="str", default="admin"),
            password=dict(type="str", required=True, no_log=True),
            name=dict(type="str"),
            descr=dict(type="str"),
            state=dict(type="str", choices=["present", "absent"], default="present"),
        ),
        required_if=([("state", "present", ["name"])]),
        supports_check_mode=True,
    )

    # Manage the result, assume no changes.
    result = dict(
        changed=False,
        original_state='',
        changed_state=''
    )

    # Set the requested state
    requested_state = module.params["state"]

    # assign parameters to local variables
    aci_hostname = module.params["hostname"]
    aci_username = module.params["username"]
    aci_password = module.params["password"]

    aci_tenant_name = module.params["name"]

    aci_tenant_descr = None
    if module.params["descr"] is not None:
        aci_tenant_descr = module.params["descr"]

    aci_login(aci_hostname, aci_username, aci_password)

    aci_query_response = aci_query(
        aci_hostname, "node/mo/uni/tn-" + aci_tenant_name + ".json"
    )

    # Assume object does not exist
    exists = False

    # Set potential changed properties to None
    cur_aci_tenant_descr = None

    if aci_query_response["totalCount"] == "1":
        exists = True
        cur_aci_tenant_descr = (aci_query_response
                                ["imdata"][0]
                                ["fvTenant"]["attributes"]
                                ["descr"])

    if exists:
        if requested_state == "present":
            if aci_tenant_descr is not None:
                if aci_tenant_descr != cur_aci_tenant_descr:
                    result['changed'] = True
        else:
            result['changed'] = True
    else:
        if requested_state == "present":
            result['changed'] = True

    if result['changed'] and not module.check_mode:
        if requested_state == "present":
            tenant_payload = {
                "fvTenant": {
                    "attributes": {
                        "name": aci_tenant_name
                    }
                }
            }
            if aci_tenant_descr is not None:
                if aci_tenant_descr != cur_aci_tenant_descr:
                    tenant_payload["fvTenant"]["attributes"]["descr"] = aci_tenant_descr

            aci_update(aci_hostname, tenant_payload, "node/mo/uni.json")
        else:
            aci_delete(aci_hostname, "node/mo/uni/tn-" + aci_tenant_name + ".json")

    aci_logout(aci_hostname)

    # exit with change state indicated and return values
    module.exit_json(**result)


if __name__ == "__main__":
    main()
