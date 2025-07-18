# tests/test_memory.py

import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from pathlib import Path
from memory.polaris_memory import PolarisMemory
from memory.models import MemoryObject
from datetime import datetime


@pytest.fixture
def sample_memory():
    path = Path("library/domains/urban_permitting/denpasar_v1/")
    return PolarisMemory(path)


def test_loads_memory_objects(sample_memory):
    # Ensure some known IDs or at least types exist
    objs = sample_memory.get_by_type("PermittingModule")
    assert isinstance(objs, list)
    assert len(objs) > 0


def test_get_by_id(sample_memory):
    all_objs = sample_memory.get_by_type("PermittingModule")
    test_id = all_objs[0].id
    result = sample_memory.get_by_id(test_id)
    assert result is not None
    assert result.id == test_id


def test_query_by_tag(sample_memory):
    # Add a tag and query it
    objs = sample_memory.get_by_type("PermittingModule")
    test_obj = objs[0]
    sample_memory.add_tag(test_obj.id, "#test_tag")

    results = sample_memory.query_by_tag("#test_tag")
    assert any(obj.id == test_obj.id for obj in results)


def test_create_version(sample_memory):
    base = sample_memory.get_by_type("PermittingModule")[0]
    new_data = {**base.data, "duration_days": 123}
    new_obj = sample_memory.create_version(base.id, new_data, created_by="test-user")

    assert new_obj is not None
    assert new_obj.previous_version == base.id
    assert new_obj.id != base.id
    assert new_obj.data["duration_days"] == 123


def test_add_and_remove_tag(sample_memory):
    obj = sample_memory.get_by_type("PermittingModule")[0]
    sample_memory.add_tag(obj.id, "#transient")

    assert "#transient" in sample_memory.get_by_id(obj.id).tags

    sample_memory.remove_tag(obj.id, "#transient")
    assert "#transient" not in sample_memory.get_by_id(obj.id).tags


def test_query_filter_fn(sample_memory):
    results = sample_memory.query(lambda o: "Environmental" in o.data.get("module_name", ""))
    assert isinstance(results, list)
    assert all("Environmental" in o.data.get("module_name", "") for o in results)
