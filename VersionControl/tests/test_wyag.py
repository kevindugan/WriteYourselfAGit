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

def test_commit_objects(tmpdir, capsys):
    
    myGit = WyagLib.wyag()
    myGit.run(['init', os.path.join(tmpdir, "myTest")])

    # Create file
    contents = "tree 025b46d991b8602e229fa477dbc50a98ee050dcf\n" + \
               "parent a33e731eb4d600b08dcd34fea6fe45cecc7958a0\n" + \
               "parent f4f16ee537a618502fac0f6a0db822ddd3b45b12\n" + \
               "author Kevin Dugan <dugankj@ornl.gov> 1560020798 -0400\n" + \
               "committer GitHub <noreply@github.com> 1560020798 -0400\n" + \
               "gpgsig -----BEGIN PGP SIGNATURE-----\n" + \
               " \n" + \
               " wsBcBAABCAAQBQJc/Ac+CRBK7hj4Ov3rIwAAdHIIAJVYNA8ZCS8Gl/ckHB+SSwIt\n" + \
                " Uu78eWzEcR/kg229iBJWhUix0M3q0ku40aMwB5YjxVvRWNUE9OYiXqqYMvRHWopO\n" + \
               " KEHK43z1SVAmAUUUfxHnqj/w72qNlSVMsNGJVMb45jlmRoaD4zt5tvnuqqAY9yV0\n" + \
               " xKtAIwjRvkX5zK9FRXPzP1e9PULLvcSXI8GJyUEi8gdryqipxyKP0B9t23tUCZLA\n" + \
               " XyAMBiQLYfo8LFvsPwS8qSeuv2JHiyBLMEeqGc90KJzXQU7vUsX0Xp9HmkG6TBCa\n" + \
               " 655BsGkxwC3y04Png6HcY5nX3Y0XNkAPCjx5fnoRxYyZC92jnREs8rZ3odc5jRo=\n" + \
               " =4fKp\n" + \
               " -----END PGP SIGNATURE-----\n" + \
               " \n" + \
               "\n" + \
               "Merge pull request #1 from kevindugan/travis-ci\n" + \
                "\n" + \
               "Adding ci script"
    filePath = os.path.join(tmpdir, "myTest", "dir1", "testFile.txt")
    os.makedirs(os.path.dirname(filePath))
    with open(filePath, "w") as f:
        f.write(contents)

    # Hash without writing
    expected_hash = '0b2076b2607785d7aa94eb7fd63689f679967c04'
    myGit.run(['hash-object', '-t', 'commit', filePath])
    captured = capsys.readouterr()
    assert captured.out.strip() == expected_hash

    assert not os.path.isfile(os.path.join(tmpdir, "myTest", ".git", "objects", expected_hash[0:2], expected_hash[2:]))

    # Hash and write file
    myGit.run(['hash-object', '-w', '-t', 'commit', filePath])
    captured = capsys.readouterr()
    assert captured.out.strip() == expected_hash

    assert os.path.isfile(os.path.join(tmpdir, "myTest", ".git", "objects", expected_hash[0:2], expected_hash[2:]))

    # Get contents of file
    os.chdir(os.path.join(tmpdir, "myTest"))
    myGit.run(['cat-file', expected_hash])
    captured = capsys.readouterr()
    assert captured.out == contents
