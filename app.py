import os 
import asyncio
import requests
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai.types.responses import ResponseTextDeltaEvent
from agents import Agent, Runner, trace, function_tool, SQLiteSession, set_tracing_disabled, OpenAIChatCompletionsModel


load_dotenv(override=True)



set_tracing_disabled(True)

api_key = os.getenv("OPENROUTER_API_KEY")
url = os.getenv("OPENROUTER_URL")

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

client = AsyncOpenAI(base_url=url,api_key=api_key)

model = OpenAIChatCompletionsModel(model="gpt-5.4-nano", openai_client=client)

agent = Agent(name="Jokestar",instructions="You are snarky witty assistant who tell a joke", model=model)


async def main():
    result = await Runner.run(agent, "tell a joke on autonomous AI")
    print(result.final_output)
    

async def stream():
    result = Runner.run_streamed(agent, input="Tell 5 jokes on ai agents")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
        
def push(message):
    payload = {
        "user":pushover_user,
        "token":pushover_token,
        "message": message
    }
    
    requests.post(pushover_url, data=payload)
    
push("hey")

    
@function_tool    
def push_tool(message: str) -> str:
    """Send the given message to the user as a push notification"""
    payload = {"user":pushover_user, "token":pushover_token,"message":message}
    result = requests.post(pushover_url, data=payload).status_code
    print(result)
    return f"Push sent with api status code {result}"
    
notify_model = OpenAIChatCompletionsModel(model="gpt-5.4-mini", openai_client=client)
notifier = Agent(name="Notifier", instructions="You notify user on requests", model=notify_model, tools=[push_tool])



async def notifier_agent():
    result = await Runner.run(notifier, "Let me know when tool called")
    print(result.final_output)
    


asyncio.run(notifier_agent())