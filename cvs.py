import os
import CVSFileSystemAdapter
import Commands

def extract_message(command):
    message_start = command.index('\'') + 1
    message_end = (command[message_start:]).index('\'') + message_start
    return command[message_start:message_end]

while True:
    command = str(input()).lstrip().rstrip()
    command_tokens = command.split()
    if len(command_tokens) == 0:
        continue

    current_path = str(os.getcwd())
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
        if len(command_tokens) != 2:
            print('>> Command \'branch\' must have 1 argument (branch name)')
            continue
        branch = Commands.BranchCommand(current_path, command_tokens[1])
        branch()
    elif command_tokens[0] == 'tag':
        tag_name = command_tokens[1]
        message = extract_message(command)
        tag = Commands.CreateTagCommand(current_path, tag_name, message)
        tag()
    else:
        print(f'>> Unknown command {command_tokens[0]}')
        continue