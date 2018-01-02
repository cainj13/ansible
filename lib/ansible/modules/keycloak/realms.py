#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '0.1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: realms

short_description: configure Keycloak realm settings

version_added: "2.4"

description:
    - "Mechanism for the creation and manipulation of Keycloak realms, settings, and clients"

options:
    name:
        description:
            - This is the message to send to the sample module
        required: true
    new:
        description:
            - Control to demo if the result of this module is changed or not
        required: false

author:
    - Josh Cain (jcain@redhat.com)
'''

EXAMPLES = '''
# Pass in a message
- name: Test with a message
  my_new_test_module:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_new_test_module:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_new_test_module:
    name: fail me
'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
message:
    description: The output message that the sample module generates
'''

from ansible.module_utils.basic import AnsibleModule
from pycloak import admin, auth
from requests.exceptions import ConnectionError

def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        name=dict(type='str', required=False, default=None)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        return result

    try:
        session = auth.AuthSession('admin', 'password')
        admin_client = admin.Admin(session)

        if not module.params['name']:
            result['realms'] = admin_client.realms
        else:
            result['realms'] = [admin_client.realm(module.params['name']).backing_json]
    except ConnectionError as e:
        module.fail_json(msg='Could not establish connection to Keycloak server')

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
