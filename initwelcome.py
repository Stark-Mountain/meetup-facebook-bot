import os
import sys
import json
import argparse

import requests


def set_get_started_button(api_url, access_token, payload):
    get_started_button = {
            'get_started': {
                'payload': payload,
                },
            }
    response = requests.post(api_url, 
                             headers={'Content-Type': 'application/json'},
                             params={'access_token': access_token},
                             data = json.dumps(get_started_button)
                             )
    return response.text



def set_greeting(api_url, access_token, greeting_text):
    greeting = {
            'greeting': [
                {
                'locale': 'default',
                'text': greeting_text,
                }
                ]
            }
    response = requests.post(api_url, 
                             headers={'Content-Type': 'application/json'},
                             params={'access_token': access_token},
                             data = json.dumps(greeting)
                             )
    return response.text


def get_get_started_button(api_url, access_token):
    response = requests.get(api_url, 
                            headers={
                                'Content-Type': 'application/json'
                                },
                            params={
                                'access_token': access_token,
                                'fields': 'get_started',
                                }
                            )
    return response.text


def get_greeting(api_url, access_token):
    response = requests.get(api_url, 
                            headers={
                                'Content-Type': 'application/json'
                                },
                            params={
                                'access_token': access_token,
                                'fields': 'greeting',
                                }
                            )
    return response.text


def delete_get_started_button(api_url, access_token):
    payload = {
            'fields': [
                'get_started',
                ]
            }
    response = requests.delete(api_url, 
                               headers={
                                   'Content-Type': 'application/json'
                                   },
                               params={
                                   'access_token': access_token,
                                   },
                               data=json.dumps(payload)
                               )
    return response.text


def delete_greeting(api_url, access_token):
    payload = {
            'fields': [
                'greeting',
                ]
            }
    response = requests.delete(api_url, 
                               headers={
                                   'Content-Type': 'application/json'
                                   },
                               params={
                                   'access_token': access_token,
                                   },
                               data=json.dumps(payload)
                               )
    return response.text


def get_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('field', type=str,
                        help='Either "get_started or greeting".')
    parser.add_argument('-g', '--get', action='store_true',
                        help='Ask facebook the current value of the field.')
    parser.add_argument('-s', '--set', type=str,
                        help='Set new value of the field to facebook')
    parser.add_argument('-d', '--delete', action='store_true',
                        help='Ask facebook to delete the current value of the field.')
    return parser.parse_args()
                        

if __name__ == '__main__':
    args = get_cli_args()
    api_url = 'https://graph.facebook.com/v2.6/me/messenger_profile'
    access_token = os.environ['ACCESS_TOKEN']
    
    getter = None
    setter = None
    deleter = None

    if args.field == 'get_started':
        getter = get_get_started_button
        setter = set_get_started_button
        deleter = delete_get_started_button
    elif args.field == 'greeting':
        getter = get_greeting
        setter = set_greeting
        deleter = delete_greeting
    else:
        sys.exit('Unknown field parameter\n')

    if args.get:
        print('Get:')
        print(getter(api_url, access_token))
    elif args.delete:
        print('Delete:')
        print(deleter(api_url, access_token))
    elif args.set:
        print('Set:')
        print(setter(api_url, access_token, args.set))
    else:
        print('Get:')
        print(getter(api_url, access_token))
