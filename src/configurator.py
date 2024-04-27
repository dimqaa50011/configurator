
import os
from typing import Optional

from dotenv import load_dotenv

from src.exc import CacheModelExists, CacheModelNotFound

from .base.singlton import Singlton


class Configurator(Singlton):
    _MODELS = {}
    _available_env_types = {
        int: int, str: str, bool: bool, list: list
    }

    def __init__(
        self,
        debug: Optional[bool] = True,
        env_path: Optional[str] = None,
        cache_models: Optional[bool] = True,
        force_update: Optional[bool] = False
    ) -> None:
        super().__init__()
        self._env_path = env_path
        self._debug = debug
        self._cache_models = cache_models
        self._force_update_cache = force_update

    def get_model(self, model_name: str):
        if self.model_exists(model_name):
            return self._MODELS[model_name]
        raise CacheModelNotFound("Model not found  in cache")

    def model_exists(self, model_name: str):
        try:
            model = self._MODELS[model_name]
            return True
        except KeyError:
            return False

    def validate_type(self, type_, value):
        return isinstance(value, type_)

    def env_model(
        self, name: Optional[str] = None,
        env_path: Optional[str] = None,


    ):
        _MODEL_NAME = name

        if self._debug:
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

            fields_dict = {}

            for key, type_ in class_model.__annotations__.items():
                fields_dict[key] = get_field(key, type_)

            dunder = "__"
            for key, value in class_model.__dict__.items():

                if key.startswith(dunder) or key.endswith(dunder):
                    continue

                annotated_field = fields_dict.get(key)
                if annotated_field:
                    if not self.validate_type(annotated_field["type_"], value):
                        raise TypeError(
                            f"Types do not match. Your type {type(value)}; annotated = {annotated_field['type_']}")
                    fields_dict[key] = get_field(
                        key, annotated_field["type_"], default=value)
                else:
                    fields_dict[key] = get_field(key, type(value), value)

            for name, item in fields_dict.items():

                _value = None
                if self._available_env_types.get(item["type_"]):
                    _data = os.getenv(name)
                    if _data is not None:
                        _value = item["type_"](_data)
                    else:
                        _value = item.get("default")
                else:
                    _value = item.get("default")

                if _value is not None:
                    setattr(class_model, name, _value)

            if self._cache_models:
                _name = _MODEL_NAME if _MODEL_NAME else class_model.__name__

                if self.model_exists(_name):
                    _model = self._MODELS[_name]
                    if self._force_update_cache:
                        self._MODELS[_name] = class_model
                    else:
                        raise CacheModelExists(
                            f"Model {_model} exists in cache! Set the force_update attribute to True to reset the model")
                else:
                    self._MODELS[_name] = class_model
            return class_model

        return wrapper
