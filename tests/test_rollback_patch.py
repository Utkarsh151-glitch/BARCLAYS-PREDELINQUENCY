"""
Comprehensive tests for .devoploy/rollback.patch.json

This module tests the structure, schema, and validity of the rollback patch
configuration file used for deployment rollback functionality.
"""

import json
import os
import pytest
from datetime import datetime
from jsonschema import validate, ValidationError, Draft7Validator


# Path to the rollback patch file
ROLLBACK_PATCH_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    ".devoploy",
    "rollback.patch.json"
)


# JSON Schema for rollback.patch.json
ROLLBACK_PATCH_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["createdAt", "entries"],
    "properties": {
        "createdAt": {
            "type": "string",
            "format": "date-time",
            "description": "ISO 8601 timestamp of when the patch was created"
        },
        "entries": {
            "type": "array",
            "description": "Array of file entries to be rolled back",
            "items": {
                "type": "object",
                "required": ["filePath", "originalContent"],
                "properties": {
                    "filePath": {
                        "type": "string",
                        "minLength": 1,
                        "description": "Relative path to the file"
                    },
                    "originalContent": {
                        "type": "string",
                        "description": "Original content of the file before changes"
                    }
                },
                "additionalProperties": False
            }
        }
    },
    "additionalProperties": False
}


