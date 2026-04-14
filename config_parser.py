from typing import Self, IO


class ConfigParser:
    REQUIREDKEYS = ['WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 'OUTPUT_FILE', 'PERFECT']
    OPTIONALKEYS = ['SEED', 'ALGORITHM' 'D_MODE']
    VALIDATORS = {
        'WIDTH': lambda v: int(v) > 0,
        'HEIGHT': lambda v: int(v) > 0,
        'SEED': lambda v: True,
        'ENTRY': lambda v: len(v.split(',')) == 2 and all(i.isdigit() for i in v.split(',')),
        'EXIT': lambda v: len(v.split(',')) == 2 and all(i.isdigit() for i in v.split(',')),
        'OUTPUT_FILE': lambda v: len(v) > 0,
        'PERFECT': lambda v: v.lower() in ['true', 'false'],
    }

    CONFIG = {
        'WIDTH': lambda v: int(v),
        'HEIGHT': lambda v: int(v),
        'SEED': lambda v: float(v),
        'ENTRY': lambda v: tuple(map(int, v.split(','))),
        'EXIT': lambda v: tuple(map(int, v.split(','))),
        'OUTPUT_FILE': lambda v: v,
        'PERFECT': lambda v: v.lower() == 'true',
    }

    def __new__(cls) -> Self:
        raise ValueError(f"{cls.__name__} is a static class and cannot be instantiated.")

    @staticmethod
    def validate(config: dict) -> dict:
        for key in ConfigParser.REQUIREDKEYS:
            if key not in config:
                raise ValueError(f"{key}")
        for key, value in config.items():
            if not ConfigParser.VALIDATORS[key](value):
                raise ValueError(f"{value}")
        for key in config:
            config[key] = ConfigParser.CONFIG[key](config[key])
        return config

    @staticmethod
    def parse(config_file: IO) -> dict:
        config = {}
        lines = config_file.readlines()
        for line in lines:
            line = line.strip()

            if not line or line.startswith('#'):
                continue
            elif '=' not in line:
                raise ValueError(f"Invalid line: '{line}'")

            key, value = [ele.strip() for ele in line.split('=', 1)]

            if not (key in ConfigParser.REQUIREDKEYS) and not (key in ConfigParser.OPTIONALKEYS):
                raise ValueError(f"Invalid key: '{key}'")
            if key in ConfigParser.VALIDATORS and ConfigParser.VALIDATORS[key](value):
                config[key] = value

        return ConfigParser.validate(config)
