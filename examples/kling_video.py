import os

from globalrouter import GlobalRouter


def main() -> None:
    model = os.environ.get("GLOBALROUTER_KLING_MODEL")
    if not model:
        raise SystemExit("Set GLOBALROUTER_KLING_MODEL to the configured Kling 4.0 model ID.")

    with GlobalRouter() as client:
        task = client.videos.generate(
            model=model,
            prompt="A slow camera move across a clean product workspace.",
            sr={
                "resolution": "1080p",
            },
            input={
                "duration_seconds": 10,
                "resolution": "1080p",
                "aspect_ratio": "adaptive",
                "references": [],
            },
        )
        print(task.model_dump(exclude_none=True))

        current = client.tasks.get(task.id)
        print(current.model_dump(exclude_none=True))
        print(
            "The final video is in the task output. If SR fails, the task remains "
            "successful and returns the original video; inspect metadata.sr for details."
        )


if __name__ == "__main__":
    main()
