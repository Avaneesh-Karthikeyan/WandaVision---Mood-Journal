import pytest
from unittest.mock import AsyncMock, patch


# ──────────────────────────────────────────────
# GET /health
# ──────────────────────────────────────────────

class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_body(self, client):
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"
        assert "message" in data
        assert isinstance(data["message"], str)


# ──────────────────────────────────────────────
# POST /journal
# ──────────────────────────────────────────────

class TestCreateJournalEntry:
    def test_create_entry_returns_201(self, client, mock_sentiment):
        payload = {"text": "Today was an amazing day. I felt very accomplished!"}
        response = client.post("/journal", json=payload)
        assert response.status_code == 201

    def test_create_entry_response_schema(self, client, mock_sentiment):
        payload = {"text": "Today was an amazing day. I felt very accomplished!"}
        response = client.post("/journal", json=payload)
        data = response.json()

        assert "id" in data
        assert "text" in data
        assert "mood" in data
        assert "reflection" in data
        assert "created_at" in data

    def test_create_entry_returns_correct_mood(self, client, mock_sentiment):
        payload = {"text": "I had such a great time at the park today!"}
        response = client.post("/journal", json=payload)
        data = response.json()
        assert data["mood"] == "happy"

    def test_create_entry_stores_original_text(self, client, mock_sentiment):
        text = "Journaling is a great way to reflect on your day."
        response = client.post("/journal", json={"text": text})
        assert response.json()["text"] == text

    def test_create_entry_reflection_is_string(self, client, mock_sentiment):
        payload = {"text": "Feeling okay today, nothing special."}
        response = client.post("/journal", json=payload)
        assert isinstance(response.json()["reflection"], str)
        assert len(response.json()["reflection"]) > 0

    def test_create_entry_sad_mood(self, client, mock_sentiment_sad):
        payload = {"text": "I feel really down and hopeless right now."}
        response = client.post("/journal", json=payload)
        assert response.status_code == 201
        assert response.json()["mood"] == "sad"

    def test_create_entry_empty_text_fails(self, client):
        response = client.post("/journal", json={"text": ""})
        assert response.status_code == 422

    def test_create_entry_missing_text_field_fails(self, client):
        response = client.post("/journal", json={})
        assert response.status_code == 422

    def test_create_entry_text_too_long_fails(self, client):
        long_text = "a" * 5001
        response = client.post("/journal", json={"text": long_text})
        assert response.status_code == 422

    def test_create_entry_calls_sentiment_analysis(self, client, mock_sentiment):
        payload = {"text": "Had a productive morning."}
        client.post("/journal", json=payload)
        mock_sentiment.assert_called_once_with(payload["text"])

    def test_create_multiple_entries_get_unique_ids(self, client, mock_sentiment):
        payload = {"text": "Entry number one."}
        r1 = client.post("/journal", json=payload)
        r2 = client.post("/journal", json=payload)
        assert r1.json()["id"] != r2.json()["id"]

    def test_create_entry_sentiment_failure_raises_500(self, client):
        with patch(
            "app.main.sentiment.analyze_sentiment",
            new_callable=AsyncMock,
            side_effect=RuntimeError("OpenAI unavailable"),
        ):
            response = client.post("/journal", json={"text": "Test entry."})
            assert response.status_code == 500


# ──────────────────────────────────────────────
# GET /journal
# ──────────────────────────────────────────────

class TestGetJournalEntries:
    def test_get_entries_returns_200(self, client):
        response = client.get("/journal")
        assert response.status_code == 200

    def test_get_entries_empty_db_returns_list(self, client):
        response = client.get("/journal")
        assert response.json() == []

    def test_get_entries_returns_created_entry(self, client, mock_sentiment):
        client.post("/journal", json={"text": "First entry."})
        response = client.get("/journal")
        entries = response.json()
        assert len(entries) == 1
        assert entries[0]["text"] == "First entry."

    def test_get_entries_returns_all_entries(self, client, mock_sentiment):
        for i in range(3):
            client.post("/journal", json={"text": f"Entry number {i}."})
        response = client.get("/journal")
        assert len(response.json()) == 3

    def test_get_entries_newest_first(self, client, mock_sentiment):
        r1 = client.post("/journal", json={"text": "First entry."})
        r2 = client.post("/journal", json={"text": "Second entry."})
        id1, id2 = r1.json()["id"], r2.json()["id"]
        entries = client.get("/journal").json()
        # IDs should appear in descending order (newest first)
        returned_ids = [e["id"] for e in entries]
        assert returned_ids.index(id2) < returned_ids.index(id1)

    def test_get_entries_each_has_required_fields(self, client, mock_sentiment):
        client.post("/journal", json={"text": "Checking fields."})
        entry = client.get("/journal").json()[0]
        for field in ("id", "text", "mood", "reflection", "created_at"):
            assert field in entry

    def test_get_entries_limit_pagination(self, client, mock_sentiment):
        for i in range(5):
            client.post("/journal", json={"text": f"Entry {i}."})
        response = client.get("/journal?limit=2")
        assert len(response.json()) == 2

    def test_get_entries_skip_pagination(self, client, mock_sentiment):
        for i in range(5):
            client.post("/journal", json={"text": f"Entry {i}."})
        all_entries = client.get("/journal").json()
        skipped = client.get("/journal?skip=2").json()
        assert len(skipped) == 3
        assert skipped[0]["id"] == all_entries[2]["id"]
