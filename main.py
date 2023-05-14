import os

import CVSFileSystemAdapter
import Commands

def extract_message(command):
    message_start = command.index('\'') + 1
    message_end = (command[message_start:]).index('\'') + message_start
    return command[message_start:message_end]

while True:
    command = str(input()).lstrip()
    command_tokens = command.split()
    if len(command_tokens) == 0:
        continue


    current_path = str(os.getcwd())
    #current_path = 'C:\\Users\\Ilya\\Desktop\\Новая папка (3)\\Новая папка'
    if command_tokens[0] == 'init':
        init = Commands.InitCommand(current_path)
        init()
    elif command_tokens[0] == 'add':
        if len(command_tokens) >= 3:
            print('Command \'add\' must have 0 or 1 argument only')
            continue
        add = Commands.AddCommand(current_path, '')
        if len(command_tokens) == 2:
            add = Commands.AddCommand(current_path, command_tokens[1])
        add()
    elif command_tokens[0] == 'commit':
        message = extract_message(command)
        commit = Commands.CommitCommand(current_path, message)
        commit()
    elif command_tokens[0] == 'checkout':
        to = command_tokens[1]  #'c5f65f' #'master'
        checkout = Commands.CheckoutCommand(current_path, to)
        checkout()
    elif command_tokens[0] == 'branch':
        branch = Commands.BranchCommand(current_path, command_tokens[1])
        branch()
    elif command_tokens[0] == 'tag':
        tag_name = command_tokens[1]
        message = extract_message(command)
        tag = Commands.CreateTagCommand(current_path, tag_name, message)
        tag()
    else:
        print(f'Unknown command {command_tokens[0]}')
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
