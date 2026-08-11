from app.feedback.feedback_store import FeedbackStore


def test_feedback_store_save_and_retrieve(tmp_path):
    file_path = tmp_path / "test_feedback.json"
    store = FeedbackStore(filepath=file_path)

    entry = store.save_feedback(
        question="What was iPhone revenue?",
        role="CTO",
        rating=-1,
        route="structured",
        answer="Incorrect answer",
        correction="iPhone revenue was $69,138 million",
    )

    assert entry["question"] == "What was iPhone revenue?"
    assert entry["rating"] == -1

    all_feedback = store.get_all_feedback()
    assert len(all_feedback) == 1

    corrections = store.get_corrections_for_question("iphone revenue")
    assert len(corrections) == 1
    assert "69,138" in corrections[0]
