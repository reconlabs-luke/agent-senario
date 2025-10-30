import boto3


def get_token(
    cognito_user_pool_id: str,
    cognito_user_name: str,
    cognito_user_password: str,
    cognito_client_id: str,
    aws_region: str,
):
    cognito = boto3.client("cognito-idp", region_name=aws_region)

    try:
        cognito.admin_create_user(
            UserPoolId=cognito_user_pool_id,
            Username=cognito_user_name,
            TemporaryPassword=cognito_user_password,
            MessageAction="SUPPRESS",
        )
        print(f"✅ Created temporary user: {cognito_user_name}")

        cognito.admin_set_user_password(
            UserPoolId=cognito_user_pool_id,
            Username=cognito_user_name,
            Password=cognito_user_password,
            Permanent=True,
        )
        print("✅ Set permanent password")

    except Exception as e:
        print(f"⚠️ Failed to create user: {e}")

    bearer_token = ""
    try:
        auth_resp = cognito.initiate_auth(
            ClientId=cognito_client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": cognito_user_name,
                "PASSWORD": cognito_user_password,
            },
        )
        bearer_token = auth_resp["AuthenticationResult"]["AccessToken"]
        print(f"✅ Got Access Token: {bearer_token[:30]}...")

    except Exception as e:
        print(f"⚠️ Failed to get token: {e}")

    return bearer_token


def get_agent_core_runtime_url(
    aws_region: str, agent_arn: str, qualifier: str | None = "DEFAULT"
):
    encoded_arn = agent_arn.replace(":", "%3A").replace("/", "%2F")
    if qualifier:
        url = f"https://bedrock-agentcore.{aws_region}.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier={qualifier}"
    else:
        url = f"https://bedrock-agentcore.{aws_region}.amazonaws.com/runtimes/{encoded_arn}/invocations"

    print(f"✅ Got URL: {url}")

    return url


if __name__ == "__main__":
    from envs import *

    token = get_token(
        cognito_user_pool_id=COGNITO_USER_POOL_ID,
        cognito_user_name=COGNITO_USERNAME,
        cognito_user_password=COGNITO_PASSWORD,
        cognito_client_id=COGNITO_CLIENT_ID,
        aws_region=AWS_REGION,
    )

    print(f"Token : {token}")
