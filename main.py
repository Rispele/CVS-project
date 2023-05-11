import os

import CVSFileSystemAdapter
import Commands

with open('Test/first.txt', 'w') as f:
    f.truncate()
    f.write('first text')

init = Commands.InitCommand('Test')
init()

add = Commands.AddCommand('Test', '')
add()

commit = Commands.CommitCommand('Test', 'message')
commit()

input()

with open('Test/first.txt', 'w') as f:
    f.truncate()
    f.write('first modified text')

add = Commands.AddCommand('Test', '')
add()

commit = Commands.CommitCommand('Test', 'message1')
commit()

input()

checkout = Commands.CheckoutCommand('Test', 'c5f65f')
checkout()

input()

branch = Commands.BranchCommand('Test', 'text-branch')
branch()

input()

tag = Commands.CreateTagCommand('Test', 'test-tag', 'test-tag')
tag()

input()

checkout = Commands.CheckoutCommand('Test', 'master')
checkout()

# tree_builder = CVSTreeBuilder.CVSTreeBuilder('Test')
# tree_builder.build()
