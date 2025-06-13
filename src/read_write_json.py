import json
import os
from error import ErrorCheck

class ReadWriteJSON:
    def get_config_path(self):
        config_path = os.path.join(
                os.path.join(
                    os.path.dirname(__file__),
                    "..", "config", "config.json"
                    )
                )

        ErrorCheck().error_check_for_loading_config(config_path)
        return config_path

    def read_config(self):
        config_path = self.get_config_path()

        with open(config_path, "r") as f:
            return json.load(f)

    def write_config(self, config):
        config_path = self.get_config_path()

        with open(config_path, "w") as f:
            json.dump(config, f, indent = 4)

    def update_config(self, key, value):
        config = self.read_config()
        config[key] = value
        self.write_config(config)

    def add_profile_to_config(self, profile_name, remote_host):
        config = self.read_config()

        if "profiles" not in config or not isinstance(config["profiles"], list):
            config["profiles"] = []

        for profile in config["profiles"]:
            if profile.get("name") == profile_name and profile.get("host") == remote_host:
                return


