from unittest import TestCase, main
from shutil import rmtree
import os

from CVSBranchProcessor import CVSBranchProcessor
from CVSFileSystemAdapter import CVSFileSystemAdapter
from Commands import InitCommand, AddCommand, CommitCommand, CheckoutCommand, \
    BranchCommand, CreateTagCommand
from cvs import ExecuteInitCommand, ExecuteAddCommand, ExecuteCommitCommand, \
    ExecuteCheckoutCommand,\
    ExecuteBranchCommand, ExecuteTagCommand, show_help


def clear_repo(self):
    if (os.path.isdir(os.path.join(self._test_folder, '.cvs'))):
        rmtree(os.path.join(self._test_folder, '.cvs'))
    if (os.path.isdir(os.path.join(self._test_folder, 'folder'))):
        rmtree(os.path.join(self._test_folder, 'folder'))
    if (os.path.isfile(os.path.join(self._test_folder, 'file2.txt'))):
        os.remove(os.path.join(self._test_folder, 'file2.txt'))


def build_repo(self):
    os.mkdir(os.path.join(self._test_folder, 'folder'))
    with open(
            os.path.join(self._test_folder, 'folder', 'file1.txt'), 'w') as f:
        f.write('content1')
    with open(os.path.join(self._test_folder, 'file2.txt'), 'w') as f:
        f.write('content2')


def get_file_content(file_location):
    file = open(file_location, 'r')
    content = file.read()
    file.close()
    return content


