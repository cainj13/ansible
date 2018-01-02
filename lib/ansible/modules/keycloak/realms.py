#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '0.1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: realms

short_description: gather facts about Keycloak realms

version_added: "2.4"

description:
    - "Gives the ability to collect information about keycloak realms"

options:
    name:
        description:
            - Name of the realm for which the search is being performed
        required: false

author:
    - Josh Cain (jcain@redhat.com)
'''

EXAMPLES = '''
# Get all realms
  - name: get all realms
    realms:
      username: admin
      password: '{{ password }}'
    no_log: True
    register: realms_results

# Get a realm by name
  - name: get a single realm
    realms:
      username: admin
      password: '{{ password }}'
    no_log: True
    register: single_realm_results
'''

RETURN = '''
realms:
    description: Keycloak realm json representation
    type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from pycloak import admin, auth
from requests.exceptions import ConnectionError


def run_module():
    module_args = dict(
        username=dict(type='str', required=True),
        password=dict(type='str', required=True),
        host=dict(type='str', required=False, default='http://localhost:8080'),
        auth_realm=dict(type='str', required=False, default='master'),
        auth_client_id=dict(type='str', required=False, default='admin-cli'),
        realm_search_name=dict(type='str', required=False, default=None)
    )
    result = dict(
        changed=False
    )
    module = AnsibleModule(
        argument_spec=module_args
    )

    try:
        session = auth.AuthSession(module.params['username'], module.params['password'], host=module.params.get(
            'host'), realm=module.params['auth_realm'], client_id=module.params['auth_client_id'])
        admin_client = admin.Admin(session)

        if not module.params['realm_search_name']:
            result['realms'] = admin_client.realms
        else:
            result['realms'] = [admin_client.realm(module.params['realm_search_name']).backing_json]
    except ConnectionError as e:
        module.fail_json(msg='Could not establish connection to Keycloak server.  Verify that the server is up and running, and reachable by the ansible host.')
    except auth.AuthException as e:
        module.fail_json(msg='Error attempting to authenticate to Keycloak server.  Validate that your username and password are correct and that the selected client is enabled for direct access grants.')

    module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()
