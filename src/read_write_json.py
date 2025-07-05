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

    def add_profile_to_config(self, profile_name, remote_host, used_passwd, passwd, filename):
        config = self.read_config()

        if "profiles" not in config or not isinstance(config["profiles"], dict):
            config["profiles"] = {}

        if profile_name in config["profiles"]:
                return

        config["profiles"][profile_name] = {
            "host": remote_host,
            "used_passwd": used_passwd,
            "passwd": passwd,
            "filename": filename
            }

        self.write_config(config)

    def edit_profile_from_config(
            self, 
            old_profile_name, 
            new_profile_name, 
            remote_host, 
            used_passwd, 
            passwd, 
            filename, 
            password_changed
            ):
        config = self.read_config()

        if "profiles" in config and old_profile_name in config["profiles"]:
            profile_data = config["profiles"].pop(old_profile_name)

            profile_data["host"] = remote_host

            if password_changed:
                profile_data["used_passwd"] = used_passwd
                profile_data["passwd"] = passwd

            profile_data["filename"] = filename

            config ["profiles"][new_profile_name] = profile_data

            self.write_config(config)
            print(f"Profile renamed from '{old_profile_name}' to {new_profile_name}' and updated.")

    def delete_profile_from_config(self, profile_name):
        config = self.read_config()

        if "profiles" in config and profile_name in config["profiles"]:
            del config["profiles"][profile_name]
            self.write_config(config)
            print(f"Profile '{profile_name}' deleted from config.")
        else:
            print(f"Profile '{profile_name}' does not exist.")

    def get_statistics_path(self):
        statistics_path = os.path.join(
                os.path.dirname(__file__),
                "..", "config", "statistics.json"
                )
        return statistics_path

    def read_statistics(self):
        stats_path = self.get_statistics_path()
        if not os.path.exists(stats_path):
            empty_stats = {
                    "tun_bytes_in": 0,
                    "tun_bytes_out": 0,
                    "tcp_bytes_in": 0,
                    "tcp_bytes_out": 0,
                    "tun_packets_in": 0,
                    "tun_packets_out": 0
                    }

            with open(stats_path, "w") as f:
                json.dump(empty_stats, f, indent=4)
            return empty_stats

        with open(stats_path, "r") as f:
            return json.load(f)

    def write_statistics(self, stats):
        stats_path = self.get_statistics_path()
        with open(stats_path, "w") as f:
            json.dump(stats, f, indent=4)


