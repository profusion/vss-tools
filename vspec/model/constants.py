#!/usr/bin/env python3

#
#
#
# All files and artifacts in this repository are licensed under the
# provisions of the license provided by the LICENSE file in this repository.
#

#
# Constant Types and Mappings
#
# noinspection PyPackageRequirements
from typing import (
    Sequence, Type, TypeVar, Optional, Dict, Tuple, NamedTuple, Iterator,
    TextIO
)

import yaml

from vspec.model import NON_ALPHANUMERIC_WORD, CONFIG_PATH


def _is_dunder(name):
    """Returns True if a __dunder__ name, False otherwise."""
    return (len(name) > 4 and
            name[:2] == name[-2:] == '__' and
            name[2] != '_' and
            name[-3] != '_')


def _is_sunder(name):
    """Returns True if a _sunder_ name, False otherwise."""
    return (len(name) > 2 and
            name[0] == name[-1] == '_' and
            name[1:2] != '_' and
            name[-2:-1] != '_')


T = TypeVar("T")


class VSSConstant(NamedTuple):
    label: str
    value: str
    description: Optional[str] = None
    domain: Optional[str] = None


class VSSEnumMeta(type):
    """This class defines the enumeration behavior for vss:
     - from_str(str): reverse lookup
     - values(): sequence of values
    """
    def __new__(mcs, cls, bases, classdict):
        cls = super().__new__(mcs, cls, bases, classdict)

        if not hasattr(cls, '__reverse_lookup__'):
            cls.__reverse_lookup__ = {
                v.value: v for k, v in classdict.items() if not _is_dunder(k) and not _is_sunder(k)
            }
        if not hasattr(cls, '__values__'):
            cls.__values__ = tuple(cls.__reverse_lookup__.keys())

        return cls

    def from_str(cls: Type[T], value: str) -> T:
        return cls.__reverse_lookup__[value]

    def values(cls: Type[T]) -> Sequence[str]:
        return cls.__values__


class VSSEnumMetaConfigurable(VSSEnumMeta):
    __config_path__ = CONFIG_PATH

    def __new__(mcs, cls, bases, classdict):
        with open(mcs.__config_path__, mode='r') as config_file:
            yaml_config = yaml.safe_load(config_file)
            for k, v in iterate_config_members(yaml_config, classdict['__config_name__']):
                classdict[k] = v
        cls = super().__new__(mcs, cls, bases, classdict)
        return cls

    def add_config(cls, config: dict):
        for k, v in iterate_config_members(config, cls.__dict__['__config_name__']):
            setattr(cls, k, v)
            cls.__reverse_lookup__[v.value] = v
        cls.__values__ = tuple(cls.__reverse_lookup__.keys())

    def from_str(cls: Type[T], value: str) -> T:
        return cls.__reverse_lookup__[value]

    def values(cls: Type[T]) -> Sequence[str]:
        return cls.__values__


class StringStyle(metaclass=VSSEnumMeta):
    NONE = VSSConstant('none', 'none')
    CAMEL_CASE = VSSConstant('camel case', 'camelCase')
    CAMEL_BACK = VSSConstant('camel back', 'camelBack')
    CAPITAL_CASE = VSSConstant('capital case', 'capitalcase')
    CONST_CASE = VSSConstant('const case', 'constcase')
    LOWER_CASE = VSSConstant('lower case', 'lowercase')
    PASCAL_CASE = VSSConstant('pascal case', 'pascalcase')
    SENTENCE_CASE = VSSConstant('sentence case', 'sentencecase')
    SNAKE_CASE = VSSConstant('snake case', 'snakecase')
    SPINAL_CASE = VSSConstant('spinal case', 'spinalcase')
    TITLE_CASE = VSSConstant('title case', 'titlecase')
    TRIM_CASE = VSSConstant('trim case', 'trimcase')
    UPPER_CASE = VSSConstant('upper case', 'uppercase')
    ALPHANUM_CASE = VSSConstant('alphanum case', 'alphanumcase')


class VSSType(metaclass=VSSEnumMeta):
    BRANCH = VSSConstant('branch', 'branch')
    RBRANCH = VSSConstant('rbranch', 'rbranch')
    ATTRIBUTE = VSSConstant('attribute', 'attribute')
    SENSOR = VSSConstant('sensor', 'sensor')
    ACTUATOR = VSSConstant('actuator', 'actuator')
    ELEMENT = VSSConstant('element', 'element')


class VSSDataType(metaclass=VSSEnumMeta):
    INT8 = VSSConstant('int8', 'int8')
    UINT8 = VSSConstant('uint8', 'uint8')
    INT16 = VSSConstant('int16', 'int16')
    UINT16 = VSSConstant('uint16', 'uint16')
    INT32 = VSSConstant('int32', 'int32')
    UINT32 = VSSConstant('uint32', 'uint32')
    INT64 = VSSConstant('int64', 'int64')
    UINT64 = VSSConstant('uint64', 'uint64')
    BOOLEAN = VSSConstant('boolean', 'boolean')
    FLOAT = VSSConstant('float', 'float')
    DOUBLE = VSSConstant('double', 'double')
    STRING = VSSConstant('string', 'string')
    UNIX_TIMESTAMP = VSSConstant('UNIX Timestamp', 'UNIX Timestamp')
    INT8_ARRAY = VSSConstant('int8[]', 'int8[]')
    UINT8_ARRAY = VSSConstant('uint8[]', 'uint8[]')
    INT16_ARRAY = VSSConstant('int16[]', 'int16[]')
    UINT16_ARRAY = VSSConstant('uint16[]', 'uint16[]')
    INT32_ARRAY = VSSConstant('int32[]', 'int32[]')
    UINT32_ARRAY = VSSConstant('uint32[]', 'uint32[]')
    INT64_ARRAY = VSSConstant('int64[]', 'int64[]')
    UINT64_ARRAY = VSSConstant('uint64[]', 'uint64[]')
    BOOLEAN_ARRAY = VSSConstant('boolean[]', 'boolean[]')
    FLOAT_ARRAY = VSSConstant('float[]', 'float[]')
    DOUBLE_ARRAY = VSSConstant('double[]', 'double[]')
    STRING_ARRAY = VSSConstant('string[]', 'string[]')
    UNIX_TIMESTAMP_ARRAY = VSSConstant('UNIX Timestamp[]', 'UNIX Timestamp[]')


def dict_to_constant_config(name: str, info: Dict) -> Tuple[str, VSSConstant]:
    assert ('label' in info)  # label is mandatory

    label = NON_ALPHANUMERIC_WORD.sub('', info['label']).upper()
    description = info.get('description', None)
    domain = info.get('domain', None)
    return label, VSSConstant(info['label'], name, description, domain)


def iterate_config_members(config_dict: dict, config_name: str) -> Iterator[Tuple[str, VSSConstant]]:
    if config_name in config_dict:
        config = config_dict[config_name]
        for u, v in config.items():
            yield dict_to_constant_config(u, v)


class Unit(metaclass=VSSEnumMetaConfigurable):
    __config_name__ = 'units'
