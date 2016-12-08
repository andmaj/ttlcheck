import yaml
import os.path
from Common.LoggingManagement import get_logger

configuration_file = "configuration.yaml"
maximum_folder_depth = 5

config = None


def get_configuration():
    global config

    if config is not None:
        return config

    logger = get_logger(__name__)
    logger.info("Loading configuration: %s", configuration_file)

    location = "./"
    for i in range(maximum_folder_depth):
        guessed_path = location + configuration_file
        if os.path.isfile(guessed_path):
            break
        elif i == maximum_folder_depth - 1:
            logger.error("No configuration file found!")
            return None
        else:
            location += "../"

    try:
        with open(location + configuration_file, "r") as f:
            loaded_config = yaml.load(f)
    except:
        logger.error("Loading configuration failed!")
        return None

    logger.info("Configuration file loaded: %s",
                (location + configuration_file))

    config = loaded_config
    return config
