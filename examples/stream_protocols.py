"""同步/异步 SSE 消费；旧服务 JSON 回滚结果由同一迭代器产出一次。"""

import asyncio
import os
from contextlib import closing

from globalrouter import GlobalRouter


def messages() -> None:
    with GlobalRouter(max_retries=0) as client:
        events = client.messages.create(
            model=os.environ["GLOBALROUTER_MESSAGES_MODEL"],
            messages=[{"role": "user", "content": "Hello"}],
            stream=True,
        )
        with closing(events) as stream:
            for event in stream:
                print(event.model_dump(exclude_unset=True))


async def responses() -> None:
    async with GlobalRouter(max_retries=0) as client:
        events = await client.responses.create_async(
            model=os.environ["GLOBALROUTER_RESPONSES_MODEL"],
            input="Hello",
            stream=True,
        )
        try:
            async for event in events:
                print(event.model_dump(exclude_unset=True))
        finally:
            await events.aclose()


if __name__ == "__main__":
    messages()
    asyncio.run(responses())
