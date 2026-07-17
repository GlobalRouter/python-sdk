from __future__ import annotations

from _example_utils import run_sdk_examples

# Request payload copied from https://test-global-router.xiaoniuds.com/zh-CN/docs/reference/videos/create-video.
EXAMPLES = {
    "seedance_video": {
        "model": "doubao-seedance-1-0-pro-fast-251015",
        "prompt": "A quiet city rooftop at sunset, slow cinematic push-in",
        "aspect_ratio": "16:9",
        "duration": 5,
        "resolution": "720p",
        "sr": {
            "resolution": "1080p",
        },
        "seed": 12345,
        "generate_audio": True,
        "callback_url": "https://example.com/webhooks/video",
        "frame_images": [
            {
                "type": "image_url",
                "image_url": {"url": "https://example.com/assets/opening-frame.png"},
                "frame_type": "first_frame",
            }
        ],
        "input_references": [
            {
                "type": "image_url",
                "image_url": {"url": "https://example.com/assets/reference.png"},
            }
        ],
        "provider": {
            "provider_id": "doubao",
            "options": {
                "doubao": {"some_provider_option": "value"},
            },
        },
    }
}


if __name__ == "__main__":
    run_sdk_examples(
        "Create video (/api/v1/videos)",
        EXAMPLES,
        lambda client, payload: client.videos.create(payload),
    )
