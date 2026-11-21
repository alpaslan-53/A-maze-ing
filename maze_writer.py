"""Export generated maze data into standard hexadecimal output format."""

from mazegen import MazeGenerator

HEX_DIGITS = "0123456789ABCDEF"


def convert_cell_to_hex(cell_value: int) -> str:
    """Convert a cell wall number (0-15) into one hexadecimal character."""
    if cell_value < 0 or cell_value > 15:
        raise ValueError(
            f"Invalid cell value: {cell_value}. Must be between 0 and 15."
        )
    return HEX_DIGITS[cell_value]


def convert_row_to_hex(row: list[int]) -> str:
    """Convert a row of cell numbers into a hexadecimal string."""
    hex_row = ""
    for cell_value in row:
        hex_row = hex_row + convert_cell_to_hex(cell_value)
    return hex_row


def format_maze_output(maze: MazeGenerator) -> str:
    """Build the complete output text in the required hexadecimal format."""
    output_lines: list[str] = []

    for row in maze.grid:
        hex_line = convert_row_to_hex(row)
        output_lines.append(hex_line)

    entry_x, entry_y = maze.entry
    exit_x, exit_y = maze.exit

    output_lines.append("")
    output_lines.append(f"{entry_x},{entry_y}")
    output_lines.append(f"{exit_x},{exit_y}")
    output_lines.append(maze.solution)

    return "\n".join(output_lines) + "\n"


def write_maze(maze: MazeGenerator, file_path: str) -> None:
    """Write the formatted hexadecimal maze text to the destination file."""
    content = format_maze_output(maze)
    with open(file_path, "w", encoding="utf-8", newline="\n") as target_file:
        target_file.write(content)
