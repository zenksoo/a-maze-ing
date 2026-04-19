from typing import Dict, TextIO
from pydantic import BaseModel, Field, field_validator
import os


class MazeConfig(BaseModel):
    width: int = Field(ge=9)
    height: int = Field(ge=7)
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: float | None

    @field_validator('entry', 'exit', mode="before")
    def coordinate_validation(cls, val: str) -> tuple[int, int]:
        try:
            coor = val.split(",")
            if len(coor) != 2:
                raise ValueError("Coordinate Must be in x,y format")
            return (int(coor[0].strip()), int(coor[1].strip()))
        except (ValueError, IndexError):
            raise ValueError("Coordinate must be in x,y format")

    @field_validator('output_file')
    def validate_output_file(cls, val: str) -> str:
        if not val:
            raise ValueError("Output file cannot be empty")
        if os.path.isdir(val):
            raise ValueError(f"Output file '{val}' is a directory")
        if val.endswith('.py'):
            raise ValueError("Output file cannot have a .py extension")
        return val

    @classmethod
    def from_file(cls, f: TextIO) -> 'MazeConfig':
        """ Create a MazeConfig instance by reading and parsing a configuration file.

        Args:
            f (TextIO): A file-like object containing the maze configuration in key=value format.

        Returns:
            MazeConfig: An instance of MazeConfig populated with the parsed configuration values.
        """
        REQUIRED = [
            'WIDTH', 'HEIGHT', 'ENTRY',
            'EXIT', 'OUTPUT_FILE', 'PERFECT']

        data: Dict[str, str] = {}
        try:
            lines = f.readlines()
            for line in lines:
                line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=")
                key = key.strip().upper()
                val = val.strip().upper()
                if key in data and key in REQUIRED and val != data[key]:
                    raise ValueError(f"Douplicate Key {key.strip()}")
                data[key] = val
        except FileNotFoundError:
            raise ValueError(f"Config File {f.name} not found")
        except PermissionError:
            raise ValueError(f"Permission Denied for config file {f.name}")
        except IOError as e:
            raise ValueError(f"Failed Reading config file {e}")
        except Exception as e:
            raise ValueError(e)

        mis = []
        for key in REQUIRED:
            if key not in data:
                mis.append(key)
        if mis:
            er_msg = f"Missing Required Configuration: {', '.join(mis)}"
            raise ValueError(er_msg)

        return cls(
            width=int(data["WIDTH"]),
            height=int(data["HEIGHT"]),
            entry=data["ENTRY"],  # type: ignore
            exit=data["EXIT"],  # type: ignore
            output_file=data["OUTPUT_FILE"],
            perfect=data["PERFECT"].lower() == "true",
            seed=float(data["SEED"]) if "SEED" in data else None
        )
