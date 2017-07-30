# coding: utf-8
# Copyright (c) Pymatgen Development Team.
# Distributed under the terms of the MIT License.

from __future__ import division, print_function, unicode_literals, absolute_import

"""
This module implements classes for reading and generating Lammps input.
"""

import os
from string import Template

from monty.json import MSONable


__author__ = "Kiran Mathew, Brandon Wood"
__email__ = "kmathew@lbl.gov, b.wood@berkeley.edu"
__credits__ = "Navnidhi Rajput"

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))


class LammpsInput(MSONable):

    def __init__(self, contents, settings, delimiter):
        self.contents = contents
        self.settings = settings
        self.delimiter = delimiter

        # make read_data configurable i.e "read_data $${data_file}"
        if ("data_file" not in self.settings and
                    self.contents.find("read_data") >= 0):
            self.settings["data_file"] = \
                self.contents.split("read_data")[-1].split("\n")[0].expandtabs().strip()
            self.contents = \
                self.contents.replace(self.settings["data_file"],
                                      "$${data_file}", 1)

    def __str__(self):
        template = self.get_template(self.__class__.__name__,
                                     delimiter=self.delimiter)
        template_string = template(self.contents)

        # might contain unused parameters as leftover $$
        unclean_template = template_string.safe_substitute(self.settings)

        clean_template = filter(lambda l: self.delimiter not in l,
                                unclean_template.split('\n'))

        return '\n'.join(clean_template)

    @classmethod
    def from_string(cls, input_string, settings=None, delimiter="$$"):
        return cls(input_string, settings, delimiter)

    @classmethod
    def from_file(cls, input_file, settings, delimiter="$$"):
        with open(input_file) as f:
            return cls.from_string(f.read(), settings, delimiter)

    def write_file(self, filename):
        with open(filename, 'w') as f:
            f.write(self.__str__())

    @staticmethod
    def get_template(name, delimiter="$$"):
        return type(name, (Template,), {"delimiter": delimiter})
