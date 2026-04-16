from typing import Dict, Any

REQUIREDKEYS = ['WIDTH', 'HEIGHT', 'ENTRY', 'EXIT', 'OUTPUT_FILE', 'PERFECT']
OPTIONALKEYS = ['SEED', 'ALGORITHM' 'D_MODE']
VALIDATORS = {
    'WIDTH': lambda v: int(v) > 0,
    'HEIGHT': lambda v: int(v) > 0,
    'SEED': lambda v: True,
    'ENTRY': lambda v: (len(v.split(',')) == 2 and
                        all(i.isdigit() for i in v.split(','))),
    'EXIT': lambda v: (len(v.split(',')) == 2 and
                       all(i.isdigit() for i in v.split(','))),
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


def validate(config: Dict[str, Any]) -> Dict:
    for key in REQUIREDKEYS:
        if key not in config:
            raise ValueError(f"{key}")
    for key, value in config.items():
        if not VALIDATORS[key](value):
            raise ValueError(f"{value}")
    for key in config:
        config[key] = CONFIG[key](config[key])
    return config


def parse(file_name: str) -> Dict:
    config = {}
    try:
        with open(file_name, 'r') as file:
            lines = file.readlines()
            for line in lines:
                line = line.strip()

                if not line or line.startswith('#'):
                    continue
                elif '=' not in line:
                    raise ValueError(f"Invalid line: '{line}'")

                key, value = [ele.strip() for ele in line.split('=', 1)]

                if not (key in REQUIREDKEYS) and not (key in OPTIONALKEYS):
                    raise ValueError(f"Invalid key: '{key}'")
                if key in VALIDATORS and VALIDATORS[key](value):
                    config[key] = value
        return validate(config)
    except (Exception, IOError) as e:
        raise ValueError(f"Feilad to Parcing Config: {e}")

