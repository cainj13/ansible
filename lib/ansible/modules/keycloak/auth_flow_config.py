

#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '0.1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

# TODO docs
DOCUMENTATION = '''
---
module: auth_flow_config

short_description: Configure Keycloak authentication flows

version_added: "2.4"

author:
    - Josh Cain (jcain@redhat.com)
'''

EXAMPLES = '''
 TODO fill in some examples
'''

RETURN = '''
auth_flows:
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.keycloak_utils import get_session
from pycloak import admin, auth, realm, client, merge, flow
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
        auth_flow=dict(type='list', required=True)
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

        updated_auth_flows_output = []
        for update_auth_flow in module.params['auth_flow']:
            # TODO validate that the minimum auth flow fields are present
            auth_flow = realm.auth_flow(alias=update_auth_flow['alias'])
            executions = update_auth_flow.pop('execution')

            if auth_flow is None:
                update_auth_flow['topLevel'] = 'true'
                update_auth_flow['builtIn'] = 'false'
                auth_flow = realm.create_auth_flow(update_auth_flow)

            # TODO Note in docs that the only time description and type can be changed is on add.  Otherwise have to remove
            # Therefore, we do not attempt to update any other fields here, just work with executions

            # Auth flow specification should be deterministic.  If it's not defined in Ansible spec, it should not exist.
            # TODO might be able to do this more efficiently than en masse delete + add, perhaps by index?  Could also pose a risk
            # if a box is in rotation with an in-use realm and executions are being added/messed with.  Need to add some warnings about that.
            # - could also try a diff to see if there are any changes whatsoever, skipping non-changed items
            auth_flow.delete_all_executions()
            for execution in executions:
                new_execution = auth_flow.create_execution(json.loads(json.dumps({'provider': execution['providerId']})))
                # ugh.
                new_execution = merge.merge(execution, new_execution.json)
                config = new_execution.pop('config', None)
                updated_execution = auth_flow.update_execution(new_execution)

                if config is not None:
                    updated_execution.create_config(config)
                    # updated_auth_flows_output.append(config)


            # Need to pull one more time to reflect execution changes
            updated_auth_flows_output.append(realm.auth_flow(alias=update_auth_flow['alias']).json)

        result['auth_flows'] = updated_auth_flows_output

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
