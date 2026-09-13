import importlib
import sys


def load_app(monkeypatch):
    monkeypatch.setenv("AWS_REGION", "us-east-1")
    monkeypatch.setenv("AWS_SQS_URL", "https://sqs.us-east-1.amazonaws.com/123456789012/events")
    monkeypatch.setenv("AWS_DYNAMODB_TABLE", "ToggleMasterAnalytics")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test")
    monkeypatch.setenv("AWS_EC2_METADATA_DISABLED", "true")
    monkeypatch.setenv("DISABLE_WORKER", "true")

    sys.modules.pop("app", None)
    module = importlib.import_module("app")
    return module


def test_health(monkeypatch):
    module = load_app(monkeypatch)
    client = module.app.test_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_process_message_writes_event_and_deletes_message(monkeypatch):
    module = load_app(monkeypatch)
    calls = {"put_item": None, "delete_message": None}

    class DynamoDBClient:
        def put_item(self, **kwargs):
            calls["put_item"] = kwargs

    class SQSClient:
        def delete_message(self, **kwargs):
            calls["delete_message"] = kwargs

    module.dynamodb_client = DynamoDBClient()
    module.sqs_client = SQSClient()

    module.process_message({
        "MessageId": "message-1",
        "ReceiptHandle": "receipt-1",
        "Body": '{"user_id":"user-1","flag_name":"checkout","result":true,"timestamp":"2026-01-01T00:00:00Z"}',
    })

    assert calls["put_item"]["TableName"] == "ToggleMasterAnalytics"
    assert calls["put_item"]["Item"]["user_id"] == {"S": "user-1"}
    assert calls["delete_message"]["ReceiptHandle"] == "receipt-1"
