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

def test_log_cmd(tmpdir, capsys):
    
    myGit = WyagLib.wyag()
    myGit.run(['init', os.path.join(tmpdir, "myTest")])

    commitHistory = git_commit_history_data()
    for item in commitHistory:
        with open(os.path.join(tmpdir, "myTest", "hashObject.txt"), "w") as f:
            f.write(item[0])
        myGit.run(['hash-object', '-w', '-t', 'commit', os.path.join(tmpdir, "myTest", "hashObject.txt")])
        captured = capsys.readouterr()
        assert captured.out.strip() == item[1]

    # Change into generated repo
    os.chdir(os.path.join(tmpdir, "myTest"))

    # Create HEAD
    with open(os.path.join(tmpdir, "myTest", ".git", "refs", "heads", "master"), "w") as f:
        f.write(commitHistory[-1][1])

    myGit.run(['log', '--no-color'])
    captured = capsys.readouterr()
    log_result = captured.out.strip()
    assert log_result == get_log_output_plain()



def git_commit_history_data():
    history = []
    history.append(["tree aff72e7367c3ae1928decc25272ec334a805e618\n" + \
                   "author Kevin J. Dugan <dugankj@ornl.gov> 1560083980 -0400\n" + \
                   "committer Kevin J. Dugan <dugankj@ornl.gov> 1560083980 -0400\n" + \
                   "\n" + \
                   "Initial Commit\n", "d228dfd0601080af1af564eb7a3bc6fbb7a2696f"])


    history.append(["tree 18e156c8acb2081a9b300796b8672f27837e3961\n" + \
                   "parent d228dfd0601080af1af564eb7a3bc6fbb7a2696f\n" + \
                   "author Kevin J. Dugan <dugankj@ornl.gov> 1560084040 -0400\n" + \
                   "committer Kevin J. Dugan <dugankj@ornl.gov> 1560084040 -0400\n" + \
                   "\n" + \
                   "Added new line\n", "30f3cf9a5f3b33b6090f469c6f8fd8ced8aad098"])


    history.append(["tree 24cc7c0ead06780c12ae9ae79fc7fb69c0f054ee\n" + \
                   "parent 30f3cf9a5f3b33b6090f469c6f8fd8ced8aad098\n" + \
                   "author Kevin J. Dugan <dugankj@ornl.gov> 1560084096 -0400\n" + \
                   "committer Kevin J. Dugan <dugankj@ornl.gov> 1560084096 -0400\n" + \
                   "\n" + \
                   "Added new file\n", "6ed18ac3b2d77272bf240f313901ef75076d6377"])

                   
    history.append(["tree c8cd9c7e731de0feb53cd0f0a60ebe39d30ebfd8\n" + \
                   "parent 6ed18ac3b2d77272bf240f313901ef75076d6377\n" + \
                   "author Kevin J. Dugan <dugankj@ornl.gov> 1560084124 -0400\n" + \
                   "committer Kevin J. Dugan <dugankj@ornl.gov> 1560084124 -0400\n" + \
                   "\n" + \
                   "Added new line\n", "17c06afad13f728e4e31ae85a534a5cf73e2bd76"])


    history.append(["tree 4fdedfd76570511fb0e43153b8cfe2aba896b009\n" + \
                   "parent 30f3cf9a5f3b33b6090f469c6f8fd8ced8aad098\n" + \
                   "author Kevin J. Dugan <dugankj@ornl.gov> 1560084362 -0400\n" + \
                   "committer Kevin J. Dugan <dugankj@ornl.gov> 1560084362 -0400\n" + \
                   "\n" + \
                   "Added new lines\n", "bbfbe5740cb7180100e86504779d38173d2247cb"])


    history.append(["tree 24cb97583ae8ef3e046c8e7f8d78aea8a0986e20\n" + \
                   "parent bbfbe5740cb7180100e86504779d38173d2247cb\n" + \
                   "parent 17c06afad13f728e4e31ae85a534a5cf73e2bd76\n" + \
                   "author Kevin J. Dugan <dugankj@ornl.gov> 1560084417 -0400\n" + \
                   "committer Kevin J. Dugan <dugankj@ornl.gov> 1560084417 -0400\n" + \
                   "\n" + \
                   "Merge branch 'new-file'\n", "af54843b4fa85db56ed9140b5a39ec2df744fc4b"])


    history.append(["tree 0fef7a0dc4cd421c3645c21f878b76205f78c3b1\n" + \
                   "parent af54843b4fa85db56ed9140b5a39ec2df744fc4b\n" + \
                   "author Kevin J. Dugan <dugankj@ornl.gov> 1560084474 -0400\n" + \
                   "committer Kevin J. Dugan <dugankj@ornl.gov> 1560084474 -0400\n" + \
                   "\n" + \
                   "added new lines\n", "075c7e021c0d2e4a43f01a2e848daf605ed4e65f"])


    return history

def get_log_output_plain():
    message = ""
    message += "commit 075c7e021c0d2e4a43f01a2e848daf605ed4e65f\n"
    message += "Author: Kevin J. Dugan <dugankj@ornl.gov>\n"
    message += "Date:   Sun Jun 9 12:47:54 2019 -0400\n"
    message += "\n"
    message += "    added new lines\n"
    message += "\n"
    message += "commit af54843b4fa85db56ed9140b5a39ec2df744fc4b\n"
    message += "Merge: bbfbe57 17c06af\n"
    message += "Author: Kevin J. Dugan <dugankj@ornl.gov>\n"
    message += "Date:   Sun Jun 9 12:46:57 2019 -0400\n"
    message += "\n"
    message += "    Merge branch 'new-file'\n"
    message += "\n"
    message += "commit bbfbe5740cb7180100e86504779d38173d2247cb\n"
    message += "Author: Kevin J. Dugan <dugankj@ornl.gov>\n"
    message += "Date:   Sun Jun 9 12:46:02 2019 -0400\n"
    message += "\n"
    message += "    Added new lines\n"
    message += "\n"
    message += "commit 17c06afad13f728e4e31ae85a534a5cf73e2bd76\n"
    message += "Author: Kevin J. Dugan <dugankj@ornl.gov>\n"
    message += "Date:   Sun Jun 9 12:42:04 2019 -0400\n"
    message += "\n"
    message += "    Added new line\n"
    message += "\n"
    message += "commit 6ed18ac3b2d77272bf240f313901ef75076d6377\n"
    message += "Author: Kevin J. Dugan <dugankj@ornl.gov>\n"
    message += "Date:   Sun Jun 9 12:41:36 2019 -0400\n"
    message += "\n"
    message += "    Added new file\n"
    message += "\n"
    message += "commit 30f3cf9a5f3b33b6090f469c6f8fd8ced8aad098\n"
    message += "Author: Kevin J. Dugan <dugankj@ornl.gov>\n"
    message += "Date:   Sun Jun 9 12:40:40 2019 -0400\n"
    message += "\n"
    message += "    Added new line\n"
    message += "\n"
    message += "commit d228dfd0601080af1af564eb7a3bc6fbb7a2696f\n"
    message += "Author: Kevin J. Dugan <dugankj@ornl.gov>\n"
    message += "Date:   Sun Jun 9 12:39:40 2019 -0400\n"
    message += "\n"
    message += "    Initial Commit"
    return message