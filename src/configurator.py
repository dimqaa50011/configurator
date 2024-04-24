
import os
from typing import Optional

from dotenv import load_dotenv

from .base.singlton import Singlton


class Configurator(Singlton):
    _MODELS = {}
    _awalable_env_types = {
        int: int, str: str, bool: bool, list: list
    }

    def __init__(
        self, env_path: Optional[str],
    ) -> None:
        super().__init__()
        self._env_path = env_path

    def validate_type(self, type_, value):
        return isinstance(value, type_)

    def env_model(
        self, name: Optional[str] = None,
        env_path: Optional[str] = None,


    ):

        if env_path:
            _env = env_path
        elif self._env_path:
            _env = self._env_path
        else:
            raise AttributeError("attr env_path not set")

        load_dotenv(_env)

        def wrapper(class_model):
            def get_field(field_name, type_, value=None, default=None):
                return {
                    "name": field_name,
                    "value": value,
                    "type_": type_,
                    "default": default
                }

            _fields = {}

            for key, type_ in class_model.__annotations__.items():
                _fields[key] = get_field(key, type_)

            dunder = "__"
            for key, value in class_model.__dict__.items():

                if key.startswith(dunder) or key.startswith(dunder):
                    continue

                __field = _fields.get(key)
                if __field:
                    if not self.validate_type(__field["type_"], value):
                        raise TypeError(
                            f"Types do not match. Your type {type(value)}; annotated = {__field['type_']}")
                    _fields[key] = get_field(
                        key, __field["type_"], default=value)
                else:
                    _fields[key] = get_field(key, type(value), value)

            for name, item in _fields.items():

                _value = None
                if self._awalable_env_types.get(item["type_"]):
                    _data = os.getenv(name)
                    if _data is not None:
                        _value = item["type_"](_data)
                    else:
                        _value = item.get("default")
                else:
                    _value = item.get("default")

                if _value is not None:
                    setattr(class_model, name, _value)
            return class_model

        return wrapper
