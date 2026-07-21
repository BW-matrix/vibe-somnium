from __future__ import annotations

import os
import sys
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts.export_public_trace import (
    _assert_sanitized,
    _content_hash,
    _private_run_replacements,
    _sanitize_and_reseal_scene_packet,
    _scene_packet_payload,
    render_public_trace,
)


def _projection_evidence(context: dict) -> tuple[dict, dict]:
    recipient = {"role": "authority", "instance_id": "authority_judge"}
    projection_type = context["context_type"]
    policy_id = f"{projection_type}.v0.1"
    context_sha256 = _content_hash(context)
    field_projections = []
    field_anchors = {}
    leaf_projections = []
    for field, value in sorted(context.items()):
        anchor = {
            "source_path": f"kernel_policy.{projection_type}.{field}",
            "source_value_sha256": _content_hash(value),
            "projection_operation": "registered_kernel_policy_derivation",
            "mapping_mode": "kernel_policy_derivation",
        }
        field_anchors[field] = anchor
        field_projections.append(
            {
                "projected_field": field,
                "value_sha256": _content_hash(value),
                **anchor,
            }
        )
        leaf_projections.append(
            {
                "projected_path": f"$.{field}",
                "value_sha256": _content_hash(value),
                "source_path": anchor["source_path"],
                "source_tokens": [],
                "source_value_sha256": anchor["source_value_sha256"],
                "projection_operation": anchor["projection_operation"],
            }
        )
    contract_core = {
        "policy_id": policy_id,
        "projection_type": projection_type,
        "recipient": recipient,
        "context_sha256": context_sha256,
        "field_anchors": field_anchors,
        "included_refs": ["test_context"],
        "excluded_refs": ["private_test_material"],
        "redaction_rule": "test projection rule",
        "compression_policy": "mechanical field selection only",
        "forbidden_downstream_use": ["private_test_material"],
    }
    contract = {
        "contract_id": f"pc_{_content_hash(contract_core)[:16]}",
        **contract_core,
    }
    manifest_core = {
        "context_sha256": context_sha256,
        "contract": contract,
    }
    manifest = {
        "manifest_id": f"pm_{_content_hash(manifest_core)[:16]}",
        "policy_id": policy_id,
        "projection_type": projection_type,
        "recipient": recipient,
        "context_sha256": context_sha256,
        "projection_contract_id": contract["contract_id"],
        "projection_contract_sha256": _content_hash(contract),
        "field_projections": field_projections,
        "leaf_projections": leaf_projections,
        "included_refs": ["test_context"],
        "excluded_refs": ["private_test_material"],
        "authority_basis": "runtime projection policy and recipient allowlist",
        "visibility_basis": "recipient-specific deterministic field selection",
        "redaction_rule": "test projection rule",
        "compression_policy": "mechanical field selection only",
        "forbidden_downstream_use": ["private_test_material"],
    }
    return manifest, contract


