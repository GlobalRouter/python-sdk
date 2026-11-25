"""示例使用 GR 模型别名；测试不调用付费上游。"""

import runpy
from pathlib import Path


def test_minimax_h3_example_accepts_gr_model_alias(monkeypatch, capsys):
    monkeypatch.setenv("GLOBALROUTER_API_KEY", "test-key")
    monkeypatch.setenv("GLOBALROUTER_MODEL", "company-video")
    example = runpy.run_path(str(Path(__file__).parents[1] / "examples/minimax_h3.py"))
    calls = []

    def call(path, body=None):
        calls.append((path, body))
        return {"task_id": "native-task", "id": "compatible-task"}

    example["main"].__globals__["call"] = call
    example["main"]()
    assert [path for path, _ in calls] == [
        "/v2/video_generation", "/v2/query/video_generation/native-task",
        "/api/v1/videos", "/api/v1/videos/compatible-task",
    ]
    assert all(body["model"] == "company-video" for _, body in calls if body)
    output = capsys.readouterr().out
    assert "GR 视频创建" in output
    assert "GR 视频查询" in output
    assert "openrouter" not in output.lower()
    assert "openrouter" not in example["__doc__"].lower()
