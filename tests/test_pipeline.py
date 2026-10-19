from src.pipeline import make_users, make_assignments, make_events, analyse

def test_data_shapes():
    users = make_users(200, 1)
    assignments = make_assignments(users, 1)
    events = make_events(users, 1000, 1)
    assert len(users) == 200
    assert len(assignments) == 1200
    assert len(events) == 1000
    assert users.user_id.is_unique

def test_analysis_output():
    users = make_users(1000, 4)
    assignments = make_assignments(users, 4)
    results = analyse(assignments, 4)
    assert len(results) == 6
    assert results.p_value.between(0, 1).all()
    assert "p_value_fdr" in results.columns
