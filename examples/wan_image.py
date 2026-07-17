from __future__ import annotations

from collections import OrderedDict

from _example_utils import run_raw_json_examples, run_sdk_examples

# Request payloads copied from ../../llm_gateway/docs/wan.yaml.
EXAMPLES = OrderedDict([('text2image',
              {'model': 'wan2.7-image-pro',
               'input': {'messages': [{'role': 'user',
                                       'content': [{'text': '一间有着精致窗户的花店，漂亮的木质门，摆放着花朵'}]}]},
               'parameters': {'size': '2K', 'n': 1, 'watermark': False, 'thinking_mode': True}}),
             ('image_edit',
              {'model': 'wan2.7-image-pro',
               'input': {'messages': [{'role': 'user',
                                       'content': [{'image': 'https://example.com/car.webp'},
                                                   {'image': 'https://example.com/paint.webp'},
                                                   {'text': '把图2的涂鸦喷绘在图1的汽车上'}]}]},
               'parameters': {'size': '2K', 'n': 1, 'watermark': False}})])


if __name__ == "__main__":
    run_raw_json_examples("Wan image generation and editing", "POST", "/v1/wan/image/create", EXAMPLES)
