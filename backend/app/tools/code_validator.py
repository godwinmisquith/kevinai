"""Code Validator Tool for validating generated code."""

import asyncio
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.tools.base import BaseTool


class ValidationLevel(Enum):
    """Validation severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class Language(Enum):
    """Supported programming languages."""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    RUBY = "ruby"
    PHP = "php"
    UNKNOWN = "unknown"


@dataclass
class ValidationIssue:
    """A single validation issue."""

    level: ValidationLevel
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None
    rule: Optional[str] = None
    source: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level.value,
            "message": self.message,
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "rule": self.rule,
            "source": self.source,
        }


@dataclass
class ValidationResult:
    """Result of a validation run."""

    success: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    summary: str = ""
    command_run: str = ""
    raw_output: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "issues": [i.to_dict() for i in self.issues],
            "summary": self.summary,
            "command_run": self.command_run,
            "error_count": len([i for i in self.issues if i.level == ValidationLevel.ERROR]),
            "warning_count": len([i for i in self.issues if i.level == ValidationLevel.WARNING]),
        }


@dataclass
class ProjectConfig:
    """Detected project configuration."""

    root_path: str
    language: Language
    has_package_json: bool = False
    has_pyproject_toml: bool = False
    has_cargo_toml: bool = False
    has_go_mod: bool = False
    has_makefile: bool = False
    lint_command: Optional[str] = None
    test_command: Optional[str] = None
    build_command: Optional[str] = None
    type_check_command: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "root_path": self.root_path,
            "language": self.language.value,
            "has_package_json": self.has_package_json,
            "has_pyproject_toml": self.has_pyproject_toml,
            "has_cargo_toml": self.has_cargo_toml,
            "has_go_mod": self.has_go_mod,
            "has_makefile": self.has_makefile,
            "lint_command": self.lint_command,
            "test_command": self.test_command,
            "build_command": self.build_command,
            "type_check_command": self.type_check_command,
        }


class CodeValidatorTool(BaseTool):
    """Tool for validating code through linting, type checking, and testing."""

    name = "code_validator"
    description = "Validate code through syntax checking, linting, type checking, and testing"

    # File extension to language mapping
    EXTENSION_MAP = {
        ".py": Language.PYTHON,
        ".js": Language.JAVASCRIPT,
        ".jsx": Language.JAVASCRIPT,
        ".ts": Language.TYPESCRIPT,
        ".tsx": Language.TYPESCRIPT,
        ".go": Language.GO,
        ".rs": Language.RUST,
        ".java": Language.JAVA,
        ".cpp": Language.CPP,
        ".cc": Language.CPP,
        ".c": Language.C,
        ".h": Language.C,
        ".rb": Language.RUBY,
        ".php": Language.PHP,
    }

    async def execute(
        self,
        operation: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute a code validation operation."""
        operations = {
            "detect_project": self._detect_project,
            "lint": self._run_lint,
            "type_check": self._run_type_check,
            "test": self._run_tests,
            "build": self._run_build,
            "validate_file": self._validate_file,
            "validate_all": self._validate_all,
            "syntax_check": self._syntax_check,
        }

        if operation not in operations:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}. Available: {list(operations.keys())}",
            }

        try:
            return await operations[operation](**kwargs)
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _run_command(
        self, command: str, cwd: str, timeout: int = 60
    ) -> tuple[int, str, str]:
        """Run a shell command and return exit code, stdout, stderr."""
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )
            return (
                process.returncode or 0,
                stdout.decode("utf-8", errors="replace"),
                stderr.decode("utf-8", errors="replace"),
            )
        except asyncio.TimeoutError:
            return -1, "", "Command timed out"
        except Exception as e:
            return -1, "", str(e)

    async def _detect_project(self, path: str) -> Dict[str, Any]:
        """Detect project configuration from a directory."""
        root = Path(path)
        if not root.exists():
            return {"success": False, "error": f"Path does not exist: {path}"}

        config = ProjectConfig(root_path=str(root), language=Language.UNKNOWN)

        # Check for config files
        config.has_package_json = (root / "package.json").exists()
        config.has_pyproject_toml = (root / "pyproject.toml").exists()
        config.has_cargo_toml = (root / "Cargo.toml").exists()
        config.has_go_mod = (root / "go.mod").exists()
        config.has_makefile = (root / "Makefile").exists()

        # Detect language and commands
        if config.has_package_json:
            config.language = Language.TYPESCRIPT  # Assume TS for npm projects
            await self._detect_npm_scripts(root, config)
        elif config.has_pyproject_toml:
            config.language = Language.PYTHON
            await self._detect_python_scripts(root, config)
        elif config.has_cargo_toml:
            config.language = Language.RUST
            config.lint_command = "cargo clippy"
            config.test_command = "cargo test"
            config.build_command = "cargo build"
        elif config.has_go_mod:
            config.language = Language.GO
            config.lint_command = "golangci-lint run"
            config.test_command = "go test ./..."
            config.build_command = "go build ./..."

        return {"success": True, "config": config.to_dict()}

    async def _detect_npm_scripts(self, root: Path, config: ProjectConfig) -> None:
        """Detect npm scripts from package.json."""
        try:
            package_json = root / "package.json"
            with open(package_json) as f:
                pkg = json.load(f)

            scripts = pkg.get("scripts", {})

            # Detect lint command
            for cmd in ["lint", "eslint", "lint:check"]:
                if cmd in scripts:
                    config.lint_command = f"npm run {cmd}"
                    break

            # Detect type check command
            for cmd in ["typecheck", "type-check", "tsc", "types"]:
                if cmd in scripts:
                    config.type_check_command = f"npm run {cmd}"
                    break

            # Detect test command
            for cmd in ["test", "test:unit", "jest", "vitest"]:
                if cmd in scripts:
                    config.test_command = f"npm run {cmd}"
                    break

            # Detect build command
            for cmd in ["build", "compile", "dist"]:
                if cmd in scripts:
                    config.build_command = f"npm run {cmd}"
                    break

            # Check if TypeScript
            if (root / "tsconfig.json").exists():
                config.language = Language.TYPESCRIPT
                if not config.type_check_command:
                    config.type_check_command = "npx tsc --noEmit"

        except Exception:
            pass

    async def _detect_python_scripts(self, root: Path, config: ProjectConfig) -> None:
        """Detect Python project scripts."""
        try:
            pyproject = root / "pyproject.toml"
            content = pyproject.read_text()

            # Check for poetry
            if "[tool.poetry]" in content:
                config.lint_command = "poetry run ruff check ."
                config.type_check_command = "poetry run mypy ."
                config.test_command = "poetry run pytest"
            else:
                # Standard pip project
                config.lint_command = "ruff check ."
                config.type_check_command = "mypy ."
                config.test_command = "pytest"

            # Check for specific tools in pyproject.toml
            if "[tool.ruff]" in content:
                pass  # Already using ruff
            elif "[tool.flake8]" in content or (root / ".flake8").exists():
                config.lint_command = config.lint_command.replace("ruff check", "flake8")

            if "[tool.mypy]" in content or (root / "mypy.ini").exists():
                pass  # Already using mypy

        except Exception:
            # Fallback defaults
            config.lint_command = "ruff check ."
            config.test_command = "pytest"

    async def _run_lint(
        self, path: str, fix: bool = False, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run linting on a project or file."""
        root = Path(path)

        # Detect project if config not provided
        if not config:
            detect_result = await self._detect_project(str(root))
            if not detect_result.get("success"):
                return detect_result
            config = detect_result.get("config", {})

        lint_cmd = config.get("lint_command")
        if not lint_cmd:
            # Try to determine from file extension
            if root.is_file():
                lang = self._detect_language(str(root))
                lint_cmd = self._get_default_lint_command(lang, str(root))
            else:
                return {"success": False, "error": "No lint command detected"}

        if fix and "ruff" in lint_cmd:
            lint_cmd = lint_cmd.replace("ruff check", "ruff check --fix")
        elif fix and "eslint" in lint_cmd:
            lint_cmd += " --fix"

        cwd = str(root) if root.is_dir() else str(root.parent)
        exit_code, stdout, stderr = await self._run_command(lint_cmd, cwd)

        issues = self._parse_lint_output(stdout + stderr, config.get("language", "unknown"))

        result = ValidationResult(
            success=exit_code == 0,
            issues=issues,
            command_run=lint_cmd,
            raw_output=stdout + stderr,
            summary=f"Lint {'passed' if exit_code == 0 else 'failed'} with {len(issues)} issues",
        )

        return result.to_dict()

    async def _run_type_check(
        self, path: str, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run type checking on a project."""
        root = Path(path)

        if not config:
            detect_result = await self._detect_project(str(root))
            if not detect_result.get("success"):
                return detect_result
            config = detect_result.get("config", {})

        type_cmd = config.get("type_check_command")
        if not type_cmd:
            lang = Language(config.get("language", "unknown"))
            if lang == Language.PYTHON:
                type_cmd = "mypy ."
            elif lang == Language.TYPESCRIPT:
                type_cmd = "npx tsc --noEmit"
            else:
                return {"success": True, "message": "No type checker available for this language"}

        cwd = str(root) if root.is_dir() else str(root.parent)
        exit_code, stdout, stderr = await self._run_command(type_cmd, cwd)

        issues = self._parse_type_check_output(stdout + stderr, config.get("language", "unknown"))

        result = ValidationResult(
            success=exit_code == 0,
            issues=issues,
            command_run=type_cmd,
            raw_output=stdout + stderr,
            summary=f"Type check {'passed' if exit_code == 0 else 'failed'} with {len(issues)} issues",
        )

        return result.to_dict()

    async def _run_tests(
        self,
        path: str,
        test_pattern: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run tests for a project."""
        root = Path(path)

        if not config:
            detect_result = await self._detect_project(str(root))
            if not detect_result.get("success"):
                return detect_result
            config = detect_result.get("config", {})

        test_cmd = config.get("test_command")
        if not test_cmd:
            return {"success": False, "error": "No test command detected"}

        if test_pattern:
            test_cmd += f" -k '{test_pattern}'"

        cwd = str(root) if root.is_dir() else str(root.parent)
        exit_code, stdout, stderr = await self._run_command(test_cmd, cwd, timeout=300)

        result = ValidationResult(
            success=exit_code == 0,
            command_run=test_cmd,
            raw_output=stdout + stderr,
            summary=f"Tests {'passed' if exit_code == 0 else 'failed'}",
        )

        return result.to_dict()

    async def _run_build(
        self, path: str, config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run build for a project."""
        root = Path(path)

        if not config:
            detect_result = await self._detect_project(str(root))
            if not detect_result.get("success"):
                return detect_result
            config = detect_result.get("config", {})

        build_cmd = config.get("build_command")
        if not build_cmd:
            return {"success": True, "message": "No build command detected"}

        cwd = str(root) if root.is_dir() else str(root.parent)
        exit_code, stdout, stderr = await self._run_command(build_cmd, cwd, timeout=300)

        result = ValidationResult(
            success=exit_code == 0,
            command_run=build_cmd,
            raw_output=stdout + stderr,
            summary=f"Build {'succeeded' if exit_code == 0 else 'failed'}",
        )

        return result.to_dict()

    async def _validate_file(self, file_path: str) -> Dict[str, Any]:
        """Validate a single file with syntax check and linting."""
        path = Path(file_path)
        if not path.exists():
            return {"success": False, "error": f"File does not exist: {file_path}"}

        lang = self._detect_language(file_path)
        results = []

        # Syntax check
        syntax_result = await self._syntax_check(file_path=file_path)
        results.append({"type": "syntax", "result": syntax_result})

        # Lint
        lint_cmd = self._get_default_lint_command(lang, file_path)
        if lint_cmd:
            exit_code, stdout, stderr = await self._run_command(
                lint_cmd, str(path.parent)
            )
            lint_result = ValidationResult(
                success=exit_code == 0,
                issues=self._parse_lint_output(stdout + stderr, lang.value),
                command_run=lint_cmd,
                raw_output=stdout + stderr,
            )
            results.append({"type": "lint", "result": lint_result.to_dict()})

        all_success = all(r["result"].get("success", False) for r in results)

        return {
            "success": all_success,
            "file": file_path,
            "language": lang.value,
            "validations": results,
        }

    async def _validate_all(
        self, path: str, skip_tests: bool = False
    ) -> Dict[str, Any]:
        """Run all validations on a project."""
        results = {}

        # Detect project
        detect_result = await self._detect_project(path)
        if not detect_result.get("success"):
            return detect_result

        config = detect_result.get("config", {})
        results["project"] = config

        # Run lint
        lint_result = await self._run_lint(path, config=config)
        results["lint"] = lint_result

        # Run type check
        type_result = await self._run_type_check(path, config=config)
        results["type_check"] = type_result

        # Run build
        build_result = await self._run_build(path, config=config)
        results["build"] = build_result

        # Run tests (optional)
        if not skip_tests:
            test_result = await self._run_tests(path, config=config)
            results["tests"] = test_result

        # Overall success
        all_success = all(
            results.get(k, {}).get("success", True)
            for k in ["lint", "type_check", "build"]
        )
        if not skip_tests:
            all_success = all_success and results.get("tests", {}).get("success", True)

        return {
            "success": all_success,
            "results": results,
            "summary": self._generate_summary(results),
        }

    async def _syntax_check(self, file_path: str) -> Dict[str, Any]:
        """Check syntax of a file."""
        path = Path(file_path)
        if not path.exists():
            return {"success": False, "error": f"File does not exist: {file_path}"}

        lang = self._detect_language(file_path)
        cmd = None

        if lang == Language.PYTHON:
            cmd = f"python -m py_compile {file_path}"
        elif lang in (Language.JAVASCRIPT, Language.TYPESCRIPT):
            # Use node to check syntax
            if lang == Language.TYPESCRIPT:
                cmd = f"npx tsc --noEmit {file_path}"
            else:
                cmd = f"node --check {file_path}"
        elif lang == Language.GO:
            cmd = f"go build -n {file_path}"
        elif lang == Language.RUST:
            cmd = f"rustfmt --check {file_path}"

        if not cmd:
            return {"success": True, "message": f"No syntax checker for {lang.value}"}

        exit_code, stdout, stderr = await self._run_command(cmd, str(path.parent))

        return {
            "success": exit_code == 0,
            "command": cmd,
            "output": stdout + stderr,
            "language": lang.value,
        }

    def _detect_language(self, file_path: str) -> Language:
        """Detect language from file extension."""
        ext = Path(file_path).suffix.lower()
        return self.EXTENSION_MAP.get(ext, Language.UNKNOWN)

    def _get_default_lint_command(self, lang: Language, file_path: str) -> Optional[str]:
        """Get default lint command for a language."""
        commands = {
            Language.PYTHON: f"ruff check {file_path}",
            Language.JAVASCRIPT: f"npx eslint {file_path}",
            Language.TYPESCRIPT: f"npx eslint {file_path}",
            Language.GO: f"golangci-lint run {file_path}",
            Language.RUST: "cargo clippy",
        }
        return commands.get(lang)

    def _parse_lint_output(self, output: str, language: str) -> List[ValidationIssue]:
        """Parse lint output into ValidationIssues."""
        issues = []

        # Python (ruff/flake8) format: file.py:10:5: E501 line too long
        python_pattern = r"([^:]+):(\d+):(\d+):\s*(\w+)\s+(.+)"

        # ESLint format: /path/file.js:10:5: error message (rule-name)
        eslint_pattern = r"([^:]+):(\d+):(\d+):\s*(error|warning)\s+(.+?)\s+(\S+)$"

        for line in output.split("\n"):
            line = line.strip()
            if not line:
                continue

            # Try Python pattern
            match = re.match(python_pattern, line)
            if match:
                file_path, line_num, col, rule, message = match.groups()
                level = ValidationLevel.ERROR if rule.startswith("E") else ValidationLevel.WARNING
                issues.append(
                    ValidationIssue(
                        level=level,
                        message=message,
                        file=file_path,
                        line=int(line_num),
                        column=int(col),
                        rule=rule,
                        source="lint",
                    )
                )
                continue

            # Try ESLint pattern
            match = re.match(eslint_pattern, line)
            if match:
                file_path, line_num, col, level_str, message, rule = match.groups()
                level = ValidationLevel.ERROR if level_str == "error" else ValidationLevel.WARNING
                issues.append(
                    ValidationIssue(
                        level=level,
                        message=message,
                        file=file_path,
                        line=int(line_num),
                        column=int(col),
                        rule=rule,
                        source="lint",
                    )
                )

        return issues

    def _parse_type_check_output(self, output: str, language: str) -> List[ValidationIssue]:
        """Parse type check output into ValidationIssues."""
        issues = []

        # mypy format: file.py:10: error: Message [error-code]
        mypy_pattern = r"([^:]+):(\d+):\s*(error|warning|note):\s*(.+?)(?:\s+\[(\S+)\])?$"

        # TypeScript format: file.ts(10,5): error TS2322: Message
        ts_pattern = r"([^(]+)\((\d+),(\d+)\):\s*(error|warning)\s+(\w+):\s*(.+)"

        for line in output.split("\n"):
            line = line.strip()
            if not line:
                continue

            # Try mypy pattern
            match = re.match(mypy_pattern, line)
            if match:
                file_path, line_num, level_str, message, rule = match.groups()
                if level_str == "note":
                    continue
                level = ValidationLevel.ERROR if level_str == "error" else ValidationLevel.WARNING
                issues.append(
                    ValidationIssue(
                        level=level,
                        message=message,
                        file=file_path,
                        line=int(line_num),
                        rule=rule,
                        source="type_check",
                    )
                )
                continue

            # Try TypeScript pattern
            match = re.match(ts_pattern, line)
            if match:
                file_path, line_num, col, level_str, code, message = match.groups()
                level = ValidationLevel.ERROR if level_str == "error" else ValidationLevel.WARNING
                issues.append(
                    ValidationIssue(
                        level=level,
                        message=message,
                        file=file_path,
                        line=int(line_num),
                        column=int(col),
                        rule=code,
                        source="type_check",
                    )
                )

        return issues

    def _generate_summary(self, results: Dict[str, Any]) -> str:
        """Generate a summary of all validation results."""
        parts = []

        lint = results.get("lint", {})
        if lint:
            errors = lint.get("error_count", 0)
            warnings = lint.get("warning_count", 0)
            status = "passed" if lint.get("success") else "failed"
            parts.append(f"Lint: {status} ({errors} errors, {warnings} warnings)")

        type_check = results.get("type_check", {})
        if type_check and type_check.get("command_run"):
            errors = type_check.get("error_count", 0)
            status = "passed" if type_check.get("success") else "failed"
            parts.append(f"Type check: {status} ({errors} errors)")

        build = results.get("build", {})
        if build and build.get("command_run"):
            status = "succeeded" if build.get("success") else "failed"
            parts.append(f"Build: {status}")

        tests = results.get("tests", {})
        if tests and tests.get("command_run"):
            status = "passed" if tests.get("success") else "failed"
            parts.append(f"Tests: {status}")

        return " | ".join(parts) if parts else "No validations run"
