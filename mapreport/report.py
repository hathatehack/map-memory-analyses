# -*- coding: utf-8 -*-
from .scanner import Scanner
from .analyser import Analyser
from .formatter import Formatter
from .render import Render
import os
import yaml
# Set global logging config
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')


class Report:
    def __init__(self, map_file, config_file, output_path='.'):
        self.map_file = map_file
        self.output_path = output_path
        # check map and config file exists
        if not os.path.isfile(map_file):
            raise FileNotFoundError('map file %s does not exist!' % map_file)
        if not os.path.isfile(config_file):
            raise FileNotFoundError('config file %s does not exist!' % config_file)
        with open(config_file, 'r') as config:
            self.config = yaml.load(config, Loader=yaml.FullLoader)
        # change working dir to output path
        os.makedirs(output_path, exist_ok=True)
        os.chdir(output_path)

    def generate_report(self):
        sections = Scanner(self.map_file)
        modules, sections_effective, sections_empty =\
            Analyser(self.config.get('classification_rules', {})).analyse_modules(sections)
        formatted_modules = Formatter.format_module(modules, sections_effective)
        summary = Formatter.summary_module(formatted_modules)
        section_group_sizes = Formatter.group_section(summary, self.config.get('section_group_sizes', {}),
                                                      sections_effective, sections_empty)
        Render().render(summary, section_group_sizes, formatted_modules)
