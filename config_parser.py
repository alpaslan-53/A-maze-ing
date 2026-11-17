"""Configuration parser and validator for A-Maze-ing."""

from dataclasses import dataclass


class ConfigError(ValueError):
    """Raised when the configuration file is invalid or missing keys."""

    pass


@dataclass(frozen=True)
class MazeConfig:
    """Holds validated configuration values for maze generation."""

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None


def read_pairs(path: str) -> dict[str, str]:
    """Read raw KEY=VALUE pairs from a configuration file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as err:
        raise ConfigError(f"Cannot read config file '{path}': {err}")

    pairs: dict[str, str] = {}
    for line_no, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ConfigError(f"Line {line_no}: missing '=' in '{line}'")
        key, val = line.split("=", 1)
        key, val = key.strip(), val.strip()
        if not key or not val:
            raise ConfigError(
                f"Line {line_no}: empty key or value in '{line}'"
            )
        if key in pairs:
            raise ConfigError(f"Line {line_no}: duplicate key '{key}'")
        pairs[key] = val
    return pairs


def to_int(name: str, value: str) -> int:
    """Convert a string value to an integer, rejecting invalid formats."""
    if not value.isascii() or not value.isdigit():
        raise ConfigError(
            f"'{name}' must be a non-negative integer, got '{value}'"
        )
    return int(value)


def parse_coord(name: str, value: str) -> tuple[int, int]:
    """Parse a coordinate string in 'x,y' format."""
    parts = value.split(",")
    if len(parts) != 2:
        raise ConfigError(
            f"'{name}' must be in 'x,y' format, got '{value}'"
        )
    x = to_int(f"{name}.x", parts[0].strip())
    y = to_int(f"{name}.y", parts[1].strip())
    return (x, y)


def parse_bool(name: str, value: str) -> bool:
    """Parse a boolean string ('True' or 'False')."""
    if value == "True":
        return True
    if value == "False":
        return False
    raise ConfigError(
        f"'{name}' must be 'True' or 'False', got '{value}'"
    )


REQUIRED_KEYS = {
    "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
}


def load_config(path: str) -> MazeConfig:
    """Load, validate, and return the maze configuration from a file."""
    pairs = read_pairs(path)

    missing = REQUIRED_KEYS - set(pairs.keys())
    if missing:
        raise ConfigError(
            f"Missing required key(s): {', '.join(sorted(missing))}"
        )

    width = to_int("WIDTH", pairs["WIDTH"])
    height = to_int("HEIGHT", pairs["HEIGHT"])
    if width < 2 or height < 2:
        raise ConfigError(
            f"Dimensions must be at least 2x2, got {width}x{height}"
        )
    if width > 500 or height > 500:
        raise ConfigError(
            f"Dimensions exceed maximum 500x500, got {width}x{height}"
        )

    entry = parse_coord("ENTRY", pairs["ENTRY"])
    exit_c = parse_coord("EXIT", pairs["EXIT"])

    if not (0 <= entry[0] < width and 0 <= entry[1] < height):
        raise ConfigError(
            f"ENTRY {entry} is outside the maze (0..{width-1}, 0..{height-1})"
        )
    if not (0 <= exit_c[0] < width and 0 <= exit_c[1] < height):
        raise ConfigError(
            f"EXIT {exit_c} is outside the maze (0..{width-1}, 0..{height-1})"
        )
    if entry == exit_c:
        raise ConfigError(f"ENTRY and EXIT cannot be identical: {entry}")

    output_file = pairs["OUTPUT_FILE"]
    perfect = parse_bool("PERFECT", pairs["PERFECT"])
    seed = to_int("SEED", pairs["SEED"]) if "SEED" in pairs else None

    return MazeConfig(
        width=width,
        height=height,
        entry=entry,
        exit=exit_c,
        output_file=output_file,
        perfect=perfect,
        seed=seed,
    )
