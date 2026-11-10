import os

from globalrouter import GlobalRouter

with GlobalRouter() as client:
    response = client.messages.create(
        {
            "model": os.environ["GLOBALROUTER_MESSAGES_MODEL"],
            "messages": [{"role": "user", "content": "Hello from GlobalRouter"}],
            "max_completion_tokens": 128,
            "vendor_extension": {"enabled": True, "values": [1, None]},
        },
        anthropic_version=os.environ.get("GLOBALROUTER_ANTHROPIC_VERSION"),
        anthropic_beta=os.environ.get("GLOBALROUTER_ANTHROPIC_BETA"),
    )
    print(response.data)
