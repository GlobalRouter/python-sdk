from __future__ import annotations

from _example_utils import run_sdk_examples

# Request payload copied from https://test-global-router.xiaoniuds.com/zh-CN/docs/reference/images/create-images-task.
EXAMPLES = {
    "jimeng_image_task": {
        "model": "jimeng_t2i_v31",
        "prompt": "生成 4 张电商商品图，白底，高级感",
        "input_references": [
            {
                "type": "image_url",
                "image_url": {"url": "https://example.com/reference.png"},
            }
        ],
        "n": 4,
        "size": "1024x1024",
        "provider": {
            "provider_id": "doubao_gr",
            "options": {
                "doubao_gr": {
                    "watermark": False,
                    "force_single": False,
                },
            },
        },
        "metadata": {
            "client_request_id": "client-001",
        },
    }
}


if __name__ == "__main__":
    run_sdk_examples(
        "Create image task (/api/v1/image-tasks)",
        EXAMPLES,
        lambda client, payload: client.images.create_task(
            payload,
            idempotency_key="client-image-task-001",
        ),
    )
