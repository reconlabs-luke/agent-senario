from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from utils import get_token, get_agent_core_runtime_url
from envs import *
from stage import Stage

import asyncio


async def remote_main():
    if STAGE.lower() == Stage.DEV.value.lower():
        mcp_url = f"http://localhost:{AGENTCORE_RUNTIME_PORT}/mcp"
        bearer_token = None
    else:
        bearer_token = get_token(
            COGNITO_USER_POOL_ID,
            COGNITO_USERNAME,
            COGNITO_PASSWORD,
            COGNITO_CLIENT_ID,
            AWS_REGION,
        )
        print(f"✅ Got Access Token: {bearer_token[:30]}...")
        mcp_url = get_agent_core_runtime_url(AWS_REGION, AGENTCORE_RUNTIME_ARN)

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
