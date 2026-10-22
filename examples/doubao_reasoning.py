"""保留 Doubao 的加密推理状态；需先启用模型并设置 GLOBALROUTER_API_KEY。"""
from globalrouter import GlobalRouter


def main() -> None:
    messages = [{"role": "user", "content": "What is 17 times 19?"}]
    model = "doubao-seed-2-1-pro-260915"
    with GlobalRouter() as client:
        first = client.chat.send(model=model, messages=messages, max_completion_tokens=1024)
        # 包括 encrypted_content、tool_calls，原样回传，不解码或修改。
        messages.append(first.choices[0]["message"])
        messages.append({"role": "user", "content": "Add 7 to that result."})
        second = client.chat.send(model=model, messages=messages, max_completion_tokens=1024)
        print(second.choices[0]["message"].get("content", ""))


if __name__ == "__main__":
    main()
