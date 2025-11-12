from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from datetime import datetime, timezone
from agents.langgraph_agent import graph
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage

import time

app = FastAPI()


class InvocationRequest(BaseModel):
    prompt: str


class InvocationResponse(BaseModel):
    answer: str
    timestamp: str


@app.post("/invocations")
async def agent_invocation(request: InvocationRequest):
    try:
        user_message = request.prompt
        if not user_message:
            raise HTTPException(
                status_code=400,
                detail="No prompt found in input. Please provide a 'prompt' key in the input.",
            )

        async def event_stream():
            ai_response = ""
            async for chunk in graph.astream({"messages": [HumanMessage(content=user_message)]}, stream_mode="values"):
                chunk["messages"][-1].pretty_print()
                if isinstance(chunk["messages"][-1], AIMessage):
                    ai_response: str = chunk["messages"][-1].content
                    for i in ai_response.split():
                        time.sleep(0.1)
                        yield f"{i} "

            # result = InvocationResponse(
            #     answer=ai_response,
            #     timestamp=str(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")),
            # ).model_dump_json()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent processing failed: {str(e)}")

    return StreamingResponse(
        content=event_stream(),
        media_type="application/json",
    )


@app.get("/ping")
async def ping():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
