"""Configuration parser and validator for A-Maze-ing."""

from dataclasses import dataclass

REQUIRED_KEYS = (
    "WIDTH",
    "HEIGHT",
    "ENTRY",
    "EXIT",
    "OUTPUT_FILE",
    "PERFECT",
)


class ConfigError(ValueError):
    """Raised when configuration values are invalid or missing."""

    pass


@dataclass(frozen=True)
class MazeConfig:
    """Container holding validated maze settings."""

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None


def read_config_file(file_path: str) -> dict[str, str]:
    """Read KEY=VALUE pairs from the configuration file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except OSError as error:
        raise ConfigError(
            f"Cannot open configuration file '{file_path}': {error}"
        )
    except UnicodeDecodeError:
        raise ConfigError(
            f"'{file_path}' is not a readable text file. "
            "Please save it as plain UTF-8 text."
        )

    settings: dict[str, str] = {}
    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if line == "" or line.startswith("#"):
            continue

        if "=" not in line:
            raise ConfigError(
                f"Line {line_number}: invalid format in '{line}'. "
                "Every line must be in 'KEY=VALUE' format."
            )

        key_part, value_part = line.split("=", 1)
        key = key_part.strip()
        value = value_part.strip()

        if key == "" or value == "":
            raise ConfigError(
                f"Line {line_number}: empty key or value in '{line}'. "
                "Please provide both a key and a value."
            )

        if key in settings:
            raise ConfigError(
                f"Line {line_number}: duplicate key '{key}'. "
                "Each setting can only be defined once."
            )

        settings[key] = value

    return settings


def convert_to_int(key_name: str, value: str) -> int:
    """Convert a digit string to an integer with clear error messages."""
    if value.startswith("-") and value[1:].isdigit():
        raise ConfigError(
            f"Invalid value for '{key_name}': '{value}'. "
            "Negative numbers are not allowed; "
            "please enter zero or a positive number."
        )
    if not (value.isascii() and value.isdigit()):
        raise ConfigError(
            f"Invalid value for '{key_name}': '{value}'. "
            "Please enter a valid number using digits only (e.g. 10)."
        )
    return int(value)


def convert_to_coord(key_name: str, value: str) -> tuple[int, int]:
    """Convert 'x,y' text into an (x, y) integer tuple."""
    parts = value.split(",")
    if len(parts) != 2:
        raise ConfigError(
            f"Invalid coordinates for '{key_name}': '{value}'. "
            "Coordinates must be written as two numbers separated by a comma "
            "(e.g. 0,0)."
        )
    x_pos = convert_to_int(f"{key_name} (x)", parts[0].strip())
    y_pos = convert_to_int(f"{key_name} (y)", parts[1].strip())
    return (x_pos, y_pos)


def convert_to_bool(key_name: str, value: str) -> bool:
    """Convert 'True' or 'False' text into a boolean value."""
    if value == "True":
        return True
    if value == "False":
        return False
    raise ConfigError(
        f"Invalid value for '{key_name}': '{value}'. "
        "Please enter strictly 'True' or 'False'."
    )


def load_config(file_path: str) -> MazeConfig:
    """Read, validate, and return the maze configuration."""
    settings = read_config_file(file_path)

    for key in REQUIRED_KEYS:
        if key not in settings:
            raise ConfigError(
                f"Missing required setting: '{key}' was not found in the file."
            )

    width = convert_to_int("WIDTH", settings["WIDTH"])
    height = convert_to_int("HEIGHT", settings["HEIGHT"])

    if width < 2 or height < 2:
        raise ConfigError(
            f"Maze dimensions are too small ({width}x{height}). "
            "Minimum allowed size is 2x2."
        )
    if width > 500 or height > 500:
        raise ConfigError(
            f"Maze dimensions are too large ({width}x{height}). "
            "Maximum allowed size is 500x500."
        )

    entry_point = convert_to_coord("ENTRY", settings["ENTRY"])
    exit_point = convert_to_coord("EXIT", settings["EXIT"])

    entry_x, entry_y = entry_point
    if entry_x >= width or entry_y >= height:
        raise ConfigError(
            f"ENTRY ({entry_x},{entry_y}) is outside the maze boundaries. "
            f"Valid range is x: 0..{width - 1}, y: 0..{height - 1}."
        )

    exit_x, exit_y = exit_point
    if exit_x >= width or exit_y >= height:
        raise ConfigError(
            f"EXIT ({exit_x},{exit_y}) is outside the maze boundaries. "
            f"Valid range is x: 0..{width - 1}, y: 0..{height - 1}."
        )

    if entry_point == exit_point:
        raise ConfigError(
            f"ENTRY and EXIT cannot be at the same position: {entry_point}. "
            "Please choose two different coordinates."
        )

    output_file = settings["OUTPUT_FILE"]
    perfect = convert_to_bool("PERFECT", settings["PERFECT"])

    if "SEED" in settings:
        seed_value: int | None = convert_to_int("SEED", settings["SEED"])
    else:
        seed_value = None

    return MazeConfig(
        width=width,
        height=height,
        entry=entry_point,
        exit=exit_point,
        output_file=output_file,
        perfect=perfect,
        seed=seed_value,
    )
