import json

import numpy as np
import openai
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv(override=True)

# Initialize OpenAI client with API key
client = OpenAI()

"""Initialize the chatbot with USD file context"""

# Start a conversation for memory management
conversation = openai.conversations.create()

print(f"Starting conversation with ID {conversation.id}")
print("Loading USD file context...")

# Read the content of minimal.usda
usda_file = "DATA/demo_scene_c.usda"
# usda_file = "minimal.usda"
usda_file = "DATA/demo_scene_c_minimal.usda"

with open(usda_file, "r") as f:
    usd_content = f.read()

system_prompt = (f"You're a spatial data analyst. "
                 f"You have read the following USD file which contains a "
                 f"scene:"
                 f"{usd_content} "
                 f"You only read this file, do not analyse the file yet."
                 f"The file is only an abstraction of a complete point cloud."
                 f"If you can't answer a question about the scene from the "
                 f"USD file, consider using tools to do more advanced "
                 f"computations."
                 f"Prefer giving high-level, human friendly answers - only "
                 f"give technical details when explicitly asked")


def calculate_point_cloud_distance(object_id_1, object_id_2):

    """Calculate distance between two objects using point cloud data."""
    print(f"\nGetting objects from the point cloud file")
    from app import objects

    if object_id_1 not in objects or object_id_2 not in objects:
        return None

    obj1_points = objects[object_id_1]['points'][['x', 'y', 'z']].values
    obj2_points = objects[object_id_2]['points'][['x', 'y', 'z']].values

    # use the distance between the two centroids
    return np.linalg.norm(
        objects[object_id_1]['centroid'] - objects[object_id_2]['centroid'])


tools = [

    {
        "type": "function",
        "name": "calculate_point_cloud_distance",
        "description": "Calculate the distance between two objects in a "
                       "point cloud using their identifiers",
        "strict": True,
        "parameters": {
            "type": "object",
            "required": [
                "object_id_1",
                "object_id_2"
            ],
            "properties": {
                "object_id_1": {
                    "type": "string",
                    "description": "Identifier of the first object in the "
                                   "point cloud, e.g., 'chair_1'."
                },
                "object_id_2": {
                    "type": "string",
                    "description": "Identifier of the second object in the "
                                   "point cloud, e.g., 'table_2'."
                }
            },
            "additionalProperties": False
        }
    }
]

# Alternative: fine-tuning via prompting
# prompt += "refuse to answer anything else than questions about the USD file"

response = client.responses.create(
    model="gpt-5",
    input=system_prompt,
    conversation=conversation.id,
)

print("✓ USD file loaded successfully!")
print(response.output_text)
print("\n" + "=" * 50)
print("Interactive USD Scene Chatbot Ready!")
print("Type 'quit' or 'exit' to end the conversation")
print("=" * 50 + "\n")

"""Main interactive chat loop"""
while True:
    try:

        # get user input and format
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\nGoodbye! Thanks for using the USD Scene Chatbot.")
            break

        if not user_input:
            continue

        print("\nAnalyzing...")

        # send to the llm and print an answer
        response = client.responses.create(
            model="gpt-5",
            input=user_input,
            conversation=conversation.id,
            tools=tools,
        )

        for item in response.output:
            if item.type == "function_call":

                print(f"\nDecided to use function {item.name} for this task")

                if item.name == "calculate_point_cloud_distance":
                    arguments = json.loads(item.arguments)
                    distance = calculate_point_cloud_distance(**arguments)

                    tool_response = {
                        "type": "function_call_output",
                        "call_id": item.call_id,
                        "output": json.dumps({
                            # make sure this is a proper float
                            "distance": distance
                        })
                    }

                    response = client.responses.create(
                        model="gpt-5",
                        conversation=conversation.id,
                        input=[tool_response]
                    )

        print(f"\nAssistant: {response.output_text}")

    except KeyboardInterrupt:
        print("\n\nGoodbye! Thanks for using the USD Scene Chatbot.")
        break
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Please try again.")
