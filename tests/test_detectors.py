"""Unit tests for Tier A (deterministic) and Tier B (structural) detectors,
against hand-built fixtures. Per the A/B/C classification, these two tiers
are validated by unit tests alone — no gold set needed.
"""

from n8n_reliability.detectors import (
    base,
    connections_integrity,
    db_upsert,
    error_handling,
    idempotency,
    retry,
    throttling,
    validation,
    webhook_auth,
)


# ---- error_handling.py -----------------------------------------------------


def test_stop_and_error_is_not_recovery(load_fixture):
    wf = load_fixture("stop_and_error_only")
    assert error_handling.stop_and_error_present(wf) is True
    assert error_handling.has_recovery_mechanism(wf) is False, (
        "Stop and Error is a deliberate abort, not recovery — the bug this fixes "
        "folded it into 'has error handling'."
    )


def test_error_trigger_counts_as_recovery(load_fixture):
    wf = load_fixture("error_trigger_present")
    assert error_handling.error_trigger_present(wf) is True
    assert error_handling.has_recovery_mechanism(wf) is True
    assert error_handling.stop_and_error_present(wf) is False


def test_on_error_recovery_value(load_fixture):
    wf = load_fixture("on_error_recovery")
    assert error_handling.node_on_error_recovery(wf) is True
    assert error_handling.has_recovery_mechanism(wf) is True
    assert error_handling.stop_and_error_present(wf) is False


def test_legacy_continue_on_fail(load_fixture):
    wf = load_fixture("continue_on_fail_legacy")
    assert error_handling.node_continue_on_fail(wf) is True
    assert error_handling.has_recovery_mechanism(wf) is True


def test_error_workflow_setting_is_never_measurable(load_fixture):
    wf = load_fixture("error_workflow_setting_null")
    assert error_handling.error_workflow_setting(wf) == base.NOT_MEASURABLE
    assert error_handling.error_workflow_setting_key_present(wf) is True
    # even a workflow with NO settings.errorWorkflow key at all must still be
    # NOT_MEASURABLE, never silently treated as "False" (no error workflow)
    bare = {"nodes": [], "connections": {}, "settings": {}}
    assert error_handling.error_workflow_setting(bare) == base.NOT_MEASURABLE
    assert error_handling.error_workflow_setting_key_present(bare) is False


def test_clean_baseline_has_no_recovery_signals(load_fixture):
    wf = load_fixture("clean_baseline")
    assert error_handling.has_recovery_mechanism(wf) is False
    assert error_handling.stop_and_error_present(wf) is False
    assert error_handling.error_trigger_present(wf) is False


# ---- retry.py ---------------------------------------------------------------


def test_node_level_retry_is_detected(load_fixture):
    wf = load_fixture("node_retry_on_fail")
    assert retry.node_retry_on_fail(wf) is True
    detail = retry.nodes_with_retry_config(wf)
    assert len(detail) == 1
    assert detail[0]["max_tries"] == 3


def test_workflow_level_retry_boilerplate_is_not_node_retry(load_fixture):
    """The fixture's settings.retryOnFail=True is workflow-level boilerplate
    layered ON TOP of a real node-level retryOnFail=True — this test proves
    the detector reads the node field, not the settings field, by checking a
    fixture where only the settings-level flag is set."""
    wf = {
        "nodes": [{"id": "1", "name": "HTTP", "type": "n8n-nodes-base.httpRequest", "parameters": {}}],
        "connections": {},
        "settings": {"retryOnFail": True, "retryCount": 3, "retryDelay": 1000},
    }
    assert retry.node_retry_on_fail(wf) is False


# ---- webhook_auth.py ---------------------------------------------------------


def test_webhook_without_auth(load_fixture):
    wf = load_fixture("webhook_no_auth")
    assert webhook_auth.webhook_present(wf) is True
    assert webhook_auth.webhook_missing_auth(wf) is True


def test_webhook_with_auth(load_fixture):
    wf = load_fixture("webhook_with_auth")
    assert webhook_auth.webhook_missing_auth(wf) is False


def test_no_webhook_is_not_applicable(load_fixture):
    wf = load_fixture("no_webhook")
    assert webhook_auth.webhook_present(wf) is False
    assert webhook_auth.webhook_missing_auth(wf) == base.NOT_APPLICABLE, (
        "A workflow with no webhook must report NOT_APPLICABLE, never False — "
        "'no webhook' and 'webhook with auth' are different facts."
    )


# ---- throttling.py ------------------------------------------------------------


