
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("ERROR: GROQ_API_KEY .env file mein nahi mili.")
else:
    try:
        client = Groq(api_key=api_key)
        models = client.models.list()

        print("\nAvailable Groq models:\n")
        for model in models.data:
            print(model.id)

    except Exception as exc:
        print(f"Could not fetch models: {exc}")
