#!/usr/bin/python

# pylint: disable=wrong-import-position, missing-docstring, no-name-in-module, import-error

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

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.aci_util import aci_login, aci_logout, aci_query, aci_delete, aci_update
#from aci_util import aci_login, aci_logout, aci_query, aci_delete, aci_update


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

    is_descr_diff = False

    aci_login(aci_hostname, aci_username, aci_password)

    aci_query_response = aci_query(
        aci_hostname, "node/mo/uni/tn-" + aci_tenant_name + ".json"
    )

    if aci_query_response["totalCount"] == "1":
        if requested_state == "present":
            if aci_tenant_descr:
                if aci_tenant_descr != (aci_query_response
                                        ["imdata"][0]
                                        ["fvTenant"]["attributes"]
                                        ["descr"]):
                    is_descr_diff = True
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
            if is_descr_diff:
                tenant_payload["fvTenant"]["attributes"]["descr"] = aci_tenant_descr

            aci_update(aci_hostname, tenant_payload, "node/mo/uni.json")
        else:
            aci_delete(aci_hostname, "node/mo/uni/tn-" + aci_tenant_name + ".json")

    aci_logout(aci_hostname)

    # exit with change state indicated and return values
    module.exit_json(**result)


if __name__ == "__main__":
    main()
