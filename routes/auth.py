from flask import Response, request
from flask_restful import Resource
from utils import get_new_code_verifier, get_new_uuid
from utils import LOGIN_TABLE, DYNAMO_CLIENT, MAL_API_ID
from json import dumps

class Auth(Resource):
    def get(self):
        try:
            data = request.get_json()
            assert data, "didn't pass params in body"
            assert "request_id" in data.keys(), "didn't pass request ID in body"
            request_id = data['request_id']

            resp = DYNAMO_CLIENT.get_item(
                TableName=LOGIN_TABLE,
                Key={
                    'request_id': { 'S': request_id }
                }
            )

            item = resp.get('Item')
            assert item, "request does not exist"
            request_challenge = item.get('challenge').get('S')

            return Response(
                response=dumps({'request_id':request_id,'challenge': request_challenge}),
                status=200,
                mimetype='application/json'
            )

        except Exception as e:
            return Response(
                response=dumps({'error message': str(e)}),
                status=400,
                mimetype='application/json'
            )
    
    
    #TODO: implement ttl for requests, expire after 1 day
    def post(self):
        try:
            request_challenge = get_new_code_verifier()
            request_id = str(get_new_uuid())

            resp = DYNAMO_CLIENT.put_item(
                TableName=LOGIN_TABLE,
                Item={
                    'request_id': {'S': request_id },
                    'challenge': {'S': request_challenge }
                }
            )
            
            url = f'https://myanimelist.net/v1/oauth2/authorize?response_type=code&client_id={MAL_API_ID}&code_challenge={request_challenge}&state={request_id}'

            return Response(
                response=dumps({'redirect': url}),
                status=200,
                mimetype='application/json'
            )
        
        except Exception as e:
            return Response(
                response=dumps({'error message': str(e)}),
                status=400,
                mimetype='application/json'
            )