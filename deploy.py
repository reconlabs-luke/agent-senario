from dotenv import load_dotenv

load_dotenv()

from botocore.exceptions import ClientError
from envs import *

import boto3

client = boto3.client("bedrock-agentcore-control", region_name=AWS_REGION)

authorizer_configuration = {}
if COGNITO_DISCOVERY_URL and COGNITO_CLIENT_ID:
    authorizer_configuration.update(
        {
            "customJWTAuthorizer": {
                "discoveryUrl": COGNITO_DISCOVERY_URL,
                "allowedClients": [COGNITO_CLIENT_ID],
            }
        }
    )

try:
    response = client.create_agent_runtime(
        agentRuntimeName=AGENT_NAME,
        agentRuntimeArtifact={
            "containerConfiguration": {"containerUri": CONTAINER_URI}
        },
        networkConfiguration={"networkMode": "PUBLIC"},
        roleArn=ROLE_ARN,
        protocolConfiguration={"serverProtocol": SERVER_PROTOCOL},
        authorizerConfiguration=authorizer_configuration,
    )

except ClientError as e:
    if e.response["Error"]["Code"] == "ConflictException":
        print("Agent Runtime already exists")
        response = client.list_agent_runtimes()
        runtime_id = [
            runtime["agentRuntimeId"]
            for runtime in response["agentRuntimes"]
            if runtime["agentRuntimeName"] == AGENT_NAME
        ][0]
        response = client.update_agent_runtime(
            agentRuntimeId=runtime_id,
            agentRuntimeArtifact={
                "containerConfiguration": {"containerUri": CONTAINER_URI}
            },
            networkConfiguration={"networkMode": "PUBLIC"},
            roleArn=ROLE_ARN,
            protocolConfiguration={"serverProtocol": SERVER_PROTOCOL},
            authorizerConfiguration=authorizer_configuration,
        )
    else:
        raise e

except Exception as e:
    print(e)
    raise e

print(f"Agent Runtime created successfully!")
print(f"Agent Runtime ARN: {response['agentRuntimeArn']}")
print(f"Status: {response['status']}")
