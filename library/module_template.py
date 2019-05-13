#!/usr/bin/python

# pylint: disable=wrong-import-position, missing-docstring, global-statement

DOCUMENTATION = '''
---
module: module_name
author:  author_name
short_description: short_description
description:
    - long_description
options:
    option_1:
        description:
            - This is option 1
        required: true
    option_2:
        description:
            - This is option 2
        required: false
    state:
        description:
            - Whether the thing should exist or not.
        default: present
        choices: ['present', 'absent']
'''

EXAMPLES = '''
- name: Ensure thing is present
  module_name:
    option_1: foo
    state: present

- name: Ensure thing is present and/or update
  module_name:
    option_1: foo
    option_2: bar
    state: present

- name: Ensure thing is absent
  module_name:
    option_1: foo
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

def update_thing(thing):
    """ update the thing """
    thing = "updated"
    return thing


def delete_thing(thing):
    """ delete the thing """
    thing = "deleted"
    return thing


from ansible.module_utils.basic import AnsibleModule


def main():
    """ Process the module """

    # Manage the parameters
    module = AnsibleModule(
        argument_spec=dict(
            option_1=dict(type="str", required=True),
            option_2=dict(type="str"),
            state=dict(type="str", choices=["present", "absent"], default="present"),
        ),
        required_if=([("state", "present", ["option_1"])]),
        supports_check_mode=True,
    )

    # Manage the result, assume no changes
    result = dict(
        changed=False,
        original_state='',
        changed_state=''
    )

    # Set the requested state
    requested_state = module.params["state"]

    # assign parameters to local variables
    option_1 = module.params["option_1"]
    option_2 = None
    if module.params["option_2"] is not None:
        option_2 = module.params["option_2"]

    # Change for testing
    exists = True
    thing_option_2 = "test"

    # if the object exists and the 'requested_state' is 'present'
    # check for changes, if there is a change set 'changed' to true

    # if the object exists and the 'requested_state' is not 'present'
    # set 'changed' to true

    # if the object does not exist and the 'requested_state' is 'present'
    # set 'changed' to true
    if exists:
        if requested_state == "present":
            if option_2:
                if option_2 != thing_option_2:
                    result['changed'] = True
        else:
            result['changed'] = True
    else:
        if requested_state == "present":
            result['changed'] = True

    # if 'changed' is True and the 'requested_state' is 'present'
    # create or update the object, if not 'module.check_mode'

    # if 'changed' is True and the 'requested_state' is 'absent'
    # delete the object, if not 'module.check_mode'
    if result['changed'] and not module.check_mode:
        if requested_state == "present":
            thing_option_2 = option_2
            update_thing(option_1)
        else:
            delete_thing(option_1)

    # exit with change state indicated
    module.exit_json(**result)


if __name__ == "__main__":
    main()
