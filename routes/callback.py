from flask import Response, request
from flask_restful import Resource

from utils import get_new_uuid
from utils import DYNAMO_CLIENT, MAL_API_ID, MAL_API_SECRET, LOGIN_TABLE, USER_TABLE

import requests
from json import dumps
from datetime import datetime, timedelta

class Callback(Resource):
    def post(self):
        try:
            data = request.get_json()
            assert data, "didnt pass in params into body"
            assert "auth_code" in data.keys(), "didn't pass user auth code in body"
            assert "request_id" in data.keys(), "didn't pass request id in body"

            auth_code = data['auth_code']
            request_id = data['request_id']

            # get challenge from request table
            resp = DYNAMO_CLIENT.delete_item(
                TableName=LOGIN_TABLE,
                Key={
                    'request_id': { 'S': request_id }
                },
                ReturnValues='ALL_OLD'
            )
            atr = resp.get('Attributes')
            assert atr, "request does not exist"
            request_challenge = atr.get('challenge').get('S')

            #request user access token from MAL
            data = {
                'client_id': MAL_API_ID,
                'client_secret': MAL_API_SECRET,
                'code': auth_code,
                'code_verifier': request_challenge,
                'grant_type': 'authorization_code'
            }
            response = requests.post("https://myanimelist.net/v1/oauth2/token", data=data)
            
            response.raise_for_status()
            token = response.json()

            access_token = str(token['access_token'])
            refresh_token = str(token["refresh_token"])
            access_token_expiration = str(
                datetime.now() + timedelta(seconds=int(token["expires_in"]))
            )
            

            #store user access token in USER_TABLE
            user_id = str(get_new_uuid())

            resp = DYNAMO_CLIENT.put_item(
                TableName=USER_TABLE,
                Item={
                    'user_id':{'S':user_id},
                    'auth_code':{'S':auth_code},
                    'access_token':{'S':access_token},
                    'refresh_token':{'S':refresh_token},
                    'access_token_expiration':{'S':access_token_expiration}
                }
            )

            return Response(
                response=dumps({'user_id': user_id}),
                status=201,
                mimetype='application/json'
            )
            
        except Exception as e:
            return Response(
                response=dumps({'error message': str(e)}),
                status=400,
                mimetype='application/json'
            )