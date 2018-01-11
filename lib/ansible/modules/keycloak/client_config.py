#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '0.1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

# TODO docs
DOCUMENTATION = '''
---
module: client_config

short_description: Configure Keycloak clients

version_added: "2.4"

description:
    - "Gives the ability to manipulate Keycloak clients"

options:
    client_id:
        description:
            - Name of the realm for which the search is being performed
        required: true

    *:
        description:
            - All other vars follow key/value pairs in sync with Keycloak JSON
        requred: false

author:
    - Josh Cain (jcain@redhat.com)
'''

EXAMPLES = '''
 TODO fill in some examples
'''

RETURN = '''
clients:
    description: Keycloak client json representation
    type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.keycloak_utils import get_session
from pycloak import admin, auth, realm, client
from requests.exceptions import ConnectionError
import json
import os

def run_module():
    module_args = dict(
        username=dict(type='str', required=False),
        password=dict(type='str', required=False),
        token=dict(type='str', required=False, default=None),
        host=dict(type='str', required=False, default='http://localhost:8080'),
        auth_realm=dict(type='str', required=False, default='master'),
        auth_client_id=dict(type='str', required=False, default='admin-cli'),
        realm=dict(type='str', required=True),
        client=dict(type='list', required=False, default={})
    )
    result = dict(
        changed=False
    )
    module = AnsibleModule(
        argument_spec=module_args
    )

    try:
        session = get_session(module.params)
        admin_client = admin.Admin(session)
        realm = admin_client.realm(module.params['realm'])

        if realm is None:
            module.fail_json(msg='Could not find specified realm, please check the realm name and try again')

        updated_clients_output = []
        for update_client in module.params.get('client'):
            # TODO validate that the minimum client fields are present
            existing_client = realm.client_id(update_client['clientId'])

            if existing_client is None:
                updated_clients_output.append(realm.create_client(update_client['clientId'], update_client['protocol']).json)
            else:
                updated_client = realm.update_client(existing_client.merge(client.Client(session, dict_rep=update_client)).json)
                updated_clients_output.append(updated_client.json)

        result['clients'] = updated_clients_output

    except ConnectionError as e:
        module.fail_json(
            msg='Could not establish connection to Keycloak server.  Verify that the server is up and running, and reachable by the ansible host.')
    except auth.AuthException as e:
        module.fail_json(
            msg='Error attempting to authenticate to Keycloak server.  Validate that your username and password are correct and that the selected client is enabled for direct access grants.')

    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
