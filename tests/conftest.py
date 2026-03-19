"""
Test configuration and fixtures.

This module must be loaded by pytest before any test file imports application.app,
because application.app calls create_app() at module level, which connects to FOLIO.
The module-level patches here (sys.modules and ConfigParser.read_file) ensure that
import of application.app is safe without a real FOLIO connection or config file.
"""

import configparser
import sys
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# 1. Mock folioclient — must happen before application.app is imported
# ---------------------------------------------------------------------------

_folio_instance = MagicMock()
_folio_instance.__enter__ = MagicMock(return_value=_folio_instance)
_folio_instance.__exit__ = MagicMock(return_value=False)


def _init_folio_get(path, key=None, query_params=None):
    """Return canned data that satisfies init_folio() lookups."""
    data = {
        "/statistical-codes": [
            {"code": "inv", "id": "stat-code-id", "name": "Inventoried 2025"}
        ],
        "/item-note-types": [
            {"name": "Inventory", "id": "note-type-id"},
            {"name": "Condition", "id": "cond-note-type-id"},
        ],
        "/item-damaged-statuses": [{"name": "Damaged", "id": "damage-status-id"}],
        "/locations": [{"id": "loc-id", "primaryServicePoint": "sp-id"}],
    }
    return data.get(path, MagicMock())


_folio_instance.folio_get.side_effect = _init_folio_get

sys.modules["folioclient"] = MagicMock(
    FolioClient=MagicMock(return_value=_folio_instance)
)

# ---------------------------------------------------------------------------
# 2. Patch ConfigParser.read_file to use a self-contained test config
#    (avoids needing config/config.properties on disk)
# ---------------------------------------------------------------------------

_TEST_CONFIG = {
    "FOLIO": {
        "base_url": "http://folio.test",
        "tenant": "test",
        "username": "testuser",
        "password": "testpass",
        "inventoried_statistical_code": "inv",
        "inventoried_item_note_type": "Inventory",
        "inventoried_item_condition_note_type": "Condition",
        "item_damage_status": "Damaged",
    },
    "Testing": {
        "secret_key": "test-secret-key",
        "enabled": "False",
    },
    "Conditions": {
        "11111": "Worn",
        "22222": "Spine damage",
        "99999": "<custom>",
    },
    "ConditionsDamageFlag": {
        "11111": "False",
        "22222": "True",
        "99999": "False",
    },
    "Validation": {
        "BARCODE": r"^\d+$",
        "ITEM_ID": r"^[0-9a-fA-F\-]{36}$",
        "SHELF_STATUS": (
            r"^(Present|Missing|Unavailable item is on shelf"
            r"|Unavailable as expected|Ignoring: Already inventoried)$"
        ),
        "SHELF_CONDITION": r"^[\w\s]+$",
    },
    "Logging": {"level": "WARNING"},
    "MetaDB": {"items_query_url": "http://test"},
    "Email": {
        "smtp_host": "localhost",
        "from_address": "test@example.com",
        "from_name": "Test",
        "to_address": "dest@example.com",
        "subject": "Shelf reading results",
    },
}

configparser.ConfigParser.read_file = lambda self, f: self.read_dict(_TEST_CONFIG)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def client():
    """Flask test client with a pre-authenticated session."""
    from application.app import app

    app.config["TESTING"] = True
    with app.test_client() as c:
        with c.session_transaction() as sess:
            sess["username"] = "testuser"
        yield c
