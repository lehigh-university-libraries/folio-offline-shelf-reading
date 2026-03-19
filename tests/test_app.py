"""
Unit tests for save_items route and modify_item helper.

conftest.py mocks FolioClient and ConfigParser.read_file at module level so
that importing application.app is safe without a real FOLIO connection.
"""

from unittest.mock import ANY, patch

import application.app as app_module
from application.app import SHELF_STATUS, app, modify_item
from flask import session

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ITEM_UUID = "550e8400-e29b-41d4-a716-446655440000"

SUCCESS_RESULT = {"barcode": "12345", "text": "Saved", "success": True}
CHECKED_IN_RESULT = {"barcode": "12345", "text": "Checked in", "success": True}
MISSING_RESULT = {"barcode": "12345", "text": "Marked as missing", "success": True}


def _make_item(status="Available"):
    return {
        "id": _ITEM_UUID,
        "barcode": "12345",
        "statisticalCodeIds": [],
        "notes": [],
        "status": {"name": status},
        "effectiveLocation": {"id": "loc-id", "name": "Main Library"},
    }


# ---------------------------------------------------------------------------
# modify_item tests
# ---------------------------------------------------------------------------


def test_modify_item_no_condition_adds_stat_code_and_note():
    item = _make_item()
    with app.test_request_context():
        session["username"] = "testuser"
        result = modify_item(item, "Present", None)

    assert app_module.inventoried_statistical_code["id"] in result["statisticalCodeIds"]
    assert len(result["notes"]) == 1
    note = result["notes"][0]
    assert note["itemNoteTypeId"] == app_module.inventoried_item_note_type
    assert "Shelf status: Present" in note["note"]
    assert note["staffOnly"] is True
    assert "itemDamagedStatusId" not in result


def test_modify_item_shelf_status_appears_in_note():
    item = _make_item()
    with app.test_request_context():
        session["username"] = "testuser"
        result = modify_item(item, "Missing", None)

    assert "Shelf status: Missing" in result["notes"][0]["note"]


def test_modify_item_non_damaging_condition_adds_condition_note():
    item = _make_item()
    with app.test_request_context():
        session["username"] = "testuser"
        result = modify_item(item, "Present", "Worn")

    assert len(result["notes"]) == 2
    cond_note = result["notes"][1]
    assert (
        cond_note["itemNoteTypeId"] == app_module.inventoried_item_condition_note_type
    )
    assert "Worn" in cond_note["note"]
    assert "itemDamagedStatusId" not in result


def test_modify_item_damaging_condition_sets_damage_status():
    item = _make_item()
    with app.test_request_context():
        session["username"] = "testuser"
        result = modify_item(item, "Present", "Spine damage")

    assert len(result["notes"]) == 2
    assert result["itemDamagedStatusId"] == app_module.item_damage_status
    assert "itemDamagedStatusDate" in result


# ---------------------------------------------------------------------------
# save_items route tests
# ---------------------------------------------------------------------------


def test_save_items_validation_error_returns_failure(client):
    response = client.post(
        "/save-items", json=[{"barcode": "not-numeric!!!", "shelf_status": "Present"}]
    )
    data = response.get_json()

    assert len(data) == 1
    assert data[0]["success"] is False
    assert "Invalid barcode" in data[0]["text"]


def test_save_items_unknown_barcode_returns_failure(client):
    with patch("application.app.load_item", return_value=None):
        response = client.post(
            "/save-items", json=[{"barcode": "12345", "shelf_status": "Present"}]
        )
    data = response.get_json()

    assert len(data) == 1
    assert data[0]["success"] is False
    assert "Unknown barcode" in data[0]["text"]


def test_save_items_present_item_not_in_check_in_statuses(client):
    item = _make_item(status="Available")
    with patch("application.app.load_item", return_value=item), patch(
        "application.app.save_item", return_value=SUCCESS_RESULT
    ) as mock_save, patch("application.app.mark_item_checked_in") as mock_checkin:
        response = client.post(
            "/save-items", json=[{"barcode": "12345", "shelf_status": "Present"}]
        )
    data = response.get_json()

    assert data[0]["success"] is True
    mock_save.assert_called_once()
    mock_checkin.assert_not_called()


def test_save_items_present_item_in_check_in_statuses_triggers_checkin(client):
    item = _make_item(status="Checked out")
    with patch("application.app.load_item", return_value=item), patch(
        "application.app.save_item", return_value=SUCCESS_RESULT
    ), patch(
        "application.app.mark_item_checked_in", return_value=CHECKED_IN_RESULT
    ) as mock_checkin:
        response = client.post(
            "/save-items", json=[{"barcode": "12345", "shelf_status": "Present"}]
        )
    data = response.get_json()

    assert data[0]["success"] is True
    mock_checkin.assert_called_once()


def test_save_items_unavailable_on_shelf_triggers_checkin(client):
    item = _make_item(status="Checked out")
    with patch("application.app.load_item", return_value=item), patch(
        "application.app.save_item", return_value=SUCCESS_RESULT
    ), patch(
        "application.app.mark_item_checked_in", return_value=CHECKED_IN_RESULT
    ) as mock_checkin:
        response = client.post(
            "/save-items",
            json=[
                {
                    "barcode": "12345",
                    "shelf_status": SHELF_STATUS["UNAVAILABLE_BUT_ON_SHELF"],
                }
            ],
        )
    data = response.get_json()

    assert data[0]["success"] is True
    mock_checkin.assert_called_once()


def test_save_items_missing_status_triggers_mark_missing(client):
    item = _make_item()
    with patch("application.app.load_item", return_value=item), patch(
        "application.app.save_item", return_value=SUCCESS_RESULT
    ), patch(
        "application.app.mark_item_missing", return_value=MISSING_RESULT
    ) as mock_missing:
        response = client.post(
            "/save-items", json=[{"barcode": "12345", "shelf_status": "Missing"}]
        )
    data = response.get_json()

    assert data[0]["success"] is True
    mock_missing.assert_called_once()


def test_save_items_multiple_items_returns_result_per_item(client):
    item = _make_item()
    with patch("application.app.load_item", side_effect=[item, None]), patch(
        "application.app.save_item", return_value=SUCCESS_RESULT
    ):
        response = client.post(
            "/save-items",
            json=[
                {"barcode": "12345", "shelf_status": "Present"},
                {"barcode": "99999", "shelf_status": "Present"},
            ],
        )
    data = response.get_json()

    assert len(data) == 2
    assert data[0]["success"] is True
    assert data[1]["success"] is False
    assert "Unknown barcode" in data[1]["text"]


def test_save_items_item_id_is_passed_to_load_item(client):
    """item_id supplied in input should be forwarded to load_item, not discarded."""
    item = _make_item()
    with patch("application.app.load_item", return_value=item) as mock_load, patch(
        "application.app.save_item", return_value=SUCCESS_RESULT
    ):
        client.post(
            "/save-items",
            json=[{"id": _ITEM_UUID, "barcode": "12345", "shelf_status": "Present"}],
        )

    mock_load.assert_called_once_with(ANY, _ITEM_UUID, "12345")


# ---------------------------------------------------------------------------
# load_conditions route tests
# ---------------------------------------------------------------------------


def test_load_conditions_returns_conditions(client):
    response = client.get("/load-conditions")

    assert response.status_code == 200
    data = response.get_json()
    assert ["11111", "Worn"] in data
    assert ["22222", "Spine damage"] in data
    assert ["99999", "<custom>"] in data
