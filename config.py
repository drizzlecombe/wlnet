import json

_current_config = None

#------------------------------------------------------------------------------
class ConfigException(Exception):
    def __init__(self, msg):
        super().__init__(msg)
#------------------------------------------------------------------------------
def load_config_file(filename):
    if filename is None:
        raise ConfigException('No configuration file')
    
    global _current_config
    if _current_config is None:
        # Only load the config once
        config = None
        with open(filename, "r") as fp:
            config = json.load(fp)

        # TODO: might want to do some config value checking here
        _current_config = config
    return _current_config
#------------------------------------------------------------------------------
def get_config() -> dict | None:
    return _current_config
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
__all__ = ['load_config_file', 'get_config', 'ConfigException']