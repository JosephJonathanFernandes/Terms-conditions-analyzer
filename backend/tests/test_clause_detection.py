"""Clause detection tests - all 21 categories."""

from app.services.clause_detection import detect_clauses, CLAUSE_PATTERNS


def _categories(text: str) -> set[str]:
    return {c["category"] for c in detect_clauses(text)}


def test_all_21_categories_registered():
    expected = {
        "data_collection", "personal_information_usage", "third_party_data_sharing",
        "cookies_and_tracking", "data_retention", "account_deletion", "user_rights",
        "payment_terms", "automatic_subscription_renewal", "cancellation_and_refunds",
        "intellectual_property_rights", "content_ownership", "license_granted_to_platform",
        "account_suspension", "termination_without_notice", "liability_limitations",
        "indemnification", "arbitration", "jurisdiction", "dispute_resolution",
        "unilateral_modification_of_terms",
    }
    assert dict(CLAUSE_PATTERNS).keys() == expected


def test_detects_data_collection():
    assert "data_collection" in _categories("We collect your personal data including name and email.")


def test_detects_personal_information_usage():
    assert "personal_information_usage" in _categories("We use your information for marketing purposes.")


def test_detects_third_party_data_sharing():
    assert "third_party_data_sharing" in _categories("We share your data with third parties.")


def test_detects_cookies_and_tracking():
    assert "cookies_and_tracking" in _categories("We use cookies and tracking pixels.")


def test_detects_data_retention():
    assert "data_retention" in _categories("We retain your data for 2 years.")


def test_detects_account_deletion():
    assert "account_deletion" in _categories("You may delete your account at any time.")


def test_detects_user_rights():
    assert "user_rights" in _categories("You have the right to access your data.")


def test_detects_payment_terms():
    assert "payment_terms" in _categories("Your subscription fee is $9.99 per month.")


def test_detects_automatic_subscription_renewal():
    assert "automatic_subscription_renewal" in _categories("Your subscription will renew automatically unless you cancel.")


def test_detects_cancellation_and_refunds():
    assert "cancellation_and_refunds" in _categories("You may cancel and request a refund within 30 days.")


def test_detects_intellectual_property_rights():
    assert "intellectual_property_rights" in _categories("All intellectual property rights are reserved.")


def test_detects_content_ownership():
    assert "content_ownership" in _categories("You retain ownership of content you upload.")


def test_detects_license_granted_to_platform():
    assert "license_granted_to_platform" in _categories("You grant us a worldwide, royalty-free license to use your content.")


def test_detects_account_suspension():
    assert "account_suspension" in _categories("We may suspend your account for violations.")


def test_detects_termination_without_notice():
    assert "termination_without_notice" in _categories("We may terminate your account without notice.")


def test_detects_liability_limitations():
    assert "liability_limitations" in _categories("Our liability is limited to the amount you paid.")


def test_detects_indemnification():
    assert "indemnification" in _categories("You agree to indemnify us for all claims.")


def test_detects_arbitration():
    assert "arbitration" in _categories("Disputes will be resolved by binding arbitration.")


def test_detects_jurisdiction():
    assert "jurisdiction" in _categories("This agreement is governed by the laws of California.")


def test_detects_dispute_resolution():
    assert "dispute_resolution" in _categories("Dispute resolution shall be handled through mediation.")


def test_detects_unilateral_modification():
    assert "unilateral_modification_of_terms" in _categories("We may change these terms at any time without notice.")


def test_empty_text():
    assert detect_clauses("") == []
    assert detect_clauses("   ") == []


def test_confidence_bounds():
    clauses = detect_clauses("We collect your personal data including name and email.")
    for c in clauses:
        assert 0.0 <= c["confidence"] <= 1.0
