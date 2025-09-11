from langgraph_sdk import get_client
import asyncio

client = get_client(url="http://localhost:2024")

async def chat_loop():
    print("Chat started. Type 'quit' to exit.")
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
            
        if not user_input:
            continue
            
        print("Assistant: ", end="", flush=True)
        
        async for chunk in client.runs.stream(
            None,  # Threadless run
            "agent", # Name of assistant. Defined in langgraph.json.
            input={
                "messages": [{
                    "role": "human",
                    "content": user_input,
                }],
            },
        ):
            if chunk.data and (messages := chunk.data.get('messages')):
                print(messages[-1]['content'], end="", flush=True)

if __name__ == "__main__":
    asyncio.run(chat_loop())