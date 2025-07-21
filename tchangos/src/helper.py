# from dotenv import dotenv_values
import configparser
import json
import os
import random

from constants import FTL_PATH
from fluent.runtime import FluentResource, FluentBundle
# from fluent.runtime.errors import FluentFormatError
from pathlib import Path


class Helper:

    @staticmethod
    def get_general_env(file_):
        # return dotenv_values(file_)
        return []


    @staticmethod
    def get_general_config(file_):
        config = configparser.ConfigParser()
        config.read(file_)
        return config


    @staticmethod
    def get_json(path, default_data=None):
        content = default_data
        with open(path, 'r', encoding='utf-8') as file:
            content = json.loads(file.read())

        return content


    @staticmethod
    def create_unique_filename(path):
        filename = str(random.randint(1, 100))

        while os.path.exists(path + filename):
            filename = str(random.randint(1, 100))

        return filename


    @staticmethod
    def set_json(path, content):
        with open(path, 'w', encoding='utf-8') as file:
            file.write(json.dumps(content))


class FTLExtractor:

    def __init__(self, locale='pt', fallback_locale='pt'):
        self.locale = locale
        self.fallback_locale = fallback_locale
        self.bundle = self.load_bundle(locale)

        if locale != fallback_locale:
            self.fallback_bundle = self.load_bundle(fallback_locale)
        else:
            self.fallback_bundle = self.bundle


    def load_bundle(self, locale):
        bundle = FluentBundle([locale])
        base_dir = Path(FTL_PATH.format(locale))

        if not base_dir.exists():
            return bundle

        for ftl_file in base_dir.glob("*.ftl"):
            content = ftl_file.read_text(encoding="utf-8")
            resource = FluentResource(content)
            bundle.add_resource(resource)
        return bundle


    def extract(self, key, **kwargs):
        bundle = self.bundle
        msg = bundle.get_message(key)
        if msg and msg.value:
            return bundle.format_pattern(msg.value, kwargs)[0]

        fallback = self.fallback_bundle.get_message(key)
        if fallback and fallback.value:
            return self.fallback_bundle.format_pattern(fallback.value, kwargs)[0]

        return f"[Missing translation: {key}]"