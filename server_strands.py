from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from agents.strands_agent import agent


app = FastAPI()


class InvocationRequest(BaseModel):
    prompt: str


class InvocationResponse(BaseModel):
    answer: str
    timestamp: str


@app.post("/invocations", response_model=InvocationResponse)
async def agent_invocation(request: InvocationRequest):
    try:
        user_message = request.prompt
        if not user_message:
            raise HTTPException(
                status_code=400,
                detail="No prompt found in input. Please provide a 'prompt' key in the input.",
            )

        response = agent(prompt=user_message)
        answer = response.message["content"][0]["text"]

        return InvocationResponse(
            answer=answer,
            timestamp=str(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")),
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Agent processing failed: {str(e)}"
        )


@app.get("/ping")
async def ping():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
