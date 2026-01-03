#!/usr/bin/env python3
"""
Simple tests for TrustyNet Bot storage functionality.
Tests only the TrustStorage class without requiring telegram dependencies.
"""

import json
import os
from pathlib import Path
from datetime import datetime


class TrustStorage:
    """Handles storage and retrieval of trust relationships."""
    
    def __init__(self, data_file: str):
        self.data_file = Path(data_file)
        self.data = self._load_data()
    
    def _load_data(self):
        """Load trust data from file."""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading data: {e}")
                return {"groups": {}, "trusts": []}
        return {"groups": {}, "trusts": []}
    
    def _save_data(self):
        """Save trust data to file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def add_group(self, group_id: int, group_name: str, owner_id: int, owner_name: str):
        """Record a group with its owner."""
        group_id_str = str(group_id)
        self.data["groups"][group_id_str] = {
            "name": group_name,
            "owner_id": owner_id,
            "owner_name": owner_name,
            "added_at": datetime.now().isoformat()
        }
        self._save_data()
        print(f"Added group {group_name} (ID: {group_id}) with owner {owner_name}")
    
    def add_trust(self, group_id: int, truster_id: int, truster_name: str, 
                  trustee_id: int, trustee_name: str):
        """Record a trust relationship."""
        trust_record = {
            "group_id": group_id,
            "truster_id": truster_id,
            "truster_name": truster_name,
            "trustee_id": trustee_id,
            "trustee_name": trustee_name,
            "created_at": datetime.now().isoformat()
        }
        
        # Check if trust already exists
        for trust in self.data["trusts"]:
            if (trust["group_id"] == group_id and 
                trust["truster_id"] == truster_id and 
                trust["trustee_id"] == trustee_id):
                print(f"Trust already exists: {truster_name} -> {trustee_name}")
                return
        
        self.data["trusts"].append(trust_record)
        self._save_data()
        print(f"Added trust: {truster_name} trusts {trustee_name} in group {group_id}")
    
    def get_group_trusts(self, group_id: int):
        """Get all trust relationships for a group."""
        return [t for t in self.data["trusts"] if t["group_id"] == group_id]
    
    def get_user_trusts(self, user_id: int):
        """Get all trusts where user is the truster."""
        return [t for t in self.data["trusts"] if t["truster_id"] == user_id]


def test_storage_initialization():
    """Test that storage initializes correctly."""
    test_file = "/tmp/test_trust_init.json"
    if Path(test_file).exists():
        os.remove(test_file)
    
    storage = TrustStorage(test_file)
    assert storage.data == {"groups": {}, "trusts": []}
    print("✓ Storage initialization test passed")


def test_add_group():
    """Test adding a group."""
    test_file = "/tmp/test_trust_group.json"
    if Path(test_file).exists():
        os.remove(test_file)
    
    storage = TrustStorage(test_file)
    storage.add_group(
        group_id=-123456,
        group_name="Test Group",
        owner_id=111111,
        owner_name="Test Owner"
    )
    
    assert "-123456" in storage.data["groups"]
    group = storage.data["groups"]["-123456"]
    assert group["name"] == "Test Group"
    assert group["owner_id"] == 111111
    assert group["owner_name"] == "Test Owner"
    print("✓ Add group test passed")


def test_add_trust():
    """Test adding a trust relationship."""
    test_file = "/tmp/test_trust_add.json"
    if Path(test_file).exists():
        os.remove(test_file)
    
    storage = TrustStorage(test_file)
    storage.add_trust(
        group_id=-123456,
        truster_id=111111,
        truster_name="Owner",
        trustee_id=222222,
        trustee_name="Member"
    )
    
    assert len(storage.data["trusts"]) == 1
    trust = storage.data["trusts"][0]
    assert trust["group_id"] == -123456
    assert trust["truster_id"] == 111111
    assert trust["trustee_id"] == 222222
    print("✓ Add trust test passed")


def test_duplicate_trust():
    """Test that duplicate trusts are not added."""
    test_file = "/tmp/test_trust_dup.json"
    if Path(test_file).exists():
        os.remove(test_file)
    
    storage = TrustStorage(test_file)
    
    # Add first trust
    storage.add_trust(-123456, 111111, "Owner", 222222, "Member")
    assert len(storage.data["trusts"]) == 1
    
    # Try to add duplicate
    storage.add_trust(-123456, 111111, "Owner", 222222, "Member")
    assert len(storage.data["trusts"]) == 1  # Should still be 1
    print("✓ Duplicate trust test passed")


def test_persistence():
    """Test that data persists across storage instances."""
    test_file = "/tmp/test_trust_persist.json"
    if Path(test_file).exists():
        os.remove(test_file)
    
    # Create first storage and add data
    storage1 = TrustStorage(test_file)
    storage1.add_group(-123456, "Test Group", 111111, "Owner")
    storage1.add_trust(-123456, 111111, "Owner", 222222, "Member")
    
    # Create second storage and verify data persists
    storage2 = TrustStorage(test_file)
    assert "-123456" in storage2.data["groups"]
    assert len(storage2.data["trusts"]) == 1
    print("✓ Persistence test passed")


def test_get_group_trusts():
    """Test getting trusts for a specific group."""
    test_file = "/tmp/test_trust_get.json"
    if Path(test_file).exists():
        os.remove(test_file)
    
    storage = TrustStorage(test_file)
    
    # Add trusts for multiple groups
    storage.add_trust(-111, 100, "Owner1", 200, "Member1")
    storage.add_trust(-111, 100, "Owner1", 201, "Member2")
    storage.add_trust(-222, 300, "Owner2", 400, "Member3")
    
    # Get trusts for first group
    group1_trusts = storage.get_group_trusts(-111)
    assert len(group1_trusts) == 2
    
    # Get trusts for second group
    group2_trusts = storage.get_group_trusts(-222)
    assert len(group2_trusts) == 1
    print("✓ Get group trusts test passed")


def run_tests():
    """Run all tests."""
    print("Running TrustyNet Bot Storage Tests...\n")
    
    try:
        test_storage_initialization()
        test_add_group()
        test_add_trust()
        test_duplicate_trust()
        test_persistence()
        test_get_group_trusts()
        
        print("\n✅ All tests passed!")
        return 0
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(run_tests())
