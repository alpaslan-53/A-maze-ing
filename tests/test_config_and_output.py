"""Unit tests for config parsing, hex output writing, and CLI handling."""

from pathlib import Path
import sys

import pytest

import a_maze_ing
from config_parser import ConfigError, load_config
import maze_display
from maze_writer import build_text, write_maze


def _write_cfg(tmp_path: Path, content: str) -> str:
    """Write a temporary config file and return its string path."""
    cfg_file = tmp_path / "test_config.txt"
    cfg_file.write_text(content, encoding="utf-8")
    return str(cfg_file)


def test_load_valid_config_with_seed(tmp_path: Path) -> None:
    """Valid config with comments and SEED parses into MazeConfig."""
    path = _write_cfg(
        tmp_path,
        "# Comment line\n"
        "WIDTH=20\n"
        "HEIGHT=15\n"
        "ENTRY=0,0\n"
        "EXIT=19,14\n"
        "OUTPUT_FILE=maze.txt\n"
        "PERFECT=True\n"
        "SEED=42\n",
    )
    cfg = load_config(path)
    assert cfg.width == 20
    assert cfg.height == 15
    assert cfg.entry == (0, 0)
    assert cfg.exit == (19, 14)
    assert cfg.output_file == "maze.txt"
    assert cfg.perfect is True
    assert cfg.seed == 42


def test_load_valid_config_without_seed(tmp_path: Path) -> None:
    """Valid config without SEED sets seed to None."""
    path = _write_cfg(
        tmp_path,
        "WIDTH=10\nHEIGHT=10\nENTRY=0,0\nEXIT=9,9\n"
        "OUTPUT_FILE=out.txt\nPERFECT=False\n",
    )
    cfg = load_config(path)
    assert cfg.perfect is False
    assert cfg.seed is None


def test_missing_file_raises_config_error(tmp_path: Path) -> None:
    """Non-existent config file raises ConfigError."""
    with pytest.raises(ConfigError, match="Cannot read config file"):
        load_config(str(tmp_path / "missing.txt"))


def test_missing_equals_raises_config_error(tmp_path: Path) -> None:
    """Line without '=' raises ConfigError."""
    path = _write_cfg(tmp_path, "WIDTH 20\n")
    with pytest.raises(ConfigError, match="missing '='"):
        load_config(path)


def test_duplicate_key_raises_config_error(tmp_path: Path) -> None:
    """Duplicate keys raise ConfigError."""
    path = _write_cfg(tmp_path, "WIDTH=10\nWIDTH=20\n")
    with pytest.raises(ConfigError, match="duplicate key"):
        load_config(path)


def test_missing_required_key_raises_config_error(tmp_path: Path) -> None:
    """Missing required key raises ConfigError."""
    path = _write_cfg(
        tmp_path,
        "WIDTH=10\nHEIGHT=10\nENTRY=0,0\nEXIT=9,9\nOUTPUT_FILE=a.txt\n",
    )
    with pytest.raises(ConfigError, match="Missing required key"):
        load_config(path)


@pytest.mark.parametrize(
    "bad_val",
    ["-5", "abc", "10.5", "1_0"],
)
def test_invalid_integer_raises_config_error(
    tmp_path: Path, bad_val: str
) -> None:
    """Non-integer or negative dimensions raise ConfigError."""
    path = _write_cfg(
        tmp_path,
        f"WIDTH={bad_val}\nHEIGHT=10\nENTRY=0,0\nEXIT=9,9\n"
        "OUTPUT_FILE=a.txt\nPERFECT=True\n",
    )
    with pytest.raises(ConfigError):
        load_config(path)


def test_invalid_bool_raises_config_error(tmp_path: Path) -> None:
    """Invalid boolean string raises ConfigError."""
    path = _write_cfg(
        tmp_path,
        "WIDTH=10\nHEIGHT=10\nENTRY=0,0\nEXIT=9,9\n"
        "OUTPUT_FILE=a.txt\nPERFECT=yes\n",
    )
    with pytest.raises(ConfigError, match="True' or 'False'"):
        load_config(path)


def test_out_of_bounds_entry_raises_config_error(tmp_path: Path) -> None:
    """Entry outside maze bounds raises ConfigError."""
    path = _write_cfg(
        tmp_path,
        "WIDTH=10\nHEIGHT=10\nENTRY=10,0\nEXIT=9,9\n"
        "OUTPUT_FILE=a.txt\nPERFECT=True\n",
    )
    with pytest.raises(ConfigError, match="outside the maze"):
        load_config(path)


def test_identical_entry_exit_raises_config_error(tmp_path: Path) -> None:
    """Identical ENTRY and EXIT raises ConfigError."""
    path = _write_cfg(
        tmp_path,
        "WIDTH=10\nHEIGHT=10\nENTRY=2,2\nEXIT=2,2\n"
        "OUTPUT_FILE=a.txt\nPERFECT=True\n",
    )
    with pytest.raises(ConfigError, match="cannot be identical"):
        load_config(path)


def test_maze_writer_hex_and_lf_format(tmp_path: Path) -> None:
    """Output file matches PDF hex format and uses pure LF newlines."""
    class MockMaze:
        grid = [[11, 5, 5, 3], [14, 12, 5, 6]]
        entry = (0, 0)
        exit = (3, 1)
        solution = "EEES"

    maze = MockMaze()
    text = build_text(maze)
    assert text == "B553\nEC56\n\n0,0\n3,1\nEEES\n"

    out_path = tmp_path / "maze_out.txt"
    write_maze(maze, str(out_path))
    raw_bytes = out_path.read_bytes()
    assert b"\r\n" not in raw_bytes
    assert raw_bytes.decode("utf-8") == text


def test_small_maze_warning_printed_to_stderr(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Small maze without 42 pattern prints a warning to stderr."""
    class SmallMockMaze:
        width = 4
        height = 3
        grid = [[15] * 4 for _ in range(3)]
        entry = (0, 0)
        exit = (3, 2)
        solution = ""
        solution_cells: list[tuple[int, int]] = []
        pattern_cells: set[tuple[int, int]] = set()
        pattern_drawn = False
        seed = 1
        perfect = True

    maze_display.show(SmallMockMaze(), False, 255, 244)
    captured = capsys.readouterr()
    assert "too small" in captured.err


def test_cli_missing_args_returns_one(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Running main() without config argument returns 1 cleanly."""
    monkeypatch.setattr(sys, "argv", ["a_maze_ing.py"])
    assert a_maze_ing.main() == 1
    assert "Usage:" in capsys.readouterr().err


def test_cli_missing_config_file_returns_one(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Running main() with missing config file catches ConfigError."""
    monkeypatch.setattr(
        sys, "argv", ["a_maze_ing.py", str(tmp_path / "nope.txt")]
    )
    assert a_maze_ing.main() == 1
    assert "Error:" in capsys.readouterr().err


def test_cli_value_error_caught_cleanly(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """ValueError from generator (e.g. entry in 42) is caught cleanly."""
    path = _write_cfg(
        tmp_path,
        "WIDTH=15\nHEIGHT=11\nENTRY=0,0\nEXIT=14,10\n"
        "OUTPUT_FILE=a.txt\nPERFECT=True\n",
    )

    def fail_build(*_args: object, **_kwargs: object) -> object:
        raise ValueError("Entry cannot be inside the 42 pattern")

    monkeypatch.setattr(a_maze_ing, "build_maze", fail_build)
    monkeypatch.setattr(sys, "argv", ["a_maze_ing.py", path])
    assert a_maze_ing.main() == 1
    assert "42 pattern" in capsys.readouterr().err
