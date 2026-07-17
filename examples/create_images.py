from __future__ import annotations

from _example_utils import run_sdk_examples

# Request payload copied from https://test-global-router.xiaoniuds.com/zh-CN/docs/reference/images/create-images.
EXAMPLES = {
    "seedream_with_reference": {
        "model": "seedream-image",
        "prompt": "生成一张简洁的模型网关架构图。",
        "input_references": [
            {
                "type": "image_url",
                "image_url": {"url": "https://example.com/reference.png"},
            }
        ],
        "provider": {
            "provider_id": "doubao",
            "options": {
                "doubao": {"some_provider_option": "value"},
            },
        },
        "background": "transparent",
        "aspect_ratio": "1:1",
        "resolution": "2K",
        "output_compression": 90,
        "output_format": "png",
        "quality": "high",
        "seed": 42,
        "stream": False,
        "n": 1,
    }
}


if __name__ == "__main__":
    run_sdk_examples(
        "Create images (/api/v1/images)",
        EXAMPLES,
        lambda client, payload: client.images.generate(payload),
    )