def _real_trace() -> dict:
    private_nonce = "private-nonce-value"
    private_run_id = "private-run-id-value"
    packet = {
        "packet_id": f"packet_{private_run_id}",
        "scene_id": "scene_test_001",
        "packet_scope": "world_driven_scene",
        "commit_status": "committed",
        "resolved_events": [],
        "state_deltas": [],
        "visibility_deltas": [],
        "publication_candidates": [],
        "canon_reveal_candidates": [],
        "pov_contract": {},
        "narration_bounds": {},
    }
    collections = [
        "resolved_events",
        "state_deltas",
        "visibility_deltas",
        "publication_candidates",
        "canon_reveal_candidates",
    ]
    packet["sealing_record"] = {
        "source_collection_sha256": {
            name: _content_hash(packet[name]) for name in collections
        },
        "sealed_payload_sha256": _content_hash(packet),
    }
    projected_context = {
        "context_type": "AuthorityReviewContext",
        "hidden": "candidate secret",
    }
    manifest, contract = _projection_evidence(projected_context)
    return {
        "fixture_path": r"D:\private\fixture.json",
        "runtime_mode": "world_driven",
        "runtime_status": "finished",
        "llm_mode": "codex-cli",
        "model": "gpt-test",
        "final_decision": "allowed",
        "run_nonce": private_nonce,
        "run_id": private_run_id,
        "projection_manifests": [manifest],
        "projection_contracts": [contract],
        "validation": {},
        "transaction": {"status": "committed", "policy": "scene_atomic"},
        "token_usage": {
            "totals": {
                "input_tokens": 10,
                "output_tokens": 5,
                "total_tokens": 15,
                "exact_agent_count": 1,
                "estimated_agent_count": 0,
            }
        },
        "agent_runs": [
            {
                "agent_name": "authority",
                "agent_instance_id": "authority_judge",
                "call_index": 0,
                "protocol_stage": "authority_subject",
                "projection_manifest_id": manifest["manifest_id"],
                "projection_contract_id": contract["contract_id"],
                "mode": "codex-cli",
                "error": None,
                "prompt": "secret projected prompt",
                "projected_context": projected_context,
                "raw_output": r"raw output mentions D:\private\auth.json",
                "parsed_output": {
                    "authority_review": {
                        "verdict": "allow",
                        "run_nonce": private_nonce,
                    }
                },
                "token_usage": {
                    "input_tokens": 10,
                    "output_tokens": 5,
                    "total_tokens": 15,
                    "is_estimated": False,
                    "source": "provider_usage",
                },
            }
        ],
        "published_narration_segments": [{"prose": "Grounded prose."}],
        "scene_packet": packet,
        "memory_handoff": {"derived_memory_deltas": []},
        "normalization_records": [],
    }


