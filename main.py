import argparse
import logging
import os


def main():
    # Set up logging to use INFO level and a ISO 8601 timestamp format
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%dT%H:%M:%S")

    # Initialize the argument parser and parse the command-line arguments
    args = init_parser()

    # Get the paths for the .env file and the .env example file
    env_file_path = args.env_file
    example_file_path = args.example_file

    # Initialize the .env file if --init flag is provided
    if args.init:
        init_env_file(args)

    # Load the .env file and get the set of keys
    env_keys = get_env_keys(env_file_path)

    # Load the .env example file and get the set of keys
    example_keys = get_env_keys(example_file_path)

    # Check for missing keys in the .env.example file
    missing_keys = get_missing_keys(env_keys, example_keys)
    if missing_keys:
        logging.warning(f"Missing keys in '{example_file_path}': {missing_keys}")

    # Fix missing keys in the .env.example file if --fix flag is provided
    if args.fix:
        fix_missing_keys(env_file_path, example_file_path)

    # Check for empty values in the .env file
    empty_keys = find_empty_keys(env_file_path)
    if empty_keys:
        logging.warning(f"Keys with empty values in '{env_file_path}': {empty_keys}")

def init_parser() -> argparse.ArgumentParser:
    """Initialize the argument parser for the CLI tool."""
    parser = argparse.ArgumentParser(prog="envalidator",
                                     description="A CLI tool to validate .env examples against .env files.")
    parser.add_argument("--env-file", "-e", default=".env",
                        help="Path to the .env file to validate against. Default is .env.")
    parser.add_argument("--example-file", "-x", default=".env.example",
                        help="Path to the .env example file to validate. Default is .env.example.")
    parser.add_argument("--init", "-i", action="store_true",
                        help="Initialize a new .env file based on the keys in the .env.example file.")
    parser.add_argument("--fix", "-f", action="store_true",
                        help="Automatically add missing keys from the .env file to the .env.example file.")
    parser.add_argument("--approve", "-y", action="store_true",
                        help="Automatically approve syncing missing keys without confirmation.")
    args = parser.parse_args()
    return args

def init_env_file(args):
    """Initialize a new .env file based on the keys in the .env.example file."""
    env_file_path = args.env_file
    example_file_path = args.example_file
    if os.path.exists(env_file_path):
        if not args.approve and not confirm_action("The .env file already exists. Do you want to overwrite it?"):
            logging.info("Initialization cancelled by user.")
            return
        logging.info(f"Overwriting existing '{env_file_path}'...")
        example_keys = get_env_keys(example_file_path)
        logging.info(f"Initializing '{env_file_path}' based on keys in '{example_file_path}'...")
        with open(env_file_path, "w") as env_file:
            for key in example_keys:
                env_file.write(f"{key}=\n")
        logging.info(f"Initialized '{env_file_path}' with keys from '{example_file_path}'.")
        return

def get_env_keys(file_path):
    """Load a .env file and return a set of keys."""
    keys = set()
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                key = line.split("=", 1)[0].strip()
                keys.add(key)
    return keys

def get_missing_keys(source_keys, target_keys):
    """Return a set of keys that are in source_keys but not in target_keys."""
    return source_keys - target_keys

def fix_missing_keys(env_file_path, example_file_path):
    """Add missing keys from the .env file to the .env.example file."""
    env_keys = get_env_keys(env_file_path)
    example_keys = get_env_keys(example_file_path)

    missing_keys = get_missing_keys(env_keys, example_keys)
    if not missing_keys:
        logging.info("No missing keys to add.")
        return

    with open(example_file_path, "a") as example_file:
        example_file.write("\n# Added by envalidator\n")
        for key in missing_keys:
            example_file.write(f"{key}=\n")
            logging.info(f"Added missing key '{key}' to '{example_file_path}'.")

def find_empty_keys(file_path):
    """Find keys in a .env file that have empty values."""
    empty_keys = set()
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if not value:
                    empty_keys.add(key)
    return empty_keys

def confirm_action(message="Do you want to sync missing keys?"):
    while True:
        choice = input(f"{message} [y/N]: ").lower().strip()
        if choice in ('y', 'yes'):
            return True
        if choice in ('n', 'no', ''): # Default to No if they just hit Enter
            return False
        print("Please enter 'y' or 'n'.")

if __name__ == "__main__":
    main()
