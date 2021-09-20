# -*- coding: utf-8 -*-
import re
import logging


class Scanner:
    """
    This class is a section iterator.
    Scan the map file, and yield each section in a lazy-loading way through the generator.
    """
    def __init__(self, map_file):
        self.map_file = map_file
        self.section_start_pattern = re.compile(r"^\.[\w\"]")
        self.end_line_pattern = re.compile(r"^OUTPUT\(\w+\.elf")
        self.__section_start_line = None

    def __iter__(self):
        lines = self.read_lines()
        for section_contents in self.scan_sections(lines):
            name, address, size, remaining_lines = self.read_section_details(section_contents)
            if name is not None:
                details = {
                    "address": address,
                    "size": size,
                    "sub_sections": self.gather_sub_sections(name, remaining_lines)
                }
                yield name, details

    def read_lines(self):
        with open(self.map_file, 'r') as f:
            line = f.readline()
            while self.section_start_pattern.match(line) is None:
                line = f.readline()
            self.__section_start_line = line
            while self.end_line_pattern.match(line) is None:
                yield line
                line = f.readline()
            # At the end of valid section line, stop reading.
            self.__section_start_line = None

    def scan_sections(self, lines):
        lines.__next__()
        while self.__section_start_line:
            # Start scanning a new section
            yield self.__scan_section(lines)

    def __scan_section(self, remaining_lines):
        yield self.__section_start_line
        for line in remaining_lines:
            if self.section_start_pattern.match(line) is None:
                yield line
            else:
                self.__section_start_line = line
                # Finish scanning a section and stop this generator.
                return

    def read_section_details(self, section_contents):
        title = section_contents.__next__().split()
        if len(title) == 1:
            if len(title[0]) > 14:
                # Name is too big so it appears on a single line, and address and size follow on next line.
                title += section_contents.__next__().split()
            else:
                # Something unexpected, just discard and skip the contents.
                logging.warning('Got unexpected section %s' % title[0])
                title = (None, None, None)
                for _ in section_contents:
                    pass
        return title[0], title[1], title[2], section_contents

    def gather_sub_sections(self, section_name, lines):
        sub_sections = []
        for section in self.read_sub_sections(section_name, lines):
            sub_sections.append(section)
        return sub_sections

    def read_sub_sections(self, section_name, lines):
        sub_name = None
        fill_pattern = re.compile(r"^ \*fill\*\s+([0-9A-Fa-fx]+)\s+([0-9A-F-a-fx]+)\s*$")
        expression_pattern = re.compile(r"^ {16}([0-9A-Fa-fx]+)\s+([0-9A-F-a-fx]+)\s+\w+\s+[0-9A-F-a-fx]+[\s\w\(\)]*$")
        full_pattern = re.compile(r"^ ([\.\w]+)\s+([0-9A-Fa-fx]+)\s+([0-9A-Fa-fx]+)\s+([:\\\s\(\)\-\./\w]+\.o[\)]*)$")
        name_part_pattern = re.compile(r"^ [\.\w]+$")
        remainder_pattern = re.compile(r"^ {16}([0-9A-Fa-fx]+)\s+([0-9A-Fa-fx]+)\s+([:\\\s\(\)\-\./\w]+\.o[\)]*)$")
        for line in lines:
            # Full object file info is within the line
            m = full_pattern.match(line)
            if m:
                yield list(m.groups())
                sub_name = m.group(1)
                continue
            # Name is too big so it appears on a single line
            m = name_part_pattern.match(line)
            if m:
                sub_name = line.strip()
                continue
            # The remainder of the above name
            m = remainder_pattern.match(line)
            if m:
                to_yield = [sub_name]
                yield to_yield + list(m.groups())
                continue
            # fill object
            m = fill_pattern.match(line)
            if m:
                yield [sub_name if sub_name else section_name] + list(m.groups()) + ["*fill*"]
                continue
            # expression object
            m = expression_pattern.match(line)
            if m:
                yield [section_name] + list(m.groups()) + ["*expression*"]
                sub_name = None
                continue
