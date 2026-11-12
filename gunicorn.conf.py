import os


def post_fork(server, worker):
    os.environ.setdefault("PYTHONPATH", "")
    from opentelemetry.instrumentation.auto_instrumentation import sitecustomize  # noqa: F401
