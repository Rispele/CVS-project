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


def show_help(command_tokens):
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


def ExecuteInitCommand(command_tokens, current_path):
    if len(command_tokens) > 1:
        print('>> Command \'init\' must have no arguments')
        return
    init = Commands.InitCommand(current_path)
    init()


def ExecuteAddCommand(command_tokens, current_path):
    if len(command_tokens) > 2:
        print('>> Command \'add\' must have 0 or 1 argument only')
        return
    add = Commands.AddCommand(current_path, '')
    if len(command_tokens) == 2:
        add = Commands.AddCommand(current_path, command_tokens[1])
    add()


def ExecuteCommitCommand(command_tokens, current_path, command):
    if len(command_tokens) > 2:
        print('>> Command \'commit\' must have 0 or 1 argument only')
        return
    elif len(command_tokens) == 1:
        commit = Commands.CommitCommand(current_path, '')
        commit()
    elif ' \'' in command and command[-1] == '\'':
        message = extract_message(command)
        if message is None:
            return
        commit = Commands.CommitCommand(current_path, message)
        commit()
    elif command_tokens[1] == 'show':
        with open(os.path.join(current_path, '.cvs', 'COMMITLOG'), 'r') as f:
            text = f.read().split('\n')
            for line in text:
                if '-- message' in line or '->' in line:
                    print(line)
    else:
        print(f'>> Unknown parameter \'{command_tokens[1]}\'')


def ExecuteCheckoutCommand(command_tokens, current_path):
    if len(command_tokens) != 2:
        print('>> Command \'checkout\' must have 1 argument (destination)')
        return
    to = command_tokens[1]
    checkout = Commands.CheckoutCommand(current_path, to)
    checkout()


def ExecuteBranchCommand(command_tokens, current_path, branch_processor):
    if len(command_tokens) > 3 or len(command_tokens) < 2:
        print(
            '>> Command \'branch\' must have 1 argument '
            '(branch name) or (show)\n'
            '>> or 2 arguments (delete) (branch name)')
        return
    if command_tokens[1] == 'show':
        branch_list = list(branch_processor.get_branch_list())
        if len(branch_list) == 0:
            print("No branches found")
        else:
            for branch in branch_list:
                print(branch)
        return
    elif command_tokens[1] == 'delete':
        branch = Commands.BranchCommand(current_path, command_tokens[2])
        branch.remove_branch()
        return
    branch = Commands.BranchCommand(current_path, command_tokens[1])
    branch()


def ExecuteTagCommand(command_tokens, current_path, command, files):
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
        return
    elif command_tokens[1] == 'delete':
        tag_name = command_tokens[2]
        Commands.CreateTagCommand(current_path, tag_name, '').remove_tag()
        print(f'>> Tag {tag_name} was successfully deleted  ')
        return
    elif len(command_tokens) != 3:
        print('>> Tag creation command receive 2 params '
              '(tag \'name\' \'message\')')
    tag_name = command_tokens[1]
    message = extract_message(command)
    if message is None:
        return
    tag = Commands.CreateTagCommand(current_path, tag_name, message)
    tag()


def TryExecuteCommand(command, current_path):
    branch_processor = CVSBranchProcessor(current_path)
    files = CVSFileSystemAdapter(current_path)
    command_tokens = command.split()
    if len(command_tokens) == 0:
        return
    if len(command_tokens) > 1 and command_tokens[1] == 'help':
        show_help(command_tokens)
        return
    if command_tokens[0] == 'init':
        ExecuteInitCommand(command_tokens, current_path)
    elif command_tokens[0] == 'add':
        ExecuteAddCommand(command_tokens, current_path)
    elif command_tokens[0] == 'commit':
        ExecuteCommitCommand(command_tokens, current_path, command)
    elif command_tokens[0] == 'checkout':
        ExecuteCheckoutCommand(command_tokens, current_path)
    elif command_tokens[0] == 'branch':
        ExecuteBranchCommand(command_tokens,
                             current_path, branch_processor)
    elif command_tokens[0] == 'tag':
        ExecuteTagCommand(command_tokens, current_path, command, files)
    else:
        print(f'>> Unknown command {command_tokens[0]}')
        return


def main():
    current_path = str(os.getcwd())
    while True:
        command = str(input()).lstrip().rstrip()
        TryExecuteCommand(command, current_path)


if __name__ == "__main__":
    main()
