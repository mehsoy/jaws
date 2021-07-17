from configparser import ConfigParser

from helpers import Singleton, get_conf_directory


class CopytoolParser(metaclass=Singleton):

    conf_dir = get_conf_directory()
    default_config_file = conf_dir + 'application/copytools.ini'

    def __init__(self, config_file=None):
        config_file = config_file if config_file else self.default_config_file
        self.config = ConfigParser()
        self.config.read(config_file)
        self.copytools = dict()

        sections = self.config.sections()
        for sec in sections:
            tool_dict = dict(self.config.items(sec))
            self.copytools[sec] = tool_dict