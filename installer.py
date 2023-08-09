import argparse
from pathlib import Path

INSTALL_DIR=Path.home().joinpath('.config')
CURRENT_DIR=Path.cwd()

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
    dirs = CURRENT_DIR.iterdir()
    for dir in dirs:
        if dir.is_dir():
            if prompt_y_n(f"Install {dir.name}?"):
                config_path = Path(INSTALL_DIR).joinpath(dir.name)
                backup_config(config_path)
                install_config(config_path)

def uninstall(args):
    dirs = CURRENT_DIR.iterdir()
    for dir in dirs:
        if dir.is_dir():
            if prompt_y_n(f"Uninstall {dir.name}?"):
                config_path = Path(INSTALL_DIR).joinpath(dir.name)
                uninstall_config(config_path)
                restore_backup_config(config_path)

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


# Run Main
try:
    main()
except KeyboardInterrupt:
    # Do nothing, as we don't want to display error in console.
    print()
