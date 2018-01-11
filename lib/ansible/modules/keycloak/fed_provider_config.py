
#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '0.1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

# TODO docs
DOCUMENTATION = '''
---
module: fed_provider_config

short_description: Configure Keycloak federation providers

version_added: "2.4"

author:
    - Josh Cain (jcain@redhat.com)
'''

EXAMPLES = '''
 TODO fill in some examples
'''

RETURN = '''
fed_providers:
    description: Keycloak client json representation
    type: dict
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.keycloak_utils import get_session
from pycloak import admin, auth, realm, client, merge
from requests.exceptions import ConnectionError
import json

def run_module():
    module_args = dict(
        username=dict(type='str', required=False),
        password=dict(type='str', required=False),
        token=dict(type='str', required=False, default=None),
        host=dict(type='str', required=False, default='http://localhost:8080'),
        auth_realm=dict(type='str', required=False, default='master'),
        auth_client_id=dict(type='str', required=False, default='admin-cli'),
        realm=dict(type='str', required=True),
        fed_provider=dict(type='list', required=True)
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

        updated_fed_providers_output = []
        for update_fed_provider in module.params['fed_provider']:
            # TODO validate that the minimum fed provider fields are present
            existing_fed_provider = realm.federation_provider(name=update_fed_provider.get('name'))

            if existing_fed_provider is None:
                updated_fed_providers_output.append(realm.add_federation_provider(update_fed_provider))
            else:
                updated_fed_provider = realm.update_federation_provider(merge.merge(update_fed_provider, existing_fed_provider))
                updated_fed_providers_output.append(updated_fed_provider)

        result['fed_providers'] = updated_fed_providers_output

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
