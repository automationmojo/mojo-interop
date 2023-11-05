
import os

from mojo.xmods.landscaping.landscapeparameters import LandscapeActivationParams
from mojo.xmods.landscaping.landscape import startup_landscape

from mojo.collections.context import Context
from mojo.collections.contextpaths import ContextPaths

def landscape_example_main():

    output_dir = os.path.expanduser("~/mjr/results/examples/landscaping")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    config_dir = os.path.expanduser("~/mjr/config")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    landscapes_dir = os.path.join(config_dir, "landscapes")
    if not os.path.exists(landscapes_dir):
        os.makedirs(landscapes_dir)

    credential_files = [
        os.path.join(config_dir, "credentials.yaml")
    ]

    landscape_files = [
        os.path.join(landscapes_dir, "default-landscape.yaml")
    ]

    ctx = Context()
    ctx.insert(ContextPaths.CONFIG_CREDENTIAL_FILES, credential_files)
    ctx.insert(ContextPaths.CONFIG_LANDSCAPE_FILES, landscape_files)
    ctx.insert(ContextPaths.OUTPUT_DIRECTORY, output_dir)

    activation_params = LandscapeActivationParams(allow_unknown_devices=True, allow_unknown_services=True)

    lscape = startup_landscape(activation_params=activation_params)

    all_devices = lscape.get_devices()

    for dev in all_devices:
        print(f"{dev}")

    all_services = lscape.get_services()

    for svc in all_services:
        print(f"{svc}")


    return

if __name__ == "__main__":
    landscape_example_main()
