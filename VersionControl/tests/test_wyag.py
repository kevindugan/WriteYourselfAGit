import pytest
from VersionControl import WyagLib
import os

def test_init_command(tmpdir):
    
    myGit = WyagLib.wyag()
    myGit.run(['init', os.path.join(tmpdir, "myTest")])

    assert os.path.isfile(os.path.join(tmpdir, "myTest", ".git", "HEAD"))
    with open(os.path.join(tmpdir, "myTest", ".git", "HEAD")) as f:
        assert f.read().strip() == "ref: refs/heads/master"

def test_blob_objects(tmpdir, capsys):
    
    myGit = WyagLib.wyag()
    myGit.run(['init', os.path.join(tmpdir, "myTest")])

    # Create file
    contents = "blah blah\n\nblah\nblahblahbla\n\n"
    filePath = os.path.join(tmpdir, "myTest", "dir1", "testFile.txt")
    os.makedirs(os.path.dirname(filePath))
    with open(filePath, "w") as f:
        f.write(contents)

    # Hash without writing
    expected_hash = '50067d0b090dc8bec4e78788eb7db8025092b6e0'
    myGit.run(['hash-object', filePath])
    captured = capsys.readouterr()
    assert captured.out.strip() == expected_hash

    assert not os.path.isfile(os.path.join(tmpdir, "myTest", ".git", "objects", expected_hash[0:2], expected_hash[2:]))

    # Hash and write file
    myGit.run(['hash-object', '-w', filePath])
    captured = capsys.readouterr()
    assert captured.out.strip() == expected_hash

    assert os.path.isfile(os.path.join(tmpdir, "myTest", ".git", "objects", expected_hash[0:2], expected_hash[2:]))

    # Get contents of file
    os.chdir(os.path.join(tmpdir, "myTest"))
    myGit.run(['cat-file', expected_hash])
    captured = capsys.readouterr()
    assert captured.out == contents
