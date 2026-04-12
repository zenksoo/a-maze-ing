# module for errors type


class ProjectBaseError(Exception):
    def __str__(self) -> str:
        return "MAZE ERROR:"


class InstantiationError(ProjectBaseError):
    def __str__(self) -> str:
        return f"{self.args[0]}"


class InvalidConfiguration(ProjectBaseError):
    def __str__(self) -> str:
        return super().__str__()


class MissingKey(ProjectBaseError):
    def __str__(self) -> str:
        return f"Missing Required Key '{self.args[0]}'"


class InvalidValue(ProjectBaseError):
    def __str__(self) -> str:
        return f"Invalid Value {self.args[0]}"


class ConfigParseError(ProjectBaseError):
    def __str__(self) -> str:
        return f"{self.args[0]}"
