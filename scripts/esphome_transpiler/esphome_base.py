from dataclasses import dataclass, field, fields, make_dataclass
from dataclass_wizard import JSONSerializable, JSONWizard, json_field

from actions.action import get_automation_actions, get_automation_conditions
from codegen.dts import DTSProperty
from esphome_const import ESPHOME_PIN
from esphome_types.pin_schema import ESPHomePin

dts_components = []

class CMetadata:
    def __init__(self, **kwargs):
        self.required = False
        if "required" in kwargs:
            self.required = kwargs["required"]
        self.vargs = False
        if "vargs" in kwargs:
            self.vargs = kwargs["vargs"]
        self.type = None
        if "type" in kwargs:
            self.type = kwargs["type"]

    def set_field(self, field):
        self.field = field

    def is_required(self):
        return self.required

    def is_vargs(self):
        return self.vargs

class DTSMetadata:
    def __init__(self, **kwargs):
        self.doc = None
        if "doc" in kwargs:
            self.doc = kwargs["doc"]
        self.name = None
        if "name" in kwargs:
            self.name = kwargs["name"]
        self.required = False
        if "required" in kwargs:
            self.required = kwargs["required"]
        self.child = False
        if "child" in kwargs:
            self.child = kwargs["child"]
        self.type = None
        if "type" in kwargs:
            self.type = kwargs["type"]
        self.enum_values = None
        if "enum_values" in kwargs:
            self.enum_values = kwargs["enum_values"]
    
    def set_field(self, field):
        self.field = field

    def is_field(self):
        return self.child == False
    
    def is_child(self):
        return self.child
    
    def get_name(self):
        if self.name:
            return self.name
        else:
            return self.field.name
    
    def is_required(self):
        return self.required

    def get_doc(self):
        return self.doc

    def get_enum(self):
        return self.enum_values


class CMakeMetadata:
    def __init__(self, **kwargs):
        self.name = None
        if "name" in kwargs:
            self.name = kwargs["name"]
        self.required = False
        if "required" in kwargs:
            self.required = kwargs["required"]
    
    def set_field(self, field):
        self.field = field
    
    def get_name(self):
        if self.name:
            return self.name
        else:
            return self.field.name
    
    def is_required(self):
        return self.required


def MixinField(**kwargs):
    metadata = {}
    if "dts" in kwargs and kwargs["dts"] == True:
        dts_metadata = DTSMetadata(**kwargs)
        metadata['dts'] = dts_metadata

    if "cmake" in kwargs and kwargs["cmake"] == True:
        cmake_metadata = CMakeMetadata(**kwargs)
        metadata['cmake'] = cmake_metadata

    if "c" in kwargs and kwargs["c"] == True:
        c_metadata = CMetadata(**kwargs)
        metadata['c'] = c_metadata

    tmp = field(default=None, metadata=metadata)

    if "dts" in metadata:
        dts_metadata.set_field(tmp)

    if "cmake" in metadata:
        cmake_metadata.set_field(tmp)

    if "c" in metadata:
        c_metadata.set_field(tmp)

    return tmp

def CMakeField(**kwargs):
    kwargs['cmake'] = True
    return MixinField(**kwargs)

def DTSField(**kwargs):
    kwargs['dts'] = True
    return MixinField(**kwargs)

def RequiredDTSField(**kwargs):
    kwargs['required'] = True
    return DTSField(**kwargs)

def RequiredGpioDTSField(**kwargs):
    if "name" not in kwargs:
        kwargs["name"] = "gpios"
    kwargs["type"] = ESPHOME_PIN
    return RequiredDTSField(**kwargs)

def DTSChildField(**kwargs):
    kwargs['child'] = True
    return DTSField(**kwargs)

def DTSEnumField(values, **kwargs):
    kwargs['enum_values'] = values
    return DTSField(**kwargs)

def CRequiredField(**kwargs):
    kwargs["c"] = True
    kwargs["required"] = True
    return MixinField(**kwargs)

def CVargsField(**kwargs):
    kwargs["c"] = True
    kwargs["vargs"] = True
    return MixinField(**kwargs)

#def DTS(compat, doc):
#    def decorator_DTS(cls):
#        setattr(cls, 'dts_compatible', compat)
#        setattr(cls, 'dts_description', doc)
#        dts_components.append(cls)
#        print("kiki mou1")
#        return cls
#    return decorator_DTS
#
#def DTSChild():
#    DTS(None, None)

class RequiredFieldError(Exception):
    def __init__(self, name):
        super().__init__("{} field is not defined".format(name))

