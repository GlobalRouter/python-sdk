from __future__ import annotations

from collections import OrderedDict

from _example_utils import run_raw_json_examples, run_sdk_examples

# Request payloads copied from ../../llm_gateway/docs/seedream.yaml.
EXAMPLES = OrderedDict([('text2image',
              {'model': 'doubao-seedream-5-0-260128',
               'prompt': '充满活力的特写编辑肖像，模特眼神犀利，头戴雕塑感帽子，色彩拼接丰富，眼部焦点锐利，景深较浅，具有Vogue杂志封面的美学风格，采用中画幅拍摄，工作室灯光效果强烈。',
               'size': '2K',
               'output_format': 'png',
               'watermark': False}),
             ('image2image',
              {'model': 'doubao-seedream-5-0-260128',
               'prompt': '保持模特姿势和液态服装的流动形状不变。将服装材质从银色金属改为完全透明的清水（或玻璃）。透过液态水流，可以看到模特的皮肤细节。光影从反射变为折射。',
               'images': ['https://ark-project.tos-cn-beijing.volces.com/doc_image/seedream4_5_imageToimage.png'],
               'size': '2K',
               'output_format': 'png',
               'watermark': False})])


if __name__ == "__main__":
    run_raw_json_examples("Seedream image generation", "POST", "/v1/seedream/image/create", EXAMPLES)
