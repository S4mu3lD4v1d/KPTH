from kindearth.db.repo import Repository


def test_create_and_fetch_engagement(tmp_path):
    repo = Repository(db_path=tmp_path / "db.sqlite3")
    repo.ensure_schema()

    created = repo.create_engagement(name="Test", org_name="Org", notes="note")
    fetched = repo.get_engagement(created.id)

    assert fetched is not None
    assert fetched.name == "Test"
    assert fetched.org_name == "Org"

    all_rows = repo.list_engagements()
    assert any(row.id == created.id for row in all_rows)
