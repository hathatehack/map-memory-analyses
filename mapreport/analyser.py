# -*- coding: utf-8 -*-
import re
from collections import defaultdict, OrderedDict
import logging


class Analyser:
    """
    Find the objects in each section and classify into certain modules.
    """
    def __init__(self, classification_rules):
        self.classification_rules = []
        for rule in classification_rules:
            self.classification_rules.append(ClassificationRule(**rule))
        self.classification_rules.extend([
            ClassificationRule(match_str='*fill*', classification='*fill*'),
            ClassificationRule(match_str='*expression*', classification='*expression*')
        ])

    def analyse_modules(self, section_data):
        """
        This method finds all object in each section and classify every object file into a modules dictionary.
        The data of each module key is another dictionary that has object as key and a list of
         [section, address, size, sub_section] lists.

        :param section_data: The section data returned by the map file scanner
        :return: A dictionary of modules and a list of sections
        """
        modules = defaultdict(OrderedDict)
        sections_effective = []
        sections_empty = []
        for section, details_dict in section_data:
            size, sub_sections = details_dict['size'], details_dict['sub_sections']
            # Ignore empty section
            if size == '0x0':
                sections_empty.append(section)
                continue

            sections_effective.append(section)
            # Analyse sub sections
            recent_module_list = []  # This is helpful for the special section *fill*. Record the recent name and module pair.
            for [sub_section, address, size, object_name] in sub_sections:
                # Classify object included in sub sections
                module_name = self.classify_by_object(object_name)
                _module = modules[module_name]
                # Merger sub section into module
                if object_name not in _module:
                    _module[object_name] = []
                _module[object_name].append([section, address, int(size, 16), sub_section])
                # Also merger the sub section *fill* into previous module in the same section!
                # yet no previous module found, just put to the list waiting to be consumed
                if module_name == '*expression*':
                    continue
                if module_name != '*fill*':
                    while any(recent_module_list):
                        previous_name, _object = recent_module_list.pop()
                        # Merger previous sub section *fill*
                        if previous_name == '*fill*':
                            if '*fill*' not in _module:
                                _module['*fill*'] = []
                            _module['*fill*'].append(_object)
                    recent_module_list.append([module_name, _module])
                elif recent_module_list:
                    previous = recent_module_list.pop()
                    previous_name, _module = previous
                    if previous_name != '*fill*':
                        if '*fill*' not in _module:
                            _module['*fill*'] = []
                        _module['*fill*'].append([section, address, int(size, 16), '*fill*'])
                    else:
                        recent_module_list.extend([previous, ['*fill*', [section, address, int(size, 16), '*fill*']]])
                else:
                    recent_module_list.extend([['*fill*', [section, address, int(size, 16), '*fill*']]])

        # Move the object *fill* to the end
        for module in modules.values():
            if '*fill*' in module.keys():
                module['*fill*'] = module.pop('*fill*')

        _ = [['UNCLASSIFIED', modules.pop('UNCLASSIFIED', None)],
             ['*expression*', modules.pop('*expression*', None)],
             ['*fill*', modules.pop('*fill*', None)]]
        modules = OrderedDict(modules)
        for key, value in _:
            if value:
                modules[key] = value

        return modules, sections_effective, sections_empty

    def classify_by_object(self, object_name):
        for rule in self.classification_rules:
            classification = rule.classific(object_name)
            if classification:
                return classification

        logging.info("Unclassified %s" % object_name)
        return "UNCLASSIFIED"


class ClassificationRule:
    def __init__(self, match_re=None, match_str=None, classification=None):
        if not (match_re or (match_str and classification)):
            raise ValueError('Provide effective rules such as "match_re", "match_re, classification" or '
                             '"match_str, classification".')
        if match_re:
            self.match_re = re.compile(match_re)
            if not classification:
                self.classific = self.__classific_re
            else:
                self.classification = classification
                self.classific = self.__classific_re_str
        elif match_str:
            self.match_str = match_str
            self.classification = classification
            self.classific = self.__classific_str_str

    def classific(self, string):
        pass

    def __classific_re(self, string):
        m = self.match_re.match(string)
        return m.group(1) if m else None

    def __classific_re_str(self, string):
        return self.classification if self.match_re.match(string) else None

    def __classific_str_str(self, string):
        return self.classification if self.match_str in string else None
