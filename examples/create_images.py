from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parents[1]

# Allow running this example with the system Python in this workspace. The SDK itself
# still comes from py_sdk/src; only third-party dependencies are reused from GR server venv.
for site_packages in (WORKSPACE / "global-router" / "code" / "server" / ".venv" / "lib").glob(
    "python*/site-packages"
):
    sys.path.append(str(site_packages))
sys.path.insert(0, str(ROOT / "src"))


REFERENCE_IMAGE_URL = (
    "http://i.lingweixin.com/proj-ff3609db/assets/portrait/"
    "%E8%BE%BE%E9%87%8C%E4%B9%8C%E6%96%AF/36be3ed05be7.png"
)

REQUEST_BODY: dict[str, Any] = {
    "model": "doubao-seedream-5-0-260128",
    "prompt": (
        "生成一个男性，参考图1的样貌特征，穿着狼族长老战袍（深棕色兽皮长袍，"
        "肩部饰有银色狼牙与骨饰，腰间束着宽大的金属腰带，袍角边缘缀有暗色流苏，"
        "透露着粗犷与威严），电影级光影，高质量角色肖像。生成这个角色的多角度展示图"
        "（排版紧凑，图像不可重叠）：包含左侧45度半身特写、正面胸像特写、全身三视图："
        "包括全身正面站姿（双手自然垂落）、左侧全身侧面、背面全身站姿（双手自然垂落），"
        "全身三视图身高很高，把身高调整到贴近图片的上下两边。呈现完整的三视图+细节特写，"
        "各角度比例协调、角色特征统一，角色手里不要拿东西。真人写实风格，8K超高分辨率，"
        "皮肤纹理细腻可见毛孔，衣物面料质感真实，面部平整，光影和谐，无生硬阴影，"
        "电影级画质，纯白极简背景，焦点清晰，色彩还原自然，写实度拉满。"
        "（服装上不要出现文字。）"
    ),
    "n": 1,
    "size": "2560x1440",
    "provider": {
        "provider_id": "doubao_gr",
    },
    "input_references": [
        {
            "type": "image_url",
            "image_url": {
                "url": REFERENCE_IMAGE_URL,
            },
        }
    ],
}


def main() -> None:
    from globalrouter import GlobalRouter

    client = GlobalRouter(
        api_key=os.environ["GLOBALROUTER_API_KEY"],
        base_url=os.environ.get("GLOBALROUTER_BASE_URL", "http://127.0.0.1:8000"),
        timeout_seconds=300,
        max_retries=0,
    )
    try:
        response = client.images.generate(REQUEST_BODY)
    finally:
        client.close()

    print(
        json.dumps(
            summarize_response(response.model_dump(mode="json")),
            ensure_ascii=False,
            indent=2,
        )
    )


def summarize_response(payload: dict[str, Any]) -> dict[str, Any]:
    summary = dict(payload)
    data = summary.get("data")
    if not isinstance(data, list):
        return summary

    summarized_data: list[Any] = []
    for item in data:
        if not isinstance(item, dict):
            summarized_data.append(item)
            continue
        image = dict(item)
        b64_json = image.get("b64_json")
        if isinstance(b64_json, str):
            image["b64_json_length"] = len(b64_json)
            image["b64_json"] = b64_json[:80] + "..."
        summarized_data.append(image)
    summary["data"] = summarized_data
    return summary


if __name__ == "__main__":
    main()
