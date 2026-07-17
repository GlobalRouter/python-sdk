from __future__ import annotations

from collections import OrderedDict

from _example_utils import run_raw_json_examples, run_sdk_examples

# Request payloads copied from ../../llm_gateway/docs/happyhorse.yaml.
EXAMPLES = OrderedDict([('text2video',
              {'model': 'happyhorse-1.0-t2v',
               'input': {'prompt': '一座由硬纸板和瓶盖搭建的微型城市，在夜晚焕发出生机。一列硬纸板火车缓缓驶过，小灯点缀其间，照亮前路。'},
               'parameters': {'resolution': '720P', 'ratio': '16:9', 'duration': 5}}),
             ('single_frame2video',
              {'model': 'happyhorse-1.0-i2v',
               'input': {'prompt': '一只猫在草地上奔跑',
                         'media': [{'type': 'first_frame',
                                    'url': 'https://cdn.translate.alibaba.com/r/wanx-demo-1.png'}]},
               'parameters': {'resolution': '720P', 'duration': 5}}),
             ('reference2video',
              {'model': 'happyhorse-1.0-r2v',
               'input': {'prompt': '[Image '
                                   '1]中身着红色旗袍的女性，镜头先以侧面中景勾勒旗袍修身剪裁与S型曲线，随即切换至低角度仰拍，捕捉她轻抬玉手展开[Image '
                                   '2]中的折扇的同时，[Image '
                                   '3]中的流苏耳坠随头部转动轻盈摆动的细节，最后推近至面部特写，定格在她指尖轻点扇骨、眼波流转间的含蓄风情，多视角全方位展现东方韵味。',
                         'media': [{'type': 'reference_image',
                                    'url': 'https://example.com/image1.jpg'},
                                   {'type': 'reference_image',
                                    'url': 'https://example.com/image2.jpg'},
                                   {'type': 'reference_image',
                                    'url': 'https://example.com/image3.jpg'}]},
               'parameters': {'resolution': '720P', 'ratio': '16:9', 'duration': 5}}),
             ('video_edit',
              {'model': 'happyhorse-1.0-video-edit',
               'input': {'prompt': '让视频中的马头人身角色穿上图片中的条纹毛衣',
                         'media': [{'type': 'video', 'url': 'https://example.com/video.mp4'},
                                   {'type': 'reference_image',
                                    'url': 'https://example.com/clothes.jpg'}]},
               'parameters': {'resolution': '720P'}})])


if __name__ == "__main__":
    run_raw_json_examples("Happyhorse video tasks", "POST", "/v1/happyhorse/create", EXAMPLES)
