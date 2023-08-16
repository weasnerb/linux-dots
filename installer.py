import argparse
from pathlib import Path

USER_HOME_DIR=Path.home()
SRC_DIR=Path.cwd().joinpath('src')

def main():
    """
    Entrypoint in installer.py
    aka. The root function
    """
    cli_app = setupCli()
    args = cli_app.parse_args()
    
    if len(vars(args)) == 0:
        cli_app.print_help()
    else:
        args.func(args)

def setupCli():
    """
    Setup the Cli Structure and Argument Parsers
    """
    parser = argparse.ArgumentParser(prog='Dot Installer', description='Linux Dot/Config file installer for weasnerb/linux-dots.')
    
    subparser = parser.add_subparsers(title='Actions')
    subparser.add_parser('install', help='Install Dot Files.').set_defaults(func=install)
    subparser.add_parser('uninstall', help='Uninstall Dot Files.').set_defaults(func=uninstall)
    
    return parser

def install(args):
    """
    Main process for installing dot configs
    """
    configs = get_dot_configs_in_path(SRC_DIR)
    for src_config_path in configs:
        config_path_relative_to_src = src_config_path.relative_to(SRC_DIR)
        if prompt_y_n(f"Install {config_path_relative_to_src}?"):
            installed_config_path = USER_HOME_DIR.joinpath(config_path_relative_to_src)
            backup_config(installed_config_path)
            install_config(src_config_path, installed_config_path)
            print(f"Done")

def uninstall(args):
    """
    Main process for uninstalling dot configs

    Note: This way of uninstalling is flawed.
    Why? Well, if we ever delete/remove a config from this repo we won't ask to uninstall it as it won't be in the src folder.
    That means that the stuff we deleted from this repo will break the symbolic link we created during install, but the symbolic link won't be deleted.
    """
    configs = get_dot_configs_in_path(SRC_DIR)
    for src_config_path in configs:
        config_path_relative_to_src = src_config_path.relative_to(SRC_DIR)
        installed_config_path = USER_HOME_DIR.joinpath(config_path_relative_to_src)
        if is_config_installed(installed_config_path) and prompt_y_n(f"Uninstall {config_path_relative_to_src}?"):
            uninstall_config(installed_config_path)
            restore_backup_config(installed_config_path)
            print(f"Done")

def backup_config(config_path):
    # Check if config already exists, if so move to path.bak
    if config_path.exists():
        backup_path = get_backup_config_path(config_path)
        # Recursive check if path.bak already exists, if so move path.bak to path.bak.bak
        if backup_path.exists():
            backup_config(backup_path)
        print(f"Backing up {str(config_path)} to {str(backup_path)}")
        config_path.rename(backup_path)

def restore_backup_config(config_path):
    if config_path.exists():
        print(f"Cannot Restore Backup for {str(config_path)} because {str(config_path)} currently exists.")
        return
    backup_path = get_backup_config_path(config_path)
    if backup_path.exists():
        print(f"Restoring backup from {str(backup_path)} to {str(config_path)}")
        backup_path.rename(config_path)
        # Recursive check if path.bak.bak exists, if so move path.bak.bak to path.bak
        if get_backup_config_path(backup_path).exists():
            restore_backup_config(backup_path)
        
def get_backup_config_path(config_path):
    BACKUP_SUFFIX = '.bak'
    return config_path.with_suffix(config_path.suffix + BACKUP_SUFFIX)

def install_config(src_config_path, installed_config_path):
    print(f"Installing {str(src_config_path.relative_to(SRC_DIR))}")
    installed_config_path.symlink_to(src_config_path)

def is_config_installed(installed_config_path):
    return installed_config_path.exists() and installed_config_path.is_symlink()

def uninstall_config(installed_config_path):
    if is_config_installed(installed_config_path):
        print(f"Deleting {str(installed_config_path)}")
        installed_config_path.unlink()

def get_dot_configs_in_path(dir_to_search):
    """
    Return a list of dot/config paths within the dir provided
    """
    dot_configs_in_path = []

    dirs = dir_to_search.iterdir()
    for dir in dirs:
        if is_dot_file(dir):
            dot_configs_in_path.append(dir)
        elif dir.is_dir():
            dot_configs_in_path.extend(get_dot_configs_in_path(dir))
    
    return dot_configs_in_path


def is_dot_file(path_to_check):
    """
    Check if a file is a dot/config file/folder.

    Will Return true if path is a file path and file starts with a `.`
    OR if the path is a file/folder who's parent folder starts with a `.`
    """
    return (path_to_check.is_file() and str(path_to_check.name)[0] == '.') or (str(path_to_check.parent.name)[0] == '.')

def prompt_y_n(question):
    """
    Prompt user with the provided question.

    IF user inputs 'y', 'Y', 'yes', 'Yes', 'YES', etc. return True
    IF user inputs 'n', 'N', 'no', 'No', or 'NO' return False
    Continue until user inputs a valid value
    """
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
    # Swallow Error, as we don't want to display the python error in console.
    # Can't have empty except clause, so just print an empty line.
    print()
