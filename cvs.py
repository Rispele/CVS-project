import os

import CVSFileSystemAdapter
import Commands
from CVSBranchProcessor import CVSBranchProcessor
from CVSFileSystemAdapter import CVSFileSystemAdapter


def extract_message(command):
    message_start = command.index('\'') + 1
    message_end = (command[message_start:]).index('\'') + message_start
    return command[message_start:message_end]

current_path = str(os.getcwd())
branch_processor = CVSBranchProcessor(current_path)
files = CVSFileSystemAdapter(current_path)

while True:
    command = str(input()).lstrip().rstrip()
    command_tokens = command.split()
    if len(command_tokens) == 0:
        continue


    #current_path = 'C:\\Users\\Ilya\\Desktop\\Новая папка (3)\\Новая папка'
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
        if command_tokens[1] == 'show':
            branch_list = list(branch_processor.get_branch_list())
            if len(branch_list) == 0:
                print("No branches found")
            else:
                for branch in branch_list:
                    print(branch)
        branch = Commands.BranchCommand(current_path, command_tokens[1])
        branch()
    elif command_tokens[0] == 'tag':
        if len(command_tokens) == 2 and command_tokens[1] == 'show':
            tag_paths = files.get_all_filepaths(
                os.path.join('.cvs', 'refs', 'tags'),
                False)
            tags = []
            for path in tag_paths:
                tags.append(os.path.split(path)[-1])
            if len(tags) == 0:
                print("No tags found")
            else:
                for tag in tags:
                    print(tag)
        elif len(command_tokens) == 1:
            tag_name = command_tokens[1]
            message = extract_message(command)
            tag = Commands.CreateTagCommand(current_path, tag_name, message)
            tag()
        else:
            print(f'Unknown parameter \'{command_tokens[1]}\'')
    else:
        print(f'>> Unknown command {command_tokens[0]}')
        continue



# with open('Test/first.txt', 'w') as f:
#     f.truncate()
#     f.write('first text')

# init = Commands.InitCommand('Test')
# init()
#
# add = Commands.AddCommand('Test', '')
# add()
#
# commit = Commands.CommitCommand('Test', 'message')
# commit()
#
# input()
#
# with open('Test/first.txt', 'w') as f:
#     f.truncate()
#     f.write('first modified text')
#
# add = Commands.AddCommand('Test', '')
# add()
#
# commit = Commands.CommitCommand('Test', 'message1')
# commit()
#
# input()
#
# checkout = Commands.CheckoutCommand('Test', 'c5f65f')
# checkout()
#
# input()
#
# branch = Commands.BranchCommand('Test', 'text-branch')
# branch()
#
# input()
#
# tag = Commands.CreateTagCommand('Test', 'test-tag', 'test-tag')
# tag()
#
# input()
#
# checkout = Commands.CheckoutCommand('Test', 'master')
# checkout()
#
# # tree_builder = CVSTreeBuilder.CVSTreeBuilder('Test')
# # tree_builder.build()
