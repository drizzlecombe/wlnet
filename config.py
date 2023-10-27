import json

_current_config = None

#------------------------------------------------------------------------------
class ConfigException(Exception):
    def __init__(self, msg):
        super().__init__(msg)
#------------------------------------------------------------------------------
def load_config_file(filename) -> dict|None:
    if filename is None:
        raise ConfigException('No configuration file')

    global _current_config
    config = None
    if _current_config is None:
        # Only load the config once
        with open(filename, "r") as fp:
            config = json.load(fp)

        # TODO: might want to do some config value checking here
        _current_config = config
        return config
#------------------------------------------------------------------------------
def get_database_name() -> str | None:
    return _current_config['database_name']

#------------------------------------------------------------------------------
def get_raw_checkin_filename() -> str | None:
    return _current_config['raw_checkin_filename']

#------------------------------------------------------------------------------
def get_raw_checkin_fieldnames() -> list[str] | None:
    return _current_config['raw_checkin_field_names']

#------------------------------------------------------------------------------
def get_num_header_lines() -> int | None:
    return int(_current_config['num_header_lines'])
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
# Test code below here
#------------------------------------------------------------------------------
def main():
    config = load_config_file('config.json')
    for k, v in config.items():
        print(k, v)

if __name__ == '__main__':
    main()
#------------------------------------------------------------------------------
# External interface
#------------------------------------------------------------------------------
__all__ = ['load_config_file',
           'get_num_header_lines',
           'get_raw_checkin_filename',
           'get_raw_checkin_fieldnames',
           'ConfigException']