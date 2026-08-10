from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _analysis_payload() -> dict[str, object]:
    return {
        "application": {
            "application_type": "web",
            "frontend_technology": "playwright",
            "architecture_style": "modular monolith",
        },
        "interfaces": {
            "web_ui": True,
            "rest_api": False,
            "graphql": False,
            "database": False,
            "messaging": False,
        },
        "automation": {
            "ui_testing": False,
            "api_testing": True,
            "integration_testing": False,
            "performance_testing": False,
            "accessibility_testing": False,
        },
        "execution": {
            "expected_test_count": 20,
            "target_execution_minutes": 10,
            "parallel_execution": False,
            "browsers": [],
        },
        "delivery": {
            "ci_provider": "github actions",
            "release_frequency": "daily",
            "pull_request_validation": False,
        },
        "team": {
            "team_size": 2,
            "languages": [],
            "automation_experience": "intermediate",
        },
        "preferences": {
            "preferred_technologies": ["  PLAYWRIGHT  ", "SELENIUM", "SELENIUM"],
        },
        "constraints": {
            "approved_technologies": ["  PLAYWRIGHT  "],
            "prohibited_technologies": [" playwright "],
            "compliance_requirements": [],
        },
    }


def test_analysis_returns_structured_normalized_traceable_result() -> None:
    response = client.post("/api/v1/requirements/analyze", json=_analysis_payload())

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "normalization",
        "completeness",
        "conflicts",
        "classification",
        "engineering_policies",
    }

    normalized = body["normalization"]["normalized_requirements"]
    assert normalized["constraints"]["approved_technologies"] == ["playwright"]
    assert normalized["preferences"]["preferred_technologies"] == [
        "playwright",
        "selenium",
        "selenium",
    ]
    assert normalized["constraints"]["prohibited_technologies"] == ["playwright"]
    assert normalized["automation"]["ui_testing"] is False
    assert normalized["automation"]["api_testing"] is True
    assert normalized["execution"]["browsers"] == []
    assert normalized["constraints"]["compliance_requirements"] == []

    approved_change = next(
        change
        for change in body["normalization"]["changes"]
        if change["field_path"] == "constraints.approved_technologies[0]"
    )
    assert approved_change["normalized_value"] == "playwright"
    assert approved_change["trace_references"] == [
        {"field_path": "constraints.approved_technologies[0]"}
    ]

    assert body["conflicts"]["has_conflicts"] is True
    assert body["conflicts"]["conflict_count"] == 2
    assert body["conflicts"]["conflicts"][0]["conflicting_value"] == "playwright"
    assert body["conflicts"]["conflicts"][0]["trace_references"] == [
        {"field_path": "constraints.approved_technologies"},
        {"field_path": "constraints.prohibited_technologies"},
    ]
    assert body["engineering_policies"]["findings"][0]["trace_references"] == [
        {"field_path": "automation.api_testing"}
    ]
    classifications = body["classification"]["classifications"]
    assert [(item["field_path"], item["kind"], item["value"]) for item in classifications] == [
        ("preferences.preferred_technologies[0]", "preference", "playwright"),
        ("preferences.preferred_technologies[1]", "preference", "selenium"),
        ("preferences.preferred_technologies[2]", "preference", "selenium"),
        ("constraints.approved_technologies[0]", "constraint", "playwright"),
        ("constraints.prohibited_technologies[0]", "constraint", "playwright"),
    ]
    assert classifications[0]["trace_references"] == [
        {"field_path": "preferences.preferred_technologies[0]"}
    ]


def test_analysis_preserves_none_false_and_empty_collection_semantics() -> None:
    response = client.post(
        "/api/v1/requirements/analyze",
        json={
            "automation": {"ui_testing": False, "api_testing": None},
            "execution": {"parallel_execution": False, "browsers": []},
            "constraints": {
                "approved_technologies": None,
                "prohibited_technologies": [],
            },
            "preferences": {"preferred_technologies": []},
        },
    )

    assert response.status_code == 200
    normalized = response.json()["normalization"]["normalized_requirements"]
    assert normalized["automation"]["ui_testing"] is False
    assert normalized["automation"]["api_testing"] is None
    assert normalized["execution"]["parallel_execution"] is False
    assert normalized["execution"]["browsers"] == []
    assert normalized["constraints"]["approved_technologies"] is None
    assert normalized["constraints"]["prohibited_technologies"] == []
    assert normalized["preferences"]["preferred_technologies"] == []


def test_omitted_and_null_preferences_preserve_transport_semantics() -> None:
    omitted = client.post("/api/v1/requirements/analyze", json={})
    supplied_null = client.post(
        "/api/v1/requirements/analyze",
        json={"preferences": {"preferred_technologies": None}},
    )

    assert omitted.status_code == 200
    assert supplied_null.status_code == 200
    assert omitted.json()["normalization"]["normalized_requirements"]["preferences"] == {
        "preferred_technologies": None
    }
    assert supplied_null.json()["normalization"]["normalized_requirements"]["preferences"] == {
        "preferred_technologies": None
    }


def test_completeness_missing_trace_references_are_serialized() -> None:
    response = client.post("/api/v1/requirements/analyze", json={})

    assert response.status_code == 200
    completeness = response.json()["completeness"]
    assert completeness["missing_requirements"]
    assert completeness["missing_trace_references"][0] == {
        "field_path": completeness["missing_requirements"][0]
    }


def test_invalid_types_unknown_fields_and_domain_invariants_return_422() -> None:
    invalid_type = client.post(
        "/api/v1/requirements/analyze",
        json={"automation": {"api_testing": {"unexpected": "object"}}},
    )
    unknown_field = client.post(
        "/api/v1/requirements/analyze",
        json={"automation": {"unknown_capability": True}},
    )
    invalid_domain_value = client.post(
        "/api/v1/requirements/analyze",
        json={"execution": {"target_execution_minutes": 0}},
    )

    assert invalid_type.status_code == 422
    assert unknown_field.status_code == 422
    assert invalid_domain_value.status_code == 422


def test_analysis_route_is_documented_and_dependency_direction_stays_inward() -> None:
    operation = app.openapi()["paths"]["/api/v1/requirements/analyze"]
    repository_root = Path(__file__).parents[1]
    application_sources = (repository_root / "app" / "application").rglob("*.py")
    domain_sources = (repository_root / "app" / "domain").rglob("*.py")

    assert set(operation) == {"post"}
    assert operation["post"]["responses"]["200"]
    assert all(
        "app.api" not in source.read_text(encoding="utf-8")
        and "pydantic" not in source.read_text(encoding="utf-8").casefold()
        for source in (*application_sources, *domain_sources)
    )
