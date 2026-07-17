from __future__ import annotations

from collections import OrderedDict

from _example_utils import run_raw_json_examples, run_sdk_examples

# Request payloads copied from ../../llm_gateway/docs/images_generations.yaml.
EXAMPLES = OrderedDict([('create_image',
              {'model': 'gpt-image-1',
               'prompt': 'A cute baby sea otter',
               'n': 1,
               'size': '1024x1024'})])


if __name__ == "__main__":
    run_sdk_examples("OpenAI-compatible image generation", EXAMPLES, lambda client, payload: client.images.generate(payload))
