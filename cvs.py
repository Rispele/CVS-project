import os

import Commands
from CVSBranchProcessor import CVSBranchProcessor
from CVSFileSystemAdapter import CVSFileSystemAdapter


def extract_message(command):
    if command.find('\'') == -1:
        print(">> Message should be rounded with \' (example: \'message\')")
        return None
    message_start = command.index('\'') + 1
    message_end = (command[message_start:]).index('\'') + message_start
    return command[message_start:message_end]

def show_help(command):
    if command_tokens[0] == 'init':
        Commands.InitCommand.print_help()
    elif command_tokens[0] == 'add':
        Commands.AddCommand.print_help()
    elif command_tokens[0] == 'commit':
        Commands.CommitCommand.print_help()
    elif command_tokens[0] == 'branch':
        Commands.BranchCommand.print_help()
    elif command_tokens[0] == 'tag':
        Commands.CreateTagCommand.print_help()
    else:
        print(f'>> Unknown command {command_tokens[0]}')


current_path = str(os.getcwd())
branch_processor = CVSBranchProcessor(current_path)
files = CVSFileSystemAdapter(current_path)

while True:
    command = str(input()).lstrip().rstrip()
    command_tokens = command.split()
    if len(command_tokens) == 0:
        continue

    if len(command_tokens) > 1 and command_tokens[1] == 'help':
        show_help(command_tokens[0])
        continue

    if command_tokens[0] == 'init':
        if len(command_tokens) > 1:
            print('>> Command \'init\' must have no arguments')
            continue
        init = Commands.InitCommand(current_path)
        init()
    elif command_tokens[0] == 'add':
        if len(command_tokens) > 2:
            print('>> Command \'add\' must have 0 or 1 argument only')
            continue
        add = Commands.AddCommand(current_path, '')
        if len(command_tokens) == 2:
            add = Commands.AddCommand(current_path, command_tokens[1])
        add()
    elif command_tokens[0] == 'commit':
        if len(command_tokens) > 2:
            print('>> Command \'commit\' must have 0 or 1 argument only')
            continue
        elif len(command_tokens) == 1:
            commit = Commands.CommitCommand(current_path, '')
            commit()
        elif ' \'' in command and command[-1] == '\'':
            message = extract_message(command)
            if message is None:
                continue
            commit = Commands.CommitCommand(current_path, message)
            commit()
        elif command_tokens[1] == 'show':
            with open(current_path + '\\.cvs\\COMMITLOG', 'r') as f:
                text = f.read().split('\n')
                for line in text:
                    if '-- message' in line or '->' in line:
                        print(line)
        else:
            print(f'>> Unknown parameter \'{command_tokens[1]}\'')
    elif command_tokens[0] == 'checkout':
        if len(command_tokens) != 2:
            print('>> Command \'checkout\' must have 1 argument (destination)')
            continue
        to = command_tokens[1]
        checkout = Commands.CheckoutCommand(current_path, to)
        checkout()
    elif command_tokens[0] == 'branch':
        if len(command_tokens) > 3 or len(command_tokens) < 2:
            print(
                '>> Command \'branch\' must have 1 argument '
                '(branch name) or (show)\n'
                '>> or 2 arguments (delete) (branch name)')
            continue
        if command_tokens[1] == 'show':
            branch_list = list(branch_processor.get_branch_list())
            if len(branch_list) == 0:
                print("No branches found")
            else:
                for branch in branch_list:
                    print(branch)
            continue
        elif command_tokens[1] == 'delete':
            branch = Commands.BranchCommand(current_path, command_tokens[2])
            branch.remove_branch()
            continue
        branch = Commands.BranchCommand(current_path, command_tokens[1])
        branch()
    elif command_tokens[0] == 'tag':
        if command_tokens[1] == 'show':
            tag_paths = files.get_all_filepaths(
                os.path.join('.cvs', 'refs', 'tags'),
                False)
            tags = []
            for path in tag_paths:
                tag_hash, message = files.read_file(path).split()
                tags.append((os.path.split(path)[-1], message))
            if len(tags) == 0:
                print(">> No tags found")
            else:
                for tag in tags:
                    print(f'{tag[0]} message: \'{tag[1]}\'')
            continue
        elif command_tokens[1] == 'delete':
            tag_name = command_tokens[2]
            Commands.CreateTagCommand(current_path, tag_name, '').remove_tag()
            print(f'>> Tag {tag_name} was successfully deleted  ')
            continue
        elif len(command_tokens) != 3:
            print('>> Tag creation command receive 2 params '
                  '(tag \'name\' \'message\')')
        tag_name = command_tokens[1]
        message = extract_message(command)
        if message is None:
            continue
        tag = Commands.CreateTagCommand(current_path, tag_name, message)
        tag()
    else:
        print(f'>> Unknown command {command_tokens[0]}')
        continue