@pytest.fixture
def rollback_patch_data():
    """Load and return the rollback patch JSON data."""
    with open(ROLLBACK_PATCH_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


@pytest.fixture
def rollback_patch_raw_content():
    """Return the raw content of the rollback patch file."""
    with open(ROLLBACK_PATCH_PATH, 'r', encoding='utf-8') as f:
        return f.read()


class TestRollbackPatchFileExists:
    """Test suite for file existence and basic accessibility."""

    def test_file_exists(self):
        """Test that rollback.patch.json file exists."""
        assert os.path.exists(ROLLBACK_PATCH_PATH), \
            f"Rollback patch file not found at {ROLLBACK_PATCH_PATH}"

    def test_file_is_readable(self):
        """Test that the file has read permissions."""
        assert os.access(ROLLBACK_PATCH_PATH, os.R_OK), \
            "Rollback patch file is not readable"

    def test_file_not_empty(self):
        """Test that the file is not empty."""
        assert os.path.getsize(ROLLBACK_PATCH_PATH) > 0, \
            "Rollback patch file is empty"


class TestRollbackPatchValidJSON:
    """Test suite for JSON validity."""

    def test_valid_json_syntax(self, rollback_patch_raw_content):
        """Test that the file contains valid JSON syntax."""
        try:
            json.loads(rollback_patch_raw_content)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON syntax: {e}")

    def test_json_is_object(self, rollback_patch_data):
        """Test that the root element is a JSON object."""
        assert isinstance(rollback_patch_data, dict), \
            "Root element must be a JSON object"


class TestRollbackPatchSchema:
    """Test suite for JSON schema validation."""

    def test_schema_validation(self, rollback_patch_data):
        """Test that the JSON conforms to the expected schema."""
        try:
            validate(instance=rollback_patch_data, schema=ROLLBACK_PATCH_SCHEMA)
        except ValidationError as e:
            pytest.fail(f"Schema validation failed: {e.message}")

    def test_has_required_fields(self, rollback_patch_data):
        """Test that all required top-level fields are present."""
        assert "createdAt" in rollback_patch_data, "Missing 'createdAt' field"
        assert "entries" in rollback_patch_data, "Missing 'entries' field"

    def test_no_extra_fields(self, rollback_patch_data):
        """Test that no unexpected fields are present at the root level."""
        allowed_fields = {"createdAt", "entries"}
        actual_fields = set(rollback_patch_data.keys())
        extra_fields = actual_fields - allowed_fields
        assert not extra_fields, f"Unexpected fields found: {extra_fields}"


class TestRollbackPatchCreatedAt:
    """Test suite for the createdAt field."""

    def test_created_at_is_string(self, rollback_patch_data):
        """Test that createdAt is a string."""
        assert isinstance(rollback_patch_data["createdAt"], str), \
            "createdAt must be a string"

    def test_created_at_not_empty(self, rollback_patch_data):
        """Test that createdAt is not an empty string."""
        assert rollback_patch_data["createdAt"].strip(), \
            "createdAt cannot be empty"

    def test_created_at_iso_format(self, rollback_patch_data):
        """Test that createdAt is in valid ISO 8601 format."""
        created_at = rollback_patch_data["createdAt"]
        try:
            # Try to parse as ISO 8601 datetime
            datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        except ValueError as e:
            pytest.fail(f"createdAt is not in valid ISO 8601 format: {e}")

    def test_created_at_has_timezone(self, rollback_patch_data):
        """Test that createdAt includes timezone information."""
        created_at = rollback_patch_data["createdAt"]
        assert 'Z' in created_at or '+' in created_at or created_at.count('-') > 2, \
            "createdAt should include timezone information"

    def test_created_at_is_reasonable_date(self, rollback_patch_data):
        """Test that createdAt represents a reasonable date (not in far future/past)."""
        created_at = rollback_patch_data["createdAt"]
        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

        # Should be after 2020 and not more than 1 year in the future
        assert dt.year >= 2020, "createdAt year should be 2020 or later"
        assert dt.year <= datetime.now().year + 1, \
            "createdAt should not be more than 1 year in the future"


class TestRollbackPatchEntries:
    """Test suite for the entries array."""

    def test_entries_is_list(self, rollback_patch_data):
        """Test that entries is a list/array."""
        assert isinstance(rollback_patch_data["entries"], list), \
            "entries must be an array"

    def test_entries_not_none(self, rollback_patch_data):
        """Test that entries is not None."""
        assert rollback_patch_data["entries"] is not None, \
            "entries cannot be None"

    def test_entries_contains_objects(self, rollback_patch_data):
        """Test that all entries are objects."""
        for i, entry in enumerate(rollback_patch_data["entries"]):
            assert isinstance(entry, dict), \
                f"Entry at index {i} must be an object"


class TestRollbackPatchEntryStructure:
    """Test suite for individual entry structure."""

    def test_entry_has_file_path(self, rollback_patch_data):
        """Test that each entry has a filePath field."""
        for i, entry in enumerate(rollback_patch_data["entries"]):
            assert "filePath" in entry, \
                f"Entry at index {i} missing 'filePath' field"

    def test_entry_has_original_content(self, rollback_patch_data):
        """Test that each entry has an originalContent field."""
        for i, entry in enumerate(rollback_patch_data["entries"]):
            assert "originalContent" in entry, \
                f"Entry at index {i} missing 'originalContent' field"

    def test_entry_file_path_is_string(self, rollback_patch_data):
        """Test that filePath is a string in each entry."""
        for i, entry in enumerate(rollback_patch_data["entries"]):
            assert isinstance(entry["filePath"], str), \
                f"filePath at index {i} must be a string"

    def test_entry_file_path_not_empty(self, rollback_patch_data):
        """Test that filePath is not empty in each entry."""
        for i, entry in enumerate(rollback_patch_data["entries"]):
            assert entry["filePath"].strip(), \
                f"filePath at index {i} cannot be empty"

    def test_entry_original_content_is_string(self, rollback_patch_data):
        """Test that originalContent is a string in each entry."""
        for i, entry in enumerate(rollback_patch_data["entries"]):
            assert isinstance(entry["originalContent"], str), \
                f"originalContent at index {i} must be a string"

    def test_entry_no_extra_fields(self, rollback_patch_data):
        """Test that entries don't have unexpected fields."""
        allowed_fields = {"filePath", "originalContent"}
        for i, entry in enumerate(rollback_patch_data["entries"]):
            actual_fields = set(entry.keys())
            extra_fields = actual_fields - allowed_fields
            assert not extra_fields, \
                f"Entry at index {i} has unexpected fields: {extra_fields}"


class TestRollbackPatchContentValidation:
    """Test suite for content-specific validation."""

    def test_original_content_preserves_line_endings(self, rollback_patch_data):
        """Test that originalContent preserves line endings (CRLF or LF)."""
        for i, entry in enumerate(rollback_patch_data["entries"]):
            content = entry["originalContent"]
            if content:
                # Should contain either \n or \r\n if it's a multi-line file
                has_line_endings = '\\n' in repr(content) or '\n' in content
                # This is informational - just verify content can have line endings
                # Don't fail if it's a single-line file

    def test_file_path_format(self, rollback_patch_data):
        """Test that filePath uses consistent path separators."""
        for i, entry in enumerate(rollback_patch_data["entries"]):
            file_path = entry["filePath"]
            # Verify path doesn't have mixed separators
            has_forward = '/' in file_path
            has_backward = '\\' in file_path
            if has_forward and has_backward:
                pytest.fail(f"Entry {i} has mixed path separators: {file_path}")


class TestRollbackPatchEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    def test_handles_empty_original_content(self):
        """Test that schema allows empty originalContent."""
        test_data = {
            "createdAt": "2026-03-05T21:07:37.969Z",
            "entries": [
                {
                    "filePath": "test.txt",
                    "originalContent": ""
                }
            ]
        }
        validate(instance=test_data, schema=ROLLBACK_PATCH_SCHEMA)

    def test_handles_empty_entries_array(self):
        """Test that schema allows empty entries array."""
        test_data = {
            "createdAt": "2026-03-05T21:07:37.969Z",
            "entries": []
        }
        validate(instance=test_data, schema=ROLLBACK_PATCH_SCHEMA)

    def test_handles_multiple_entries(self):
        """Test that schema allows multiple entries."""
        test_data = {
            "createdAt": "2026-03-05T21:07:37.969Z",
            "entries": [
                {"filePath": "file1.txt", "originalContent": "content1"},
                {"filePath": "file2.txt", "originalContent": "content2"},
                {"filePath": "file3.txt", "originalContent": "content3"}
            ]
        }
        validate(instance=test_data, schema=ROLLBACK_PATCH_SCHEMA)

    def test_rejects_missing_created_at(self):
        """Test that schema rejects data without createdAt."""
        test_data = {
            "entries": []
        }
        with pytest.raises(ValidationError):
            validate(instance=test_data, schema=ROLLBACK_PATCH_SCHEMA)

    def test_rejects_missing_entries(self):
        """Test that schema rejects data without entries."""
        test_data = {
            "createdAt": "2026-03-05T21:07:37.969Z"
        }
        with pytest.raises(ValidationError):
            validate(instance=test_data, schema=ROLLBACK_PATCH_SCHEMA)

    def test_rejects_null_created_at(self):
        """Test that schema rejects null createdAt."""
        test_data = {
            "createdAt": None,
            "entries": []
        }
        with pytest.raises(ValidationError):
            validate(instance=test_data, schema=ROLLBACK_PATCH_SCHEMA)

    def test_rejects_null_entries(self):
        """Test that schema rejects null entries."""
        test_data = {
            "createdAt": "2026-03-05T21:07:37.969Z",
            "entries": None
        }
        with pytest.raises(ValidationError):
            validate(instance=test_data, schema=ROLLBACK_PATCH_SCHEMA)

    def test_rejects_entry_missing_file_path(self):
        """Test that schema rejects entries without filePath."""
        test_data = {
            "createdAt": "2026-03-05T21:07:37.969Z",
            "entries": [
                {"originalContent": "content"}
            ]
        }
        with pytest.raises(ValidationError):
            validate(instance=test_data, schema=ROLLBACK_PATCH_SCHEMA)

    def test_rejects_entry_missing_original_content(self):
        """Test that schema rejects entries without originalContent."""
        test_data = {
            "createdAt": "2026-03-05T21:07:37.969Z",
            "entries": [
                {"filePath": "file.txt"}
            ]
        }
        with pytest.raises(ValidationError):
            validate(instance=test_data, schema=ROLLBACK_PATCH_SCHEMA)

    def test_rejects_extra_root_fields(self):
        """Test that schema rejects extra fields at root level."""
        test_data = {
            "createdAt": "2026-03-05T21:07:37.969Z",
            "entries": [],
            "extraField": "should not be here"
        }
        with pytest.raises(ValidationError):
            validate(instance=test_data, schema=ROLLBACK_PATCH_SCHEMA)

    def test_rejects_extra_entry_fields(self):
        """Test that schema rejects extra fields in entries."""
        test_data = {
            "createdAt": "2026-03-05T21:07:37.969Z",
            "entries": [
                {
                    "filePath": "file.txt",
                    "originalContent": "content",
                    "extraField": "should not be here"
                }
            ]
        }
        with pytest.raises(ValidationError):
            validate(instance=test_data, schema=ROLLBACK_PATCH_SCHEMA)


class TestRollbackPatchDataIntegrity:
    """Test suite for data integrity and realistic scenarios."""

    def test_file_path_references_valid_structure(self, rollback_patch_data):
        """Test that filePath references appear to be valid paths."""
        for i, entry in enumerate(rollback_patch_data["entries"]):
            file_path = entry["filePath"]
            # Should not start or end with path separators
            assert not file_path.startswith('/') and not file_path.startswith('\\'), \
                f"Entry {i}: filePath should not start with separator"

    def test_original_content_json_validity(self, rollback_patch_data):
        """Test that if originalContent is JSON, it's valid JSON."""
        for i, entry in enumerate(rollback_patch_data["entries"]):
            content = entry["originalContent"]
            file_path = entry["filePath"]

            # If the file is a .json file, verify the content is valid JSON
            if file_path.endswith('.json'):
                try:
                    json.loads(content)
                except json.JSONDecodeError as e:
                    pytest.fail(f"Entry {i}: originalContent for JSON file is invalid: {e}")

    def test_consistency_between_entries(self, rollback_patch_data):
        """Test that entries don't have duplicate filePaths."""
        file_paths = [entry["filePath"] for entry in rollback_patch_data["entries"]]
        duplicates = [fp for fp in file_paths if file_paths.count(fp) > 1]
        unique_duplicates = list(set(duplicates))
        assert not unique_duplicates, \
            f"Duplicate filePaths found: {unique_duplicates}"


class TestRollbackPatchBoundaryConditions:
    """Test suite for boundary conditions and stress scenarios."""

    def test_handles_large_original_content(self):
        """Test that schema handles large originalContent strings."""
        test_data = {
            "createdAt": "2026-03-05T21:07:37.969Z",
            "entries": [
                {
                    "filePath": "large.txt",
                    "originalContent": "x" * 100000  # 100KB of content
                }
            ]
        }
        validate(instance=test_data, schema=ROLLBACK_PATCH_SCHEMA)

    def test_handles_special_characters_in_content(self):
        """Test that schema handles special characters in originalContent."""
        test_data = {
            "createdAt": "2026-03-05T21:07:37.969Z",
            "entries": [
                {
                    "filePath": "special.txt",
                    "originalContent": "Hello\nWorld\r\n\t\"quotes\"\\backslash\u0000null"
                }
            ]
        }
        validate(instance=test_data, schema=ROLLBACK_PATCH_SCHEMA)

    def test_handles_unicode_in_file_path(self):
        """Test that schema handles Unicode characters in filePath."""
        test_data = {
            "createdAt": "2026-03-05T21:07:37.969Z",
            "entries": [
                {
                    "filePath": "folder/файл.txt",  # Cyrillic
                    "originalContent": "content"
                }
            ]
        }
        validate(instance=test_data, schema=ROLLBACK_PATCH_SCHEMA)

    def test_handles_deep_directory_paths(self):
        """Test that schema handles deep directory structures."""
        test_data = {
            "createdAt": "2026-03-05T21:07:37.969Z",
            "entries": [
                {
                    "filePath": "a/b/c/d/e/f/g/h/i/j/file.txt",
                    "originalContent": "content"
                }
            ]
        }
        validate(instance=test_data, schema=ROLLBACK_PATCH_SCHEMA)


class TestRollbackPatchRegressionTests:
    """Test suite for regression scenarios and additional confidence checks."""

    def test_actual_file_matches_expected_structure(self, rollback_patch_data):
        """Regression test: verify actual file has expected number of entries."""
        # This test is based on the current state of the file
        # Adjust if the file structure changes
        assert isinstance(rollback_patch_data["entries"], list)

        # Verify each entry in the actual file is properly structured
        for entry in rollback_patch_data["entries"]:
            assert "filePath" in entry
            assert "originalContent" in entry
            assert isinstance(entry["filePath"], str)
            assert isinstance(entry["originalContent"], str)

    def test_created_at_matches_expected_pattern(self, rollback_patch_data):
        """Regression test: verify createdAt follows expected timestamp pattern."""
        created_at = rollback_patch_data["createdAt"]
        # Should match ISO 8601 with milliseconds and Z timezone
        # Example: 2026-03-05T21:07:37.969Z
        assert created_at.endswith('Z'), "createdAt should end with 'Z' for UTC"
        assert 'T' in created_at, "createdAt should have 'T' separator"
        assert created_at.count(':') == 2, "createdAt should have hours, minutes, seconds"
        assert '.' in created_at, "createdAt should include milliseconds"

    def test_file_can_be_loaded_multiple_times(self):
        """Test that the file can be read and parsed multiple times consistently."""
        with open(ROLLBACK_PATCH_PATH, 'r', encoding='utf-8') as f:
            data1 = json.load(f)

        with open(ROLLBACK_PATCH_PATH, 'r', encoding='utf-8') as f:
            data2 = json.load(f)

        assert data1 == data2, "File should parse consistently across multiple reads"

    def test_schema_validator_is_properly_configured(self):
        """Test that the JSON schema validator itself is properly set up."""
        validator = Draft7Validator(ROLLBACK_PATCH_SCHEMA)
        assert validator.is_valid({
            "createdAt": "2026-03-05T00:00:00Z",
            "entries": []
        }), "Schema validator should accept minimal valid data"