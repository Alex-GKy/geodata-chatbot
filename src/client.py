import asyncio

from langgraph_sdk import get_client

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
                "agent",  # Name of assistant. Defined in langgraph.json.
                input={
                    "messages": [{
                        "role": "human",
                        "content": user_input,
                    }],
                },
                stream_mode="messages-tuple"
        ):
            # print(f"Event: {chunk.event}")
            if chunk.event != "messages":
                continue

            message_chunk, metadata = chunk.data
            if (message_chunk["content"] and
                    message_chunk["type"] == "AIMessageChunk"):
                print(message_chunk["content"], end="", flush=True)


if __name__ == "__main__":
    asyncio.run(chat_loop())
