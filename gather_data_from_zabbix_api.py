# Author: crazy_cc@hotmail.com

import requests
import json
import pandas as pd

# Zabbix API URL and user credentials
ZABBIX_API_URL = 'http://ZABBIX_URL/zabbix/api_jsonrpc.php'
ZABBIX_USER = 'Admin'
ZABBIX_PASSWORD = 'Admin'
def get_zabbix_api_token():
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({
        'jsonrpc': '2.0',
        'method': 'user.login',
        'params': {
            'user': ZABBIX_USER,
            'password': ZABBIX_PASSWORD
        },
        'id': 1
    })

    response = requests.post(ZABBIX_API_URL, headers=headers, data=data)
    try:
        response_json = response.json()
    except json.JSONDecodeError as e:
        print("Error decoding JSON response:", e)
        print("Response content:", response.text)
        return None

    if 'result' in response_json:
        return response_json['result']
    else:
        print("Failed to get API token:", response_json)
        return None

def get_hosts(auth_token):
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({
        'jsonrpc': '2.0',
        'method': 'host.get',
        'params': {
            'output': ['hostid', 'name']
        },
        'auth': auth_token,
        'id': 1
    })

    response = requests.post(ZABBIX_API_URL, headers=headers, data=data)
    try:
        response_json = response.json()
    except json.JSONDecodeError as e:
        print("Error decoding JSON response:", e)
        print("Response content:", response.text)
        return []

    return response_json.get('result', [])

def get_items(auth_token, host_id):
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({
        'jsonrpc': '2.0',
        'method': 'item.get',
        'params': {
            'output': ['itemid', 'name'],
            'hostids': host_id
        },
        'auth': auth_token,
        'id': 1
    })

    response = requests.post(ZABBIX_API_URL, headers=headers, data=data)
    try:
        response_json = response.json()
    except json.JSONDecodeError as e:
        print("Error decoding JSON response:", e)
        print("Response content:", response.text)
        return []

    return response_json.get('result', [])

def get_triggers(auth_token, item_id):
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({
        'jsonrpc': '2.0',
        'method': 'trigger.get',
        'params': {
            'output': ['triggerid', 'description'],
            'itemids': item_id
        },
        'auth': auth_token,
        'id': 1
    })

    response = requests.post(ZABBIX_API_URL, headers=headers, data=data)
    try:
        response_json = response.json()
    except json.JSONDecodeError as e:
        print("Error decoding JSON response:", e)
        print("Response content:", response.text)
        return []

    return response_json.get('result', [])

def main():
    auth_token = get_zabbix_api_token()
    if not auth_token:
        print("Failed to obtain Zabbix API token. Exiting.")
        return

    hosts = get_hosts(auth_token)
    if not hosts:
        print("Failed to retrieve hosts. Exiting.")
        return

    # Prepare a list to store all data
    data = []

    for host in hosts:
        host_id = host['hostid']
        host_name = host['name']

        items = get_items(auth_token, host_id)
        for item in items:
            item_id = item['itemid']
            item_name = item['name']

            triggers = get_triggers(auth_token, item_id)
            for trigger in triggers:
                trigger_id = trigger['triggerid']
                trigger_description = trigger['description']

                # Append the data to the list
                data.append([host_id, host_name, item_id, item_name, trigger_id, trigger_description])

    # Create a DataFrame
    df = pd.DataFrame(data, columns=['Host ID', 'Host Name', 'Item ID', 'Item Name', 'Trigger ID', 'Trigger Description'])

    # Write the DataFrame to an Excel file
    df.to_excel('zabbix_monitoring_data.xlsx', index=False)
    print("Data has been written to zabbix_monitoring_data.xlsx")

if __name__ == '__main__':
    main()
