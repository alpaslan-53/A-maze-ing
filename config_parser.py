"""Configuration parser and validator for A-Maze-ing."""

from dataclasses import dataclass


class ConfigError(ValueError):
    """Raised when configuration values are malformed or missing."""

    pass


@dataclass(frozen=True)
class MazeConfig:
    """Immutable container holding validated maze settings."""

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None


def read_pairs(path: str) -> dict[str, str]:
    """Extract raw key-value definitions from the specified file."""
    try:
        with open(path, "r", encoding="utf-8") as file_handle:
            raw_lines = file_handle.readlines()
    except OSError as err:
        raise ConfigError(f"Cannot read config file '{path}': {err}")

    config_map: dict[str, str] = {}
    for line_idx, raw_line in enumerate(raw_lines, start=1):
        content = raw_line.strip()
        if not content or content.startswith("#"):
            continue
        if "=" not in content:
            raise ConfigError(f"Line {line_idx}: missing '=' in '{content}'")
        key_part, val_part = content.split("=", 1)
        key, val = key_part.strip(), val_part.strip()
        if not key or not val:
            raise ConfigError(
                f"Line {line_idx}: empty key or value in '{content}'"
            )
        if key in config_map:
            raise ConfigError(f"Line {line_idx}: duplicate key '{key}'")
        config_map[key] = val
    return config_map


def to_int(name: str, value: str) -> int:
    """Parse positive numerical digit string into an integer."""
    if not value.isascii() or not value.isdigit():
        raise ConfigError(
            f"'{name}' must be a non-negative integer, got '{value}'"
        )
    return int(value)


def parse_coord(name: str, value: str) -> tuple[int, int]:
    """Convert comma-separated coordinates 'x,y' into an integer pair."""
    segments = value.split(",")
    if len(segments) != 2:
        raise ConfigError(
            f"'{name}' must be in 'x,y' format, got '{value}'"
        )
    coord_x = to_int(f"{name}.x", segments[0].strip())
    coord_y = to_int(f"{name}.y", segments[1].strip())
    return (coord_x, coord_y)


def parse_bool(name: str, value: str) -> bool:
    """Convert explicit boolean string to native bool."""
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
    """Parse config file, enforce validation rules, and return config."""
    config_map = read_pairs(path)

    missing_keys = REQUIRED_KEYS - set(config_map.keys())
    if missing_keys:
        formatted = ", ".join(sorted(missing_keys))
        raise ConfigError(f"Missing required key(s): {formatted}")

    maze_w = to_int("WIDTH", config_map["WIDTH"])
    maze_h = to_int("HEIGHT", config_map["HEIGHT"])
    if maze_w < 2 or maze_h < 2:
        raise ConfigError(
            f"Dimensions must be at least 2x2, got {maze_w}x{maze_h}"
        )
    if maze_w > 500 or maze_h > 500:
        raise ConfigError(
            f"Dimensions exceed maximum 500x500, got {maze_w}x{maze_h}"
        )

    start_cell = parse_coord("ENTRY", config_map["ENTRY"])
    end_cell = parse_coord("EXIT", config_map["EXIT"])

    if not (0 <= start_cell[0] < maze_w and 0 <= start_cell[1] < maze_h):
        raise ConfigError(
            f"ENTRY {start_cell} is outside the maze "
            f"(0..{maze_w - 1}, 0..{maze_h - 1})"
        )
    if not (0 <= end_cell[0] < maze_w and 0 <= end_cell[1] < maze_h):
        raise ConfigError(
            f"EXIT {end_cell} is outside the maze "
            f"(0..{maze_w - 1}, 0..{maze_h - 1})"
        )
    if start_cell == end_cell:
        raise ConfigError(f"ENTRY and EXIT cannot be identical: {start_cell}")

    target_file = config_map["OUTPUT_FILE"]
    is_perfect = parse_bool("PERFECT", config_map["PERFECT"])
    random_seed = (
        to_int("SEED", config_map["SEED"])
        if "SEED" in config_map
        else None
    )

    return MazeConfig(
        width=maze_w,
        height=maze_h,
        entry=start_cell,
        exit=end_cell,
        output_file=target_file,
        perfect=is_perfect,
        seed=random_seed,
    )
