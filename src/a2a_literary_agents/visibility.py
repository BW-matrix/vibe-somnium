"""Deterministic visibility and encounter checks for projected contexts."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


PUBLIC_SCOPE_NAMES = {
    "scene_public",
    "local_public",
    "institution_public",
    "city_public",
    "realm_public",
}
DIRECT_OBSERVER_SCOPES = {
    "private_self",
    "private_target",
    "scene_pair",
    "restricted_subset",
}
PUBLIC_EVENT_VIEW_FIELDS = {
    "publication_id",
    "source_event_ref",
    "effective_scope",
    "scope_ref",
    "public_summary",
    "report_form",
    "certainty",
    "contestability",
    "published_at",
}


def event_visible_to(
    event: dict[str, Any], character_id: str, fixture: dict[str, Any]
) -> bool:
    visibility = event.get("visibility")
    if not isinstance(visibility, dict):
        return False
    scope = visibility.get("scope")
    observers = visibility.get("observer_refs", [])
    if not isinstance(scope, str):
        return False
    if scope == "private_self":
        actors = event.get("actors")
        return (
            isinstance(actors, list)
            and bool(actors)
            and isinstance(observers, list)
            and observers == [actors[0]]
            and visibility.get("scope_ref") == actors[0]
            and character_id == actors[0]
        )
    if scope == "scene_pair":
        participants = fixture.get("scene_participant_ids")
        return (
            isinstance(observers, list)
            and len(observers) == 2
            and all(isinstance(observer, str) for observer in observers)
            and len(set(observers)) == 2
            and isinstance(participants, list)
            and all(observer in participants for observer in observers)
            and character_id in observers
        )
    if scope in DIRECT_OBSERVER_SCOPES:
        return isinstance(observers, list) and character_id in observers
    if scope == "system_restricted":
        return False
    if scope == "scene_public":
        if visibility.get("scope_ref") != fixture.get("scene_id"):
            return False
        participants = fixture.get("scene_participant_ids")
        if not isinstance(participants, list):
            return False
        return (
            isinstance(observers, list)
            and character_id in observers
            and character_id in participants
        )
    if scope in PUBLIC_SCOPE_NAMES:
        scope_ref = visibility.get("scope_ref")
        registry = fixture.get("public_scope_registry", {})
        entry = registry.get(scope_ref, {}) if isinstance(registry, dict) else {}
        if not isinstance(entry, dict) or entry.get("scope_type") != scope:
            return False
        members = entry.get("members", [])
        return (
            isinstance(observers, list)
            and character_id in observers
            and isinstance(members, list)
            and character_id in members
        )
    return False


def event_directly_observed_by(
    event: dict[str, Any], character_id: str, fixture: dict[str, Any]
) -> bool:
    """Return whether a committed event can enter owner memory as observation."""

    visibility = event.get("visibility")
    if not isinstance(visibility, dict):
        return False
    observers = visibility.get("observer_refs")
    return (
        isinstance(observers, list)
        and character_id in observers
        and event_visible_to(event, character_id, fixture)
    )


def visible_event_views(
    events: list[dict[str, Any]], character_id: str, fixture: dict[str, Any]
) -> list[dict[str, Any]]:
    return [
        {
            "event_id": event.get("event_id"),
            "public_surface": event.get("public_surface"),
            "visibility": projected_visibility(event),
        }
        for event in events
        if event_visible_to(event, character_id, fixture)
    ]


def encountered_public_events(
    fixture: dict[str, Any], character_id: str
) -> list[dict[str, Any]]:
    encountered_refs = set(
        fixture.get("encountered_public_event_refs", {}).get(character_id, [])
    )
    return [
        public_event_view(event)
        for event in fixture.get("public_event_ledger", [])
        if event.get("publication_id") in encountered_refs
        and public_event_available_to(event, character_id, fixture)
    ]


def public_event_available_to(
    event: dict[str, Any], character_id: str, fixture: dict[str, Any]
) -> bool:
    scope = event.get("effective_scope")
    scope_ref = event.get("scope_ref")
    if not isinstance(scope, str):
        return False
    if scope == "scene_public":
        participants = fixture.get("scene_participant_ids")
        return (
            scope_ref == fixture.get("scene_id")
            and isinstance(participants, list)
            and character_id in participants
        )
    if scope in PUBLIC_SCOPE_NAMES:
        registry = fixture.get("public_scope_registry", {})
        entry = registry.get(scope_ref, {}) if isinstance(registry, dict) else {}
        members = entry.get("members", []) if isinstance(entry, dict) else []
        return (
            isinstance(entry, dict)
            and entry.get("scope_type") == scope
            and isinstance(members, list)
            and character_id in members
        )
    return False


def public_event_view(event: dict[str, Any]) -> dict[str, Any]:
    return {
        field: deepcopy(event[field])
        for field in PUBLIC_EVENT_VIEW_FIELDS
        if field in event
    }


def public_event_views(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [public_event_view(event) for event in events if isinstance(event, dict)]


def projected_visibility(event: dict[str, Any]) -> dict[str, Any]:
    visibility = event.get("visibility", {})
    if not isinstance(visibility, dict):
        return {}
    return {
        field: deepcopy(visibility[field])
        for field in ["scope", "scope_ref"]
        if field in visibility
    }


def legal_character_trigger_refs(
    fixture: dict[str, Any],
    runtime_state: dict[str, Any],
    character_id: str,
) -> set[str]:
    refs: set[str] = set()
    for observation in fixture.get("visible_observations", {}).get(character_id, []):
        if isinstance(observation, dict) and isinstance(observation.get("observation_id"), str):
            refs.add(observation["observation_id"])
    refs.update(
        str(event["publication_id"])
        for event in encountered_public_events(fixture, character_id)
        if event.get("publication_id")
    )
    refs.update(
        str(event["event_id"])
        for event in runtime_state.get("committed_world_events", [])
        if event.get("event_id") and event_visible_to(event, character_id, fixture)
    )
    return refs
