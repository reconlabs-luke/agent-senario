from a2a.client import A2AClient
from typing import Any
from uuid import uuid4
from a2a.types import (
    SendMessageRequest,
    MessageSendParams,
    # SendStreamingMessageRequest,
)
from utils import get_agent_core_runtime_url, get_token
from envs import *
from stage import Stage

import httpx


async def main() -> None:
    headers = {"Content-Type": "application/json"}
    if STAGE.lower() in [Stage.QA.value.lower(), Stage.PROD.value.lower()]:
        headers.update(
            {
                "Authorization": f"Bearer {get_token(COGNITO_USER_POOL_ID, COGNITO_USERNAME, COGNITO_PASSWORD, COGNITO_CLIENT_ID, AWS_REGION)}",
            }
        )
    async with httpx.AsyncClient(timeout=300, headers=headers) as httpx_client:
        client = A2AClient(
            httpx_client=httpx_client,
            url=(
                f"http://localhost:{AGENTCORE_RUNTIME_PORT}"
                if STAGE.lower() == Stage.DEV.value.lower()
                else get_agent_core_runtime_url(AWS_REGION, AGENTCORE_RUNTIME_ARN, None)
            ),
        )
        id = uuid4().hex
        send_message_payload: dict[str, Any] = {
            "message": {
                "role": "user",
                "parts": [
                    {
                        "kind": "text",
                        "text": "Hello, Im Luke. Please get my canvas name.",
                    }
                ],
                "messageId": id,
            },
        }
        request = SendMessageRequest(
            id=id, params=MessageSendParams(**send_message_payload)
        )

        response = await client.send_message(request)
        print(response.model_dump(mode="json", exclude_none=True))

        # streaming_request = SendStreamingMessageRequest(
        #     id=id,
        #     params=MessageSendParams(**send_message_payload)
        # )

        # stream_response = client.send_message_streaming(streaming_request)
        # async for chunk in stream_response:
        #     print(chunk.model_dump(mode='json', exclude_none=True))


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
