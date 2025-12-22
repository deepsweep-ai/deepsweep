"""
Core validation engine for DeepSweep.

Validates paths and content against detection patterns.
"""

from pathlib import Path

from deepsweep.constants import SCANNABLE_FILES
from deepsweep.exceptions import FileAccessError, ValidationError
from deepsweep.models import FileResult, Finding, ValidationResult
from deepsweep.patterns import Pattern, get_all_patterns, get_pattern_count


def validate_path(path: Path | str) -> ValidationResult:
    """
    Validate all AI assistant configurations in a path.

    Args:
        path: Directory or file path to validate

    Returns:
        ValidationResult with all findings and score

    Raises:
        ValidationError: If path cannot be accessed
    """
    path = Path(path)

    if not path.exists():
        raise ValidationError(f"Path does not exist: {path}")

    patterns = get_all_patterns()
    file_results: list[FileResult] = []

    if path.is_file():
        # Single file validation
        result = _validate_file(path, patterns)
        file_results.append(result)
    else:
        # Directory validation
        for scannable in SCANNABLE_FILES:
            # Check both direct path and nested path
            candidates = [
                path / scannable,
                path / scannable.lstrip("."),
            ]

            for candidate in candidates:
                if candidate.exists() and candidate.is_file():
                    result = _validate_file(candidate, patterns)
                    file_results.append(result)
                    break

        # Also check subdirectories for hidden files
        for item in path.rglob("*"):
            if item.is_file():
                rel_path = str(item.relative_to(path))
                if any(rel_path.endswith(s) or s in rel_path for s in SCANNABLE_FILES):
                    # Avoid duplicates
                    if not any(fr.path == str(item) for fr in file_results):
                        result = _validate_file(item, patterns)
                        file_results.append(result)

    return ValidationResult(
        files=tuple(file_results),
        pattern_count=get_pattern_count(),
    )


def validate_content(content: str, file_path: str) -> ValidationResult:
    """
    Validate content string against patterns.

    Useful for testing or validating in-memory content.

    Args:
        content: Content to validate
        file_path: Virtual file path (for pattern matching)

    Returns:
        ValidationResult with findings
    """
    patterns = get_all_patterns()
    findings = _match_patterns(content, file_path, patterns)

    file_result = FileResult(
        path=file_path,
        findings=tuple(findings),
    )

    return ValidationResult(
        files=(file_result,),
        pattern_count=get_pattern_count(),
    )


def _validate_file(path: Path, patterns: tuple[Pattern, ...]) -> FileResult:
    """
    Validate a single file against patterns.

    Args:
        path: Path to file
        patterns: Patterns to match against

    Returns:
        FileResult with findings
    """
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except PermissionError:
        return FileResult(
            path=str(path),
            skipped=True,
            skip_reason="Permission denied",
        )
    except Exception as e:
        return FileResult(
            path=str(path),
            skipped=True,
            skip_reason=f"Read error: {e}",
        )

    findings = _match_patterns(content, str(path), patterns)

    return FileResult(
        path=str(path),
        findings=tuple(findings),
    )


def _match_patterns(
    content: str,
    file_path: str,
    patterns: tuple[Pattern, ...],
) -> list[Finding]:
    """
    Match content against all patterns.

    Args:
        content: Content to check
        file_path: File path for pattern matching
        patterns: Patterns to apply

    Returns:
        List of findings
    """
    findings: list[Finding] = []

    for pattern in patterns:
        matches = pattern.matches(content, file_path)
        for line_num, matched_text in matches:
            finding = pattern.to_finding(file_path, line_num, matched_text)
            findings.append(finding)

    return findings
