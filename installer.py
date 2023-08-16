import argparse
from pathlib import Path

USER_HOME_DIR=Path.home()
SRC_DIR=Path.cwd().joinpath('src')

parser = argparse.ArgumentParser(prog='Dot Installer', description='Linux Dot/Config file installer for weasnerb/linux-dots.')

def main():
    setupCli()
    args = parser.parse_args()
    
    if len(vars(args)) == 0:
        parser.print_help()
    else:
        args.func(args)

def setupCli():
    subparser = parser.add_subparsers(title='Actions')
    subparser.add_parser('install', help='Install Dot Files.').set_defaults(func=install)
    subparser.add_parser('uninstall', help='Uninstall Dot Files.').set_defaults(func=uninstall)

def install(args):
    configs = get_configs_in_path(SRC_DIR)
    for config in configs:
        config_path_relative_to_src = config.relative_to(SRC_DIR)
        if prompt_y_n(f"Install {config_path_relative_to_src}?"):
            config_path = USER_HOME_DIR.joinpath(config_path_relative_to_src)
            backup_config(config_path)
            install_config(config_path)

def uninstall(args):
    configs = get_configs_in_path(SRC_DIR)
    for config in configs:
        config_path_relative_to_src = config.relative_to(SRC_DIR)
        if prompt_y_n(f"Uninstall {config_path_relative_to_src}?"):
            config_path = USER_HOME_DIR.joinpath(config_path_relative_to_src)
            uninstall_config(config_path)
            restore_backup_config(config_path)


def backup_config(config_path):
    # Check if config already exists, if so move to path.bak
    if config_path.exists():
        backup_path = get_backup_config_path(config_path)
        # Recursive check if .bak already exists, if so move path.bak to path.bak.bak
        if backup_path.exists():
            backup_config(backup_path)
        print(f"Backing up {str(config_path)} to {str(backup_path)}")
        # Move existing config to backup_path

def restore_backup_config(config_path):
    backup_path = get_backup_config_path(config_path)
    if backup_path.exists():
        print(f"Restoring backup from {str(backup_path)} to {str(config_path)}")
        # Move existing backup to config_path 
        
def get_backup_config_path(config_path):
    BACKUP_SUFFIX = '.bak'
    return config_path.with_suffix(config_path.suffix + BACKUP_SUFFIX)

def install_config(config_path):
    print(f"Installing {str(config_path)}")

def uninstall_config(config_path):
    if config_path.exists() and config_path.is_symlink():
        print(f"Deleting {str(config_path)}")
        #config_path.unlink()

def get_configs_in_path(dir_to_search):
    configs_in_path = []

    dirs = dir_to_search.iterdir()
    for dir in dirs:
        if is_dot_file(dir):
            configs_in_path.append(dir)
        elif dir.is_dir():
            configs_in_path.extend(get_configs_in_path(dir))
    
    return configs_in_path

# Check if a file is a dot/config file/folder
# Will Return true if path is a file path and file starts with a `.`
# OR if the path is a file/folder who's parent folder starts with a `.`
def is_dot_file(path_to_check):
    return (path_to_check.is_file() and str(path_to_check.name)[0] == '.') or (str(path_to_check.parent.name)[0] == '.')

def prompt_y_n(question):
    while True:
        result = input(question + ' (y/n):\n> ').lower()
        if result in ['y', 'yes']:
            return True
        elif result in ['n', 'no']:
            return False
        else:
            print('Invalid input.')
            continue;

# Run Main
try:
    main()
except KeyboardInterrupt:
    # Do nothing, as we don't want to display error in console.
    # Can't have empty except clause, so just print a new line.
    print()
