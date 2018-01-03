#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '0.1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

# TODO docs
DOCUMENTATION = '''
---
module: realm_config

short_description: gather facts about Keycloak realms

version_added: "2.4"

description:
    - "Gives the ability to collect information about keycloak realms"

options:
    id:
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
# Create or update a realm
  - name: create or update realm
    realm_config:
      host: http://localhost:8081
      username: '{{ username }}'
      password: '{{ password }}'
      realm:
        - id: 'test-realm'
          enabled: 'true'
          attributes:
            displayName: 'Test Realm'
          displayName: 'Test Realm'
          loginWithEmailAllowed: 'false'
          sslRequired: all
    register: test_realm_result
    no_log: true

'''

RETURN = '''
realms:
    description: Keycloak realm json representation
    type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from pycloak import admin, auth, realm
from requests.exceptions import ConnectionError
import json


def run_module():
    module_args = dict(
        username=dict(type='str', required=True),
        password=dict(type='str', required=True),
        host=dict(type='str', required=False, default='http://localhost:8080'),
        auth_realm=dict(type='str', required=False, default='master'),
        auth_client_id=dict(type='str', required=False, default='admin-cli'),
        realm=dict(type='list', required=False, default={})
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

        updated_realms_output = []
        for update_realm in module.params.get('realm'):
            existing_realm = admin_client.realm(update_realm['id'])
            if existing_realm is None:
                existing_realm = admin_client.add_realm(update_realm['id'])

            updated_realm = admin_client.update_realm(existing_realm.merge(realm.Realm(session, dict_rep=update_realm)))
            updated_realms_output.append(updated_realm.json)

        result['realms'] = updated_realms_output

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
