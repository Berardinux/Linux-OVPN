import json
import os
from cryptography.fernet import Fernet
from error import ErrorCheck

class ReadWriteJSON:
    def __init__(self):
        key = os.environ.get("OVPN_SECRET_KEY")

        if not key:
            key_path = "/opt/LinuxOVPN/docs/secret.key"
            
            if os.path.exists(key_path):
                with open(key_path, "rb") as f:
                    key = f.read()
            else:
                os.makedirs(os.path.dirname(key_path), exist_ok=True)
                key = Fernet.generate_key()
                with open(key_path, "wb") as f:
                    f.write(key)
                os.chmod(key_path, 0o600)
                print(f"Created a new secret key at {key_path}. Keep this file safe!")

        self.fernet = Fernet(key)

    def encrypt_string(self, plaintext):
        if plaintext is None or plaintext == "":
            return ""
        token = self.fernet.encrypt(plaintext.encode())
        return token.decode()

    def decrypt_string(self, encrypted_str):
        if encrypted_str is None or encrypted_str == "":
            return ""
        decrypted = self.fernet.decrypt(encrypted_str.encode())
        return decrypted.decode()

    def get_config_path(self):
        config_path = os.path.join(
            os.path.dirname(__file__),
            "..", "config", "config.json"
        )

        ErrorCheck().error_check_for_loading_config(config_path)
        return config_path

    def read_config(self):
        config_path = self.get_config_path()

        with open(config_path, "r") as f:
            config = json.load(f)

        if "profiles" in config:
            for profile_data in config["profiles"].values():
                encrypted_pw = profile_data.get("passwd", "")
                if encrypted_pw:
                    try:
                        decrypted_pw = self.decrypt_string(encrypted_pw)
                        profile_data["passwd"] = decrypted_pw
                    except Exception as e:
                        print(f"[WARNING] Could not decrypt password for a profile: {e}")
                        profile_data["passwd"] = ""

        return config

    def write_config(self, config):
        if "profiles" in config:
            for profile_data in config["profiles"].values():
                plain_pw = profile_data.get("passwd", "")
                if plain_pw:
                    profile_data["passwd"] = self.encrypt_string(plain_pw)

        config_path = self.get_config_path()
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)

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

            config["profiles"][new_profile_name] = profile_data

            self.write_config(config)
            print(f"Profile renamed from '{old_profile_name}' to '{new_profile_name}' and updated.")

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
