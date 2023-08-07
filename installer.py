import argparse


parser = argparse.ArgumentParser(prog='Dot Installer', description='Linux Dot/Config file installer for weasnerb/linux-dots.')


def main():
    setupCli()
    args = parser.parse_args()
    
    if (len(vars(args)) == 0):
        parser.print_help()
    else:
        args.func(args)

def setupCli():
    subparser = parser.add_subparsers(title='Actions')
    subparser.add_parser('install', help='Install Dot Files.').set_defaults(func=install)
    subparser.add_parser('uninstall', help='Uninstall Dot Files.').set_defaults(func=uninstall)

def install(args):
    print('Do the installing here!')
    
def uninstall(args):
    print('Do the Uninstalling Here!')

# Run Main
main()
