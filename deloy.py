from pydoc import describe
from dotenv import load_dotenv

load_dotenv()

from botocore.exceptions import ClientError

import boto3
import os
import argparse

args = argparse.ArgumentParser()
args.add_argument("--agent_name", type=str, default=os.getenv("AGENT_NAME"))
args.add_argument("--region_name", type=str, default=os.getenv("REGION"))
args.add_argument("--container_uri", type=str, default=os.getenv("CONTAINER_URI"))
args.add_argument("--role_arn", type=str, default=os.getenv("ROLE_ARN"))
args.add_argument("--server_protocol", type=str, default="MCP", choices=["MCP", "HTTP", "A2A"])
args.add_argument("--discovery_url", type=str, default=os.getenv("COGNITO_DISCOVERY_URL"))
args.add_argument("--client_id", type=str, default=os.getenv("COGNITO_CLIENT_ID"))

client = boto3.client("bedrock-agentcore-control", region_name=args.region_name)

agent_runtime_name = args.agent_name
container_uri = args.container_uri
role_arn = args.role_arn
server_protocol = args.server_protocol

# Auth of Cognito
discovery_url = args.discovery_url
client_id = args.client_id

try:
    response = client.create_agent_runtime(
        agentRuntimeName=agent_runtime_name,
        agentRuntimeArtifact={
            "containerConfiguration": {"containerUri": container_uri}
        },
        networkConfiguration={"networkMode": "PUBLIC"},
        roleArn=role_arn,
        protocolConfiguration={"serverProtocol": server_protocol},
        authorizerConfiguration={
            "customJWTAuthorizer": {
                "discoveryUrl": discovery_url,
                "allowedClients": [client_id],
            }
        },
    )

except ClientError as e:
    if e.response["Error"]["Code"] == "ConflictException":
        print("Agent Runtime already exists")
        response = client.list_agent_runtimes()
        runtime_id = [
            runtime["agentRuntimeId"]
            for runtime in response["agentRuntimes"]
            if runtime["agentRuntimeName"] == agent_runtime_name
        ][0]
        response = client.update_agent_runtime(
            agentRuntimeId=runtime_id,
            agentRuntimeArtifact={
                "containerConfiguration": {"containerUri": container_uri}
            },
            networkConfiguration={"networkMode": "PUBLIC"},
            roleArn=role_arn,
            protocolConfiguration={"serverProtocol": server_protocol},
            authorizerConfiguration={
                "customJWTAuthorizer": {
                    "discoveryUrl": discovery_url,
                    "allowedClients": [client_id],
                }
            },
        )
    else:
        raise e

except Exception as e:
    print(e)
    raise e

print(f"Agent Runtime created successfully!")
print(f"Agent Runtime ARN: {response['agentRuntimeArn']}")
print(f"Status: {response['status']}")
