import os
from dotenv import load_dotenv
from google import genai
import argparse
from google.genai import types
from prompts import system_prompt
from call_function import available_functions

def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    if api_key == None:
        raise RuntimeError('Api key not found')

    client = genai.Client(api_key=api_key)

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
        # Now we can access `args.user_prompt`

    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

    config = types.GenerateContentConfig(
        tools=[available_functions],
        system_instruction=system_prompt,
        temperature=0,
    )
    response = client.models.generate_content(
        model='gemini-2.5-flash', 
        contents=messages, 
        config=config,
        )

    if args.verbose == True:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")

    if response.usage_metadata != None:
        print(f"Total tokens: {response.usage_metadata.total_token_count}")
    else:
        raise RuntimeError('Metadata is None')
    
    candidate = response.candidates[0]

    if candidate.content.parts:
        for part in candidate.content.parts:
            if part.function_call:
                func_name = part.function_call.name
                args = part.function_call.args
                print(f"Calling function: {func_name}({args})")
    else:
        print(response.text)

if __name__ == "__main__":
    main()
