"""Risk engine tests."""

from app.services.risk_engine import assess_risk, compute_distribution, _escalate, _deescalate


def test_third_party_sharing_high_risk():
    clause = {"category": "third_party_data_sharing", "original_text": "We share your data with third parties."}
    r = assess_risk(clause)
    assert r["risk_level"] == "HIGH"


def test_third_party_sharing_sell_escalates_to_critical():
    clause = {"category": "third_party_data_sharing", "original_text": "We sell your data to brokers."}
    r = assess_risk(clause)
    assert r["risk_level"] == "CRITICAL"


def test_third_party_sharing_opt_out_deescalates():
    clause = {"category": "third_party_data_sharing", "original_text": "You may opt out of data sharing with third parties."}
    r = assess_risk(clause)
    assert r["risk_level"] == "MEDIUM"


def test_data_collection_medium():
    clause = {"category": "data_collection", "original_text": "We collect your name and email."}
    r = assess_risk(clause)
    assert r["risk_level"] == "MEDIUM"


def test_distribution_sums():
    clauses = [
        {"risk_level": "LOW"},
        {"risk_level": "LOW"},
        {"risk_level": "HIGH"},
        {"risk_level": "CRITICAL"},
    ]
    dist = compute_distribution(clauses)
    assert dist["LOW"] == 2
    assert dist["HIGH"] == 1
    assert dist["CRITICAL"] == 1
    assert dist["MEDIUM"] == 0


def test_unknown_category_defaults_low():
    clause = {"category": "unknown_category", "original_text": "Some random text."}
    r = assess_risk(clause)
    assert r["risk_level"] == "LOW"


def test_escalate_deescalate():
    assert _escalate("LOW") == "MEDIUM"
    assert _escalate("CRITICAL") == "CRITICAL"
    assert _deescalate("CRITICAL") == "HIGH"
    assert _deescalate("LOW") == "LOW"
