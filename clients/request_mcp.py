from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from utils import get_token
from envs import *

import asyncio
import sys


async def remote_main():
    bearer_token = get_token(
        COGNITO_USER_POOL_ID,
        COGNITO_USERNAME,
        COGNITO_PASSWORD,
        COGNITO_CLIENT_ID,
        AWS_REGION,
    )
    print(f"✅ Got Access Token: {bearer_token[:30]}...")

    if not AGENT_NAME or not bearer_token:
        raise ValueError("Error: AGENT_RUNTIME_NAME or BEARER_TOKEN environment variable is not set")


    encoded_arn = AGENT_ARN.replace(":", "%3A").replace("/", "%2F")
    if AGENT_ARN:
        mcp_url = f"https://bedrock-agentcore.{AWS_REGION}.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT"
    else:
        mcp_url = MCP_URL

    headers = {"Content-Type": "application/json"}
    if bearer_token:
        headers.update({"authorization": f"Bearer {bearer_token}"})

    print(f"Invoking: {mcp_url}, \nwith headers: {headers}\n")

    async with streamablehttp_client(
        mcp_url, headers, timeout=120, terminate_on_close=False
    ) as (
        read_stream,
        write_stream,
        _,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tool_result = await session.list_tools()
            print(tool_result)


if __name__ == "__main__":
    asyncio.run(remote_main())