def test_throttling_nodes_detected(load_fixture):
    wf = load_fixture("wait_and_split")
    assert throttling.throttling_node_present(wf) is True
    assert throttling.has_time_delay_wait(wf) is True


def test_wait_webhook_resume_is_not_a_time_delay(load_fixture):
    wf = load_fixture("wait_webhook_resume")
    assert throttling.throttling_node_present(wf) is True
    assert throttling.has_time_delay_wait(wf) is False


def test_no_throttling(load_fixture):
    wf = load_fixture("no_throttling")
    assert throttling.throttling_node_present(wf) is False


# ---- db_upsert.py — the bug-fix regression test ------------------------------


def test_real_upsert_operation_detected(load_fixture):
    wf = load_fixture("db_upsert_operation")
    assert db_upsert.db_upsert_operation(wf) is True


def test_sticky_note_text_does_not_trigger_the_real_detector(load_fixture):
    """This is the exact bug class the earlier prototype had: 'upsert'
    appears only inside a sticky note's comment text, on a node that is
    actually configured as 'insert', not 'upsert'."""
    wf = load_fixture("upsert_bug_regression")
    assert db_upsert.db_upsert_operation(wf) is False, (
        "The fixed, anchored detector must NOT be fooled by the word 'upsert' "
        "appearing inside a sticky note."
    )
    assert db_upsert.naive_upsert_text_match(wf) is True, (
        "The naive comparator (kept only for this regression test) SHOULD still "
        "be fooled — that's the bug being regression-tested against, proving the "
        "fixed detector's exclusion of sticky notes is what makes the difference."
    )


def test_sticky_notes_only_workflow_does_not_crash_any_detector(load_fixture):
    wf = load_fixture("sticky_notes_only")
    assert error_handling.has_recovery_mechanism(wf) is False
    assert error_handling.stop_and_error_present(wf) is False
    assert retry.node_retry_on_fail(wf) is False
    assert webhook_auth.webhook_missing_auth(wf) == base.NOT_APPLICABLE
    assert throttling.throttling_node_present(wf) is False
    assert db_upsert.db_upsert_operation(wf) is False


# ---- connections_integrity.py — the "error-handler-<uuid>" corpus finding ----


def test_resolvable_connections_are_not_flagged(load_fixture):
    wf = load_fixture("on_error_recovery")  # built with real name-matched connections
    assert connections_integrity.connections_present(wf) is True
    assert connections_integrity.connections_have_unresolvable_targets(wf) is False


def test_unresolvable_connections_are_flagged(load_fixture):
    wf = load_fixture("unresolvable_connections")
    assert connections_integrity.connections_present(wf) is True
    assert connections_integrity.connections_have_unresolvable_targets(wf) is True
    assert connections_integrity.unresolvable_targets_match_error_handler_pattern(wf) is True


def test_no_connections_is_not_applicable(load_fixture):
    wf = load_fixture("error_trigger_present")  # single node, no connections key needed
    assert connections_integrity.connections_present(wf) is False
    assert connections_integrity.connections_have_unresolvable_targets(wf) == base.NOT_APPLICABLE


def test_corruption_commit_citation_fields():
    citation = connections_integrity.corruption_commit_citation()
    assert citation["commit_sha"] == "5ffee225b7c9e314cacefd7f0a46a1c10ae3d20e"
    assert citation["commit_url"].endswith(citation["commit_sha"])
    assert citation["verified_still_broken_on_pinned_commit"] is True
    assert citation["pinned_commit_is_descendant"] is True


# ---- Tier C candidates (not validated, but must not crash / must be labeled) --


def test_tier_c_detectors_are_registered_as_tier_c():
    assert base.REGISTRY["idempotency_candidate"].tier is base.Tier.C_SEMANTIC
    assert base.REGISTRY["validation_candidate"].tier is base.Tier.C_SEMANTIC


def test_validation_candidate_structural_heuristic(load_fixture):
    positive = load_fixture("validation_candidate_positive")
    negative = load_fixture("validation_candidate_negative")
    assert validation.validation_candidate(positive) is True
    assert validation.validation_candidate(negative) is False


def test_idempotency_candidate_from_upsert(load_fixture):
    wf = load_fixture("db_upsert_operation")
    assert idempotency.idempotency_candidate(wf) is True


# ---- registry sanity ----------------------------------------------------------


def test_all_registered_detectors_have_a_denominator_definition():
    for key, detector in base.REGISTRY.items():
        assert detector.denominator_definition, f"{key} missing denominator_definition"
        assert detector.version, f"{key} missing version"