class TestCommands(TestCase):
    def setUp(self):
        self._test_folder = \
            os.path.join(str(os.getcwd()), 'tests', 'test_repo')

    def test_init(self):
        clear_repo(self)

        init = InitCommand(self._test_folder)
        init()
        self.assertEqual(
            os.path.isdir(os.path.join(self._test_folder, '.cvs')),
            True)
        self.assertEqual(
            os.path.isdir(os.path.join(self._test_folder, '.cvs', 'objects')),
            True)
        self.assertEqual(
            os.path.isdir(os.path.join(self._test_folder, '.cvs', 'refs')),
            True)
        self.assertEqual(
            os.path.isdir(
                os.path.join(self._test_folder, '.cvs', 'refs', 'heads')),
            True)
        self.assertEqual(
            os.path.isdir(
                os.path.join(self._test_folder, '.cvs', 'refs', 'tags')),
            True)
        self.assertEqual(
            os.path.isfile(os.path.join(self._test_folder, '.cvs', 'HEAD')),
            True)
        self.assertEqual(
            os.path.isfile(os.path.join(self._test_folder, '.cvs', 'LOG')),
            True)
        self.assertEqual(
            os.path.isfile(
                os.path.join(self._test_folder, '.cvs', 'COMMITLOG')),
            True)

        self.assertEqual(
            get_file_content(os.path.join(self._test_folder, '.cvs', 'HEAD')),
            'ref: refs/heads/master')
        self.assertEqual(len(get_file_content(
            os.path.join(self._test_folder, '.cvs', 'LOG'))) > 0, True)
        self.assertEqual(get_file_content(
            os.path.join(self._test_folder, '.cvs', 'COMMITLOG')),
            'Project commits:\n')

    def test_add(self):
        clear_repo(self)
        build_repo(self)

        InitCommand(self._test_folder)()
        AddCommand(self._test_folder, '')()

        content = get_file_content(
            os.path.join(self._test_folder, '.cvs', 'LOG'))
        print(content)
        self.assertEqual(content.count('file1.txt'), 1)
        self.assertEqual(content.count('file2.txt'), 1)
        self.assertEqual(content.count(os.path.join('folder', 'file1.txt')), 1)
        self.assertEqual(os.path.isfile(
            os.path.join(self._test_folder, '.cvs', 'index')),
                         True)
        self.assertEqual(len([p for p in os.walk(
            os.path.join(self._test_folder, '.cvs', 'objects'))]), 3)

    def test_commit(self):
        clear_repo(self)
        build_repo(self)

        InitCommand(self._test_folder)()
        AddCommand(self._test_folder, '')()
        CommitCommand(self._test_folder, '')()

        content = get_file_content(
            os.path.join(self._test_folder, '.cvs', 'index'))
        self.assertEqual(content.count('file1.txt'), 1)
        self.assertEqual(content.count('file2.txt'), 1)
        self.assertEqual(content.count(os.path.join('folder', 'file1.txt')), 1)
        content = get_file_content(
            os.path.join(self._test_folder, '.cvs', 'COMMITLOG'))
        self.assertEqual(content.count('added'), 2)
        self.assertEqual(content.count('file1.txt'), 2)
        self.assertEqual(content.count('file2.txt'), 2)
        self.assertEqual(content.count(os.path.join('folder', 'file1.txt')), 2)

    def test_checkout_to_commit(self):
        clear_repo(self)
        build_repo(self)

        InitCommand(self._test_folder)()
        AddCommand(self._test_folder, '')()
        CommitCommand(self._test_folder, '')()

        with open(os.path.join(
                self._test_folder, '.cvs', 'refs', 'heads', 'master')) as f:
            commit_hash1 = f.read()[:6]

        with open(os.path.join(self._test_folder, '.cvs', 'index')) as f:
            file_hash1 = f.read().split('\n')[0][-40:][:6]

        with open(os.path.join(self._test_folder, 'file2.txt'), 'w') as f:
            f.write('edited content2')
        AddCommand(self._test_folder, '')()
        CommitCommand(self._test_folder, '')()
        edited_file_hash = get_file_content(os.path.join(
            self._test_folder, '.cvs', 'index')).split('\n')[0][-40:]

        CheckoutCommand(self._test_folder, commit_hash1)()
        file_hash_after_checkout = get_file_content(os.path.join(
            self._test_folder, '.cvs', 'index')).split('\n')[0][-40:]

        self.assertEqual(file_hash1 in file_hash_after_checkout, True)
        self.assertEqual(file_hash_after_checkout != edited_file_hash, True)

    def test_branch(self):
        clear_repo(self)
        build_repo(self)

        InitCommand(self._test_folder)()
        AddCommand(self._test_folder, '')()
        CommitCommand(self._test_folder, '')()
        BranchCommand(self._test_folder, 'newbranch')()

        self.assertEqual(os.path.isfile(os.path.join(
            self._test_folder, '.cvs', 'refs', 'heads', 'newbranch')), True)

        last_commit_on_new_branch = get_file_content(os.path.join(
            self._test_folder, '.cvs', 'refs', 'heads', 'newbranch'))
        last_commit_on_master = get_file_content(
            os.path.join(self._test_folder, '.cvs', 'refs', 'heads', 'master'))
        self.assertEqual(
            last_commit_on_master == last_commit_on_new_branch, True)

        CheckoutCommand(self._test_folder, 'newbranch')()

        with open(os.path.join(self._test_folder, 'file2.txt'), 'w') as f:
            f.write('edited content2')

        AddCommand(self._test_folder, '')()
        CommitCommand(self._test_folder, '')()

        last_commit_on_new_branch = get_file_content(os.path.join(
            self._test_folder, '.cvs', 'refs', 'heads', 'newbranch'))
        last_commit_on_master = get_file_content(os.path.join(
            self._test_folder, '.cvs', 'refs', 'heads', 'master'))

        self.assertEqual(
            last_commit_on_master == last_commit_on_new_branch, False)

    def test_simple_scenario(self):
        clear_repo(self)
        build_repo(self)

        ExecuteInitCommand('init'.split(), self._test_folder)
        ExecuteAddCommand('add'.split(), self._test_folder)
        ExecuteCommitCommand('commit \'files\''.split(),
                             self._test_folder, 'commit \'files\'')
        ExecuteCommitCommand('commit show'.split(),
                             self._test_folder, 'commit show')
        ExecuteBranchCommand('branch newBranch'.split(),
                             self._test_folder,
                             CVSBranchProcessor(self._test_folder))
        self.assertEqual(os.path.isfile(os.path.join(
            self._test_folder, '.cvs', 'refs', 'heads', 'newBranch')), True)
        ExecuteBranchCommand('branch show'.split(),
                             self._test_folder,
                             CVSBranchProcessor(self._test_folder))
        ExecuteCheckoutCommand('checkout newBranch'.split(),
                               self._test_folder)
        ExecuteTagCommand('tag tag \'tagged\''.split(),
                          self._test_folder,
                          'tag tag \'tagged\'',
                          CVSFileSystemAdapter(self._test_folder))
        self.assertEqual(os.path.isfile(os.path.join(
            self._test_folder, '.cvs', 'refs', 'tags', 'tag')), True)
        ExecuteTagCommand('tag show'.split(),
                          self._test_folder,
                          'tag show',
                          CVSFileSystemAdapter(self._test_folder))
        ExecuteTagCommand('tag delete tag'.split(),
                          self._test_folder,
                          'tag delete tag',
                          CVSFileSystemAdapter(self._test_folder))
        self.assertEqual(os.path.isfile(os.path.join(
            self._test_folder, '.cvs', 'refs', 'tags', 'tag')), False)
        show_help('help tag'.split())


if __name__ == "__main__":
    main()
