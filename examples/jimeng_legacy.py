from __future__ import annotations

from collections import OrderedDict

from _example_utils import run_raw_path_examples

# Request payloads copied from ../../llm_gateway/docs/jimeng.yaml legacy /v1/jimeng/* endpoints.
EXAMPLES = [{'name': 'text2video_720p',
  'method': 'POST',
  'path': '/v1/jimeng/create',
  'json_body': {'req_key': 'jimeng_ti2v_v30_pro',
                'prompt': '千军万马在草原上奔跑的壮观场景',
                'frames': 121,
                'aspect_ratio': '16:9'}},
 {'name': 'text2video_1080p',
  'method': 'POST',
  'path': '/v1/jimeng/create',
  'json_body': {'req_key': 'jimeng_ti2v_v30_1080',
                'prompt': '千军万马在草原上奔跑的壮观场景',
                'frames': 121,
                'aspect_ratio': '16:9'}},
 {'name': 'single_frame2video_720p',
  'method': 'POST',
  'path': '/v1/jimeng/create',
  'json_body': {'req_key': 'jimeng_i2v_first_v30',
                'prompt': '千军万马',
                'image_urls': ['https://img.alicdn.com/imgextra/i1/O1CN01gDEY8M1W114Hi3XcN_!!6000000002727-0-tps-1024-406.jpg'],
                'frames': 121,
                'aspect_ratio': '16:9'}},
 {'name': 'single_frame2video_1080p',
  'method': 'POST',
  'path': '/v1/jimeng/create',
  'json_body': {'req_key': 'jimeng_i2v_first_v30_1080',
                'prompt': '千军万马',
                'image_urls': ['https://img.alicdn.com/imgextra/i1/O1CN01gDEY8M1W114Hi3XcN_!!6000000002727-0-tps-1024-406.jpg'],
                'frames': 121,
                'aspect_ratio': '16:9'}},
 {'name': 'first_last_frames2video_720p',
  'method': 'POST',
  'path': '/v1/jimeng/create',
  'json_body': {'req_key': 'jimeng_i2v_first_tail_v30',
                'prompt': '千军万马',
                'image_urls': ['https://img.alicdn.com/imgextra/i1/O1CN01gDEY8M1W114Hi3XcN_!!6000000002727-0-tps-1024-406.jpg',
                               'https://img.alicdn.com/imgextra/i2/O1CN01ktT8451iQutqReELT_!!6000000004408-0-tps-689-487.jpg'],
                'frames': 121,
                'aspect_ratio': '16:9'}},
 {'name': 'first_last_frames2video_1080p',
  'method': 'POST',
  'path': '/v1/jimeng/create',
  'json_body': {'req_key': 'jimeng_i2v_first_tail_v30_1080',
                'prompt': '千军万马',
                'image_urls': ['https://img.alicdn.com/imgextra/i1/O1CN01gDEY8M1W114Hi3XcN_!!6000000002727-0-tps-1024-406.jpg',
                               'https://img.alicdn.com/imgextra/i2/O1CN01ktT8451iQutqReELT_!!6000000004408-0-tps-689-487.jpg'],
                'frames': 121,
                'aspect_ratio': '16:9'}},
 {'name': 'query',
  'method': 'POST',
  'path': '/v1/jimeng/query',
  'json_body': {'task_id': '7491596536074305586'}}]


if __name__ == "__main__":
    run_raw_path_examples("Jimeng legacy video tasks", EXAMPLES)
