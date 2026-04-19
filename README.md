# A-Maze-ing

A Python-based maze generator and solver featuring configurable maze generation algorithms, interactive visualization, and pathfinding capabilities.

## Summary

A-Maze-ing is an interactive terminal application that generates perfect and imperfect mazes using the Origin-Shift algorithm and solves them using the A* pathfinding algorithm. The project supports multiple visual themes, animated generation/solving, and exports mazes in a custom hex-encoded format.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Algorithms](#algorithms)
- [Project Structure](#project-structure)
- [Themes](#themes)
- [Requirements](#requirements)

## Features

- **Perfect Maze Generation**: Uses the Origin-Shift algorithm to create mazes with exactly one path between any two points
- **Imperfect Mazes**: Optional mode that adds multiple paths and dead ends
- **Interactive CLI**: Real-time menu system with keyboard controls
- **Multiple Themes**: 6 color themes for visual customization
- **Animated Generation**: Watch the maze being generated in real-time
- **Pathfinding**: A* algorithm finds and displays the optimal solution path
- **File Export**: Save generated mazes in hex-encoded format with solution paths
- **42 Logo**: Special locked cells form the "42" logo in the maze center
- **Configurable**: Fully customizable via configuration files

## Installation

### Requirements

- Python 3.10 or higher
- Dependencies listed in `requirements.txt`

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd a-maze-ing
```

2. Install dependencies:
```bash
make install
# or
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
make run
# or
python3 a_maze_ing.py config.txt
```

### Interactive Menu

Once the maze is generated, use the following keyboard commands:

- **`r`** - Re-generate maze (without animation)
- **`R`** - Re-generate with animation
- **`s`** - Toggle solution path visibility
- **`S`** - Animate the solution path
- **`c`** - Change color theme
- **`W`** - Write maze to file
- **`q`** - Exit application

### Debugging

```bash
make debug
```

This launches the Python debugger for step-by-step execution.

## Configuration

Create a configuration file (e.g., `config.txt`) with the following parameters:

```
WIDTH=24              # Maze width in cells
HEIGHT=15             # Maze height in cells
ENTRY=14,14          # Entry point (x,y coordinates)
EXIT=15,0            # Exit point (x,y coordinates)
OUTPUT_FILE=maze.txt # Output filename
PERFECT=True         # True for perfect maze, False for imperfect
SEED=1010            # Random seed (optional, uses current time if not set)
```

### Parameter Descriptions

- **WIDTH/HEIGHT**: Grid dimensions (minimum 3x3, recommended for visibility)
- **ENTRY/EXIT**: Starting and ending coordinates (must be within grid bounds)
- **OUTPUT_FILE**: File where the maze will be saved with solution
- **PERFECT**: 
  - `True` = Single path maze (Origin-Shift only)
  - `False` = Multiple paths and dead ends (Origin-Shift + imperfect modifications)
- **SEED**: Random seed for reproducible mazes (if omitted, uses current timestamp)

## Algorithms

### Origin-Shift Algorithm

The Origin-Shift algorithm generates perfect mazes:

1. Start at a random cell (origin)
2. Move to a random adjacent unvisited cell
3. Open the wall between the current cell and the new cell
4. Repeat until all cells are visited
5. Result: Exactly one path exists between any two points

**Time Complexity**: O(width × height)  
**Space Complexity**: O(width × height) for maze grid + visited set

### A* Pathfinding

Finds the shortest path from entry to exit:

1. Initialize start node with g=0, h=heuristic(start, goal)
2. Add start to open list (priority queue)
3. While open list is not empty:
   - Pop node with lowest f-cost (f = g + h)
   - If goal reached, reconstruct and return path
   - For each neighbor:
     - Calculate tentative g-cost
     - If lower than previous, update and add to open list
4. Return empty list if no path exists

**Heuristic**: Manhattan distance  
**Time Complexity**: O(width × height × log(width × height))  
**Space Complexity**: O(width × height)

### Imperfect Maze Generation

Adds complexity to perfect mazes:

1. For each neighbor of the exit point:
   - Select a random closed wall
   - Open wall to a random adjacent cell
2. Repeat for entry point
3. Result: Multiple paths exist, creating a more challenging maze

## Project Structure

```
a-maze-ing/
├── a_maze_ing.py              # Main entry point
├── config.txt                 # Configuration file (example)
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── Makefile                   # Build commands
├── mazegenerator/
│   ├── __init__.py           # Package exports
│   ├── MazeGenerator.py       # Core generation logic
│   ├── MazeCell.py           # Grid cell representation
│   ├── MazeConfig.py         # Configuration parser
│   ├── MazeRenderer.py       # Terminal rendering
│   ├── cell_encoding.py      # Bit manipulation utilities
│   └── themes/               # Color theme definitions
└── .git/                     # Git repository
```

### Key Modules

- **MazeGenerator**: Orchestrates maze generation pipeline (build → generate → solve → save)
- **MazeCell**: Represents a single grid cell with wall state and A* search metadata
- **MazeRenderer**: Handles terminal-based rendering with color themes
- **cell_encoding**: Utility functions for encoding/decoding cell properties using bit manipulation

## Cell Encoding

Each maze cell stores data in a single byte (8 bits):

**Bits 0-3** (Wall Configuration):
- Bit 0: North wall (1 = closed, 0 = open)
- Bit 1: East wall
- Bit 2: South wall
- Bit 3: West wall

**Bits 4-7** (Cell Type):
- `0000` = Normal cell
- `0001` = Start/Entry point
- `0010` = End/Exit point
- `0011` = Solution path
- `1000` = Generation origin
- `1100` = Visited during pathfinding
- `1111` = Locked cell (cannot be modified)

## Themes

The application includes 6 built-in color themes:

1. **royal_depth** - Deep purples and blues
2. **dark_forest** - Dark greens and earth tones
3. **deep_ocean** - Cyan and navy blues
4. **ember_core** - Reds and oranges
5. **midnight_blue** - Cool blue tones
6. **steel_industrial** - Gray and steel tones

Switch themes at runtime using the `[c]` menu option.

## File Format

### Output Maze File Format

```
<hex_grid>          # Each cell as hexadecimal (wall configuration + type)
<blank_line>
<entry_x>,<entry_y> # Entry coordinates
<exit_x>,<exit_y>   # Exit coordinates
<path_directions>   # Solution path as N/S/E/W characters
```

**Example**:
```
0123456789ABCDEF
F0F0F0F0F0F0F0F0
...
14,14
15,0
EEESSSSWWWWN...
```

## Code Quality

The project maintains high code quality standards:

- **Linting**: `flake8` for style compliance
- **Type Checking**: `mypy` with strict type hints
- **Python Version**: 3.10+

Run linting:
```bash
make lint          # Standard linting
make lint-strict   # Strict mode with mypy
```

## Requirements

See `requirements.txt` for complete dependencies:
- pydantic (≥2.13.2) - Configuration validation
- annotated-types - Type annotation support
- typing-inspection - Advanced type handling

## Troubleshooting

### Terminal Display Issues
- Ensure your terminal supports ANSI color codes
- Try resizing the terminal window
- On Windows, consider using Windows Terminal or WSL

### Large Maze Animation
- For mazes larger than ~1000 cells, the application prompts to confirm animation
- Use `R` for animated generation or `r` for instant generation
- Use `S` for animated solution or `s` for instant solution

### Reproducibility
- Set a fixed SEED value in config.txt to generate the same maze
- Default (no SEED) uses current timestamp for randomness

## Development

### Running Tests
```bash
make test  # If test suite is configured
```

### Cleaning Build Artifacts
```bash
make clean
```

## Team & Retrospective

### Team Members

- **Amissa** - Pathfinding and Maze Generation Algorithms
- **Amedina** - Makefile Configuration and Documentation

### What Worked Well ✅

- **A* Pathfinding Algorithm**: The pathfinding implementation performs excellently, efficiently finding optimal solution paths with good performance across various maze sizes. The algorithm handles both perfect and imperfect mazes without issues.

### Areas for Improvement 🔧

- **Maze Generator Performance**: The Origin-Shift algorithm experiences performance degradation with large maze sizes (1000+ cells). Generation time increases significantly, and the algorithm may be slow during animated generation. Potential optimizations:
  - Implement iterative approaches instead of recursive patterns
  - Use more efficient data structures for tracking visited cells
  - Parallelize generation where possible
  - Cache frequently accessed neighbor calculations

### Bonus Features 🎁

- **Animation System**: Implemented real-time animation for both maze generation and pathfinding processes
  - Animated generation (`R` command) shows the origin-shift algorithm in action
  - Animated solution (`S` command) visualizes the A* pathfinding step-by-step
  - Automatic performance optimization for large mazes (prompts user for large maze animations)
  - Smooth visual feedback with configurable animation timing

### Lessons Learned

- Bit-level cell encoding provides memory-efficient storage but requires careful implementation
- Interactive terminal rendering with ANSI codes offers engaging user experience
- Balancing visual feedback with performance is crucial for larger datasets
- Comprehensive configuration system enables flexible maze generation scenarios

## License

This project is part of the 42 school curriculum.

## Authors

- **Amissa** - Pathfinding and Maze Generation Algorithms
- **Amedina** - Makefile and Documentation