# import argparse
# import os
# import sys

# import toml
# import yaml
# import zephyr_module
# from west.commands import WestCommand
# from zephyr_ext_common import ZEPHYR_BASE


# class Autoctx(WestCommand):
#     def __init__(self):
#         super().__init__(
#             'autoctx',
#             'automatically infer devicetree LSP context for Helix',
#             'automatically infer devicetree LSP context for Helix',
#             accepts_unknown_args=True,
#         )


# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("path", type=str)
#     args = parser.parse_args()
#     yaml_path = args.path

#     if not os.path.exists(yaml_path):
#         sys.exit("ERROR: specified path does not exist")

#     if os.path.isdir(yaml_path):
#         yaml_path = find_yaml(yaml_path)
#         if yaml_path is None:
#             sys.exit("ERROR: could not find build_info.yml")

#     lang_toml = toml.load("/home/bex/.config/helix/languages.toml")

#     try:
#         ctx = lang_toml["language-server"]["devicetree_ls"]["config"]["devicetree"]["contexts"]
#     except Exception as e:
#         sys.exit(f"ERROR: {e}. Could not retrieve devicetree context from toml.")

#     with open(yaml_path) as f:
#         yaml_data = yaml.safe_load(f)

#     yaml_dts = yaml_data["cmake"]["devicetree"]
#     yaml_board_dts = yaml_dts["files"][0]
#     yaml_overlay_dts = yaml_dts["user-files"]

#     if not os.path.exists(yaml_board_dts) or not all(os.path.exists(p) for p in yaml_overlay_dts):
#         sys.exit("ERROR: yaml does not point to existing paths")

#     ctx[0]["dtsFile"] = yaml_board_dts
#     ctx[0]["overlays"] = yaml_overlay_dts

#     with open("/home/bex/.config/helix/languages.toml", "w") as f:
#         toml.dump(lang_toml, f)


# def find_yaml(path):
#     path = os.path.join(path, "build_info.yml")
#     return path if os.path.exists(path) else None


# if __name__ == "__main__":
#     main()


import os
import sys
from pathlib import Path


sys.path.append(os.fspath(Path(__file__).parent.parent))
import toml
import yaml
from west.commands import WestCommand
from zephyr_ext_common import ZEPHYR_BASE
import zephyr_module


class Autoctx(WestCommand):
    def __init__(self):
        super().__init__(
            'autoctx',
            'automatically infer devicetree LSP context for Helix',
            'Automatically infer devicetree LSP context for Helix',
            accepts_unknown_args=True,
        )

    def do_add_parser(self, parser_adder):
        parser = parser_adder.add_parser(
            self.name,
            help=self.help,
            description=self.description,
        )
        parser.add_argument(
            'path',
            type=str,
            help='Path to build_info.yml or directory containing it',
        )
        return parser

    def do_run(self, args, unknown_args):
        yaml_path = args.path
        print(yaml_path)

        if not os.path.exists(yaml_path):
            sys.exit("ERROR: specified path does not exist")

        if os.path.isdir(yaml_path):
            yaml_path = self.find_yaml(yaml_path)
            if yaml_path is None:
                sys.exit("ERROR: could not find build_info.yml")

        lang_toml_path = str(Path.home() / ".config/helix/languages.toml")
        lang_toml = toml.load(lang_toml_path)

        try:
            ctx = lang_toml["language-server"]["devicetree_ls"]["config"]["devicetree"]["contexts"]
        except KeyError as e:
            sys.exit(f"ERROR: {e}. Could not retrieve devicetree context from toml.")

        with open(yaml_path) as f:
            yaml_data = yaml.safe_load(f)

        yaml_dts = yaml_data["cmake"]["devicetree"]
        yaml_board_dts = yaml_dts["files"][0]
        yaml_overlay_dts = yaml_dts.get("user-files", [])

        if not os.path.exists(yaml_board_dts) or not all(
            os.path.exists(p) for p in yaml_overlay_dts
        ):
            sys.exit("ERROR: yaml does not point to existing paths")

        ctx[0]["dtsFile"] = yaml_board_dts
        ctx[0]["overlays"] = yaml_overlay_dts

        with open(lang_toml_path, "w") as f:
            toml.dump(lang_toml, f)

        print(f"devicetree context updated from {yaml_path}")

    @staticmethod
    def find_yaml(path):
        path = os.path.join(path, "build/build_info.yml")
        return path if os.path.exists(path) else None