class ESPHomeBase(JSONWizard):
    @classmethod
    def is_none(cls, key, o):
        if key not in o or o[key] is None:
            return True
        return False

    @classmethod
    def _pre_from_dict(cls, o):
        for field in fields(cls):
            if "dts" in field.metadata:
                dts_metadata = field.metadata["dts"]
                if dts_metadata.required:
                    if cls.is_none(field.name, o):
                        raise RequiredFieldError("name")

            # Automation may be a list or directly a dict
            # Convert it to a list in such case
            if field.type == list[Automation]:
                if cls.is_none(field.name, o):
                    continue
                automation_data = o[field.name]
                if isinstance(automation_data, list):
                    new_automation_data = []
                    for item in automation_data:
                        if isinstance(item, dict):
                            if "then" in item:
                                new_automation_data.append(item)
                            else:
                                new_automation_data.append({"then": [item]})
                        if isinstance(item, list):
                            new_automation_data.append(item)
                    o[field.name] = new_automation_data
                elif isinstance(automation_data, dict):
                    o[field.name] = [automation_data]
                elif isinstance(automation_data, str):
                    o[field.name] = [{"then": [automation_data]}]
            elif field.type == ESPHomePin:
                pin_data = o[field.name]
                if isinstance(pin_data, str):
                    o[field.name] = {"number": pin_data}
                elif isinstance(pin_data, int):
                    o[field.name] = {"number": "GPIO{}".format(pin_data)}


        return o

    @classmethod
    def dts_compatible(cls):
        return None

    @classmethod
    def dts_description(cls):
        return None

    @classmethod
    def kconfig_symbol(cls):
        return None

    @classmethod
    def kconfig_dependencies(cls):
        return []

    def get_dts_property(self, field_name):
        for field in fields(self):
            if field.name != field_name:
                continue
            dts_prop = DTSProperty(None, self, field)
            return dts_prop.to_string(0)

        return None

@dataclass
class AutomationCondition(ESPHomeBase):
    class Meta(JSONSerializable.Meta):
        json_key_to_field = {
            'or': 'k_or',
            'and': 'k_and',
            'xor': 'k_xor',
        }
        recursive_classes = True

    # TODO check that at least one is defined
    k_or: list['PrivAutomationCondition'] = None
    k_and: list['PrivAutomationCondition'] = None
    k_xor: list['PrivAutomationCondition'] = None


PrivAutomationActionBase = make_dataclass('PrivAutomationAction', get_automation_actions())
class PrivAutomationAction(PrivAutomationActionBase, ESPHomeBase):
    class Meta(JSONSerializable.Meta):
        recursive_classes = True
        raise_on_unknown_json_key = True

    @classmethod
    def _pre_from_dict(cls, o):
        o = super()._pre_from_dict(o)
        for field in fields(cls):
            # Sometime, we may expect a dict but passing a single argument
            # is accepted. Convert this single value to a dict.
            if field.type == dict:
                for key in field.json.keys:
                    if not cls.is_none(key, o):
                        if isinstance(o[key], str):
                            o[key] = {'default_arg': o[key]}
        return o

PrivAutomationConditionBase = make_dataclass('PrivAutomationCondition', get_automation_conditions())
class PrivAutomationCondition(PrivAutomationConditionBase, ESPHomeBase):
    class Meta(JSONSerializable.Meta):
        recursive_classes = True

    @classmethod
    def _pre_from_dict(cls, o):
        o = super()._pre_from_dict(o)
        for field in fields(cls):
            # Sometime, we may expect a dict but passing a single argument
            # is accepted. Convert this single value to a dict.
            if field.type == dict:
                for key in field.json.keys:
                    if not cls.is_none(key, o):
                        if isinstance(o[key], str):
                            o[key] = {'default_arg': o[key]}
        return o

@dataclass
class Automation(ESPHomeBase):
    class Meta(JSONSerializable.Meta):
        json_key_to_field = {
            'then': 'k_then',
            '__all__': True,
        }
        recursive_classes = True

    k_then: list[PrivAutomationAction]

@dataclass
class AutomationIf(ESPHomeBase):
    class Meta(JSONSerializable.Meta):
        json_key_to_field = {
            'then': 'k_then',
            'else': 'k_else',
            '__all__': True,
        }
        recursive_classes = True

    condition: AutomationCondition
    # TODO check that at least one is defined
    k_then: list[PrivAutomationAction] = None
    k_else: list[PrivAutomationAction] = None
