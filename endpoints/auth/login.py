import boto3

from endpoints.helpers.returns import generate_response
from endpoints.helpers.getRequestData import get_body, check_fields
import endpoints.helpers.config as config
import authExceptions


def initiate_auth(client, username, password):
    try:
        resp = client.admin_initiate_auth(
            UserPoolId=config.USER_POOL_ID,
            ClientId=config.CLIENT_ID,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password,
            }
        )

    except Exception as e:
        return None, authExceptions.handle_auth_exception(e)

    return resp, None


def lambda_handler(event, context):
    params = get_body(event)
    client_cognito = boto3.client('cognito-idp')

    invalid_fields = check_fields(["username", "password"], [str, str], event)
    if invalid_fields is not None:
        return invalid_fields

    username = params['username']
    password = params['password']

    resp, err = initiate_auth(client_cognito, username, password)
    if err is not None:
        return err

    if resp.get("AuthenticationResult"):
        return generate_response(200, {
            "success": True,
            "message": "Success",
            "data": {
                "id_token": resp["AuthenticationResult"]["IdToken"],
                "refresh_token": resp["AuthenticationResult"]["RefreshToken"],
                "access_token": resp["AuthenticationResult"]["AccessToken"],
                "expires_in": resp["AuthenticationResult"]["ExpiresIn"],
                "token_type": resp["AuthenticationResult"]["TokenType"]
            }
        })

    else:  # this code block is relevant only when MFA is enabled
        generate_response(200, {
            "success": False,
            "message": "MFA has failed"
        })
