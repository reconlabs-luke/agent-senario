from dotenv import load_dotenv

load_dotenv()

import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

AWS_REGION = os.getenv("AWS_REGION")
AGENT_NAME = os.getenv("AGENT_CORE_NAME")
CONTAINER_URI = os.getenv("AGENT_CORE_CONTAINER_URI")
ROLE_ARN = os.getenv("AGENT_CORE_ROLE_ARN")
SERVER_PROTOCOL = os.getenv("AGENT_CORE_SERVER_PROTOCOL")
AGENT_ARN = os.getenv("AGENT_CORE_ARN")

COGNITO_DISCOVERY_URL = os.getenv("COGNITO_DISCOVERY_URL")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_USERNAME = os.getenv("COGNITO_USERNAME")
COGNITO_PASSWORD = os.getenv("COGNITO_PASSWORD")

MCP_URL = os.getenv("MCP_URL")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

required_envs = []

for env in required_envs:
    if None in env.values():
        raise ValueError(f"Missing environment variable: {env.keys()}")