class PublicTraceExportTests(unittest.TestCase):
    def test_export_preserves_outputs_and_usage_without_private_trace_material(self) -> None:
        trace = _real_trace()
        private_nonce = trace["run_nonce"]
        private_run_id = trace["run_id"]

        document = render_public_trace(trace)
        _assert_sanitized(document, trace)

        self.assertIn('"verdict": "allow"', document)
        self.assertIn('"run_nonce": "[redacted-run-nonce]"', document)
        self.assertIn('"packet_id": "packet_[redacted-run-id]"', document)
        self.assertIn('"seal_scope": "sanitized_public_export"', document)
        self.assertIn('"source_private_seal_verified": true', document)
        self.assertIn("| `authority` | 1 | 10 | 5 | 15 |", document)
        self.assertNotIn(private_nonce, document)
        self.assertNotIn(private_run_id, document)
        self.assertNotIn("secret projected prompt", document)
        self.assertNotIn("candidate secret", document)
        self.assertNotIn("auth.json", document.lower())
        self.assertNotIn(r"D:\private", document)

    def test_export_reseals_the_sanitized_scene_packet(self) -> None:
        trace = _real_trace()
        private_packet = trace["scene_packet"]
        public_packet = _sanitize_and_reseal_scene_packet(
            private_packet, _private_run_replacements(trace)
        )

        public_hash = _content_hash(_scene_packet_payload(public_packet))
        self.assertEqual(
            public_packet["sealing_record"]["sealed_payload_sha256"], public_hash
        )
        self.assertNotEqual(
            private_packet["sealing_record"]["sealed_payload_sha256"], public_hash
        )

    def test_export_rejects_non_real_non_committed_or_estimated_traces(self) -> None:
        cases = []
        legacy_trace = _real_trace()
        legacy_trace["runtime_mode"] = "legacy_window_v0.1"
        cases.append(legacy_trace)
        mock_trace = _real_trace()
        mock_trace["llm_mode"] = "mock"
        cases.append(mock_trace)
        blocked_trace = _real_trace()
        blocked_trace["final_decision"] = "blocked"
        cases.append(blocked_trace)
        estimated_trace = _real_trace()
        estimated_trace["agent_runs"][0]["token_usage"]["is_estimated"] = True
        estimated_trace["agent_runs"][0]["token_usage"]["source"] = "local_estimate"
        cases.append(estimated_trace)

        for trace in cases:
            with self.subTest(trace=trace["llm_mode"], decision=trace["final_decision"]):
                with self.assertRaises(ValueError):
                    render_public_trace(trace)

    def test_export_rejects_an_invalid_private_scene_packet_seal(self) -> None:
        trace = _real_trace()
        trace["scene_packet"]["sealing_record"]["sealed_payload_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "private ScenePacket seal"):
            render_public_trace(trace)

    def test_export_requires_complete_projection_evidence(self) -> None:
        cases = []
        missing_manifests = _real_trace()
        missing_manifests["projection_manifests"] = []
        cases.append(missing_manifests)
        missing_contracts = _real_trace()
        missing_contracts["projection_contracts"] = []
        cases.append(missing_contracts)

        for trace in cases:
            with self.subTest(
                manifests=len(trace["projection_manifests"]),
                contracts=len(trace["projection_contracts"]),
            ):
                with self.assertRaisesRegex(ValueError, "projection"):
                    render_public_trace(trace)

    def test_export_rejects_blocking_projection_validation(self) -> None:
        trace = _real_trace()
        trace["validation"]["projection_authority_subject"] = [
            {
                "severity": "block",
                "kind": "projection_manifest",
                "code": "forged_projection",
            }
        ]
        with self.assertRaisesRegex(ValueError, "blocking validation"):
            render_public_trace(trace)

    def test_export_rejects_projection_recipient_or_hash_mismatch(self) -> None:
        cases = []
        wrong_recipient = _real_trace()
        wrong_recipient["projection_manifests"][0]["recipient"][
            "instance_id"
        ] = "another_judge"
        cases.append(wrong_recipient)
        wrong_hash = _real_trace()
        wrong_hash["projection_contracts"][0]["context_sha256"] = "0" * 64
        cases.append(wrong_hash)

        for trace in cases:
            with self.subTest(trace=trace):
                with self.assertRaisesRegex(ValueError, "projection|context hash"):
                    render_public_trace(trace)

    def test_export_rejects_incomplete_or_inconsistent_leaf_evidence(self) -> None:
        cases = []

        missing_leaves = _real_trace()
        missing_leaves["projection_manifests"][0]["leaf_projections"] = []
        cases.append(missing_leaves)

        wrong_source_path = _real_trace()
        wrong_source_path["projection_manifests"][0]["leaf_projections"][0][
            "source_path"
        ] = "fixture.latent_canon"
        cases.append(wrong_source_path)

        wrong_value_hash = _real_trace()
        wrong_value_hash["projection_manifests"][0]["leaf_projections"][0][
            "value_sha256"
        ] = "0" * 64
        cases.append(wrong_value_hash)

        for trace in cases:
            with self.subTest(trace=trace):
                with self.assertRaisesRegex(ValueError, "leaf"):
                    render_public_trace(trace)

    def test_export_rejects_manifest_contract_policy_drift(self) -> None:
        trace = _real_trace()
        trace["projection_manifests"][0]["excluded_refs"] = []

        with self.assertRaisesRegex(ValueError, "projection policy"):
            render_public_trace(trace)

    def test_export_requires_agent_calls(self) -> None:
        with self.assertRaisesRegex(ValueError, "agent_runs"):
            render_public_trace({"agent_runs": []})

    def test_sanitizer_rejects_a_path_inside_parsed_output(self) -> None:
        trace = {"run_nonce": "private-nonce"}
        with self.assertRaisesRegex(ValueError, "windows absolute path"):
            _assert_sanitized(r'prose accidentally echoed C:\\private\\trace.json', trace)

    def test_sanitizer_rejects_an_embedded_private_run_id(self) -> None:
        trace = {"run_id": "private-run-id"}
        with self.assertRaisesRegex(ValueError, "private run identifier"):
            _assert_sanitized("packet_private-run-id", trace)


if __name__ == "__main__":
    unittest.main()
