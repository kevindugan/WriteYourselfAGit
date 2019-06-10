import pytest
from VersionControl import GitRepository, BlobObject, GitObject, CommitObject
import os

def test_create_blob_object(tmpdir):
    repo = GitRepository.GitRepository(os.path.join(tmpdir, "myTest"))
    repo.initializeGitDir()

    # Create File
    contents = 'blah\nblahblah\nblah blah blah\n\nblah\n'
    expected_hash = '5e9548362714d1cef162e97a23a7a42f7311e54d'

    obj = BlobObject.BlobObject(repo, contents)
    sha = obj.create_object(False)

    assert sha == expected_hash

    sha = obj.create_object(True)
    assert os.path.isfile(os.path.join(tmpdir, "myTest", ".git", "objects", expected_hash[0:2], expected_hash[2:]))

def test_read_blob_object(tmpdir):
    repo = GitRepository.GitRepository(os.path.join(tmpdir, "myTest"))
    repo.initializeGitDir()

    # Create File
    contents = 'blah\nblahblah\nblah blah blah\n\nblah\n'
    expected_hash = '5e9548362714d1cef162e97a23a7a42f7311e54d'

    obj = BlobObject.BlobObject(repo, contents)
    sha = obj.create_object(True)

    result = obj.read_object(sha).serializeData()
    assert result == contents

def test_parse_commit_object():

    # Standard Commit
    contents, expected_hash = get_simple_commit_data()

    result = GitObject.GitObject.parse_commit_object(contents)

    assert "tree" in result
    assert result["tree"] == 'aa2fd36eabc0cdb0c629c3d164d81dc31c2aa8fb'
    assert "parent" in result
    assert result["parent"] == '6d2f5894d033a5c19cd8d3a41ab1626ab272ed51'
    assert "short_msg" in result
    assert result["short_msg"] == 'Adding readme'
    assert "long_msg" not in result

    serial_result = GitObject.GitObject.serialize_commit_object(result)
    assert serial_result == contents

    # More complicated commit
    contents, expected_hash = get_complex_commit_data()

    result = GitObject.GitObject.parse_commit_object(contents)

    assert "tree" in result
    assert result["tree"] == "025b46d991b8602e229fa477dbc50a98ee050dcf"
    assert "parent" in result
    assert len(result["parent"]) == 2
    for p,expt in zip (result["parent"], ["a33e731eb4d600b08dcd34fea6fe45cecc7958a0", "f4f16ee537a618502fac0f6a0db822ddd3b45b12"]):
        assert p == expt
    assert "gpgsig" in result
    assert result["gpgsig"] == "-----BEGIN PGP SIGNATURE-----\n" + \
                                "\n" + \
                                "wsBcBAABCAAQBQJc/Ac+CRBK7hj4Ov3rIwAAdHIIAJVYNA8ZCS8Gl/ckHB+SSwIt\n" + \
                                "Uu78eWzEcR/kg229iBJWhUix0M3q0ku40aMwB5YjxVvRWNUE9OYiXqqYMvRHWopO\n" + \
                                "KEHK43z1SVAmAUUUfxHnqj/w72qNlSVMsNGJVMb45jlmRoaD4zt5tvnuqqAY9yV0\n" + \
                                "xKtAIwjRvkX5zK9FRXPzP1e9PULLvcSXI8GJyUEi8gdryqipxyKP0B9t23tUCZLA\n" + \
                                "XyAMBiQLYfo8LFvsPwS8qSeuv2JHiyBLMEeqGc90KJzXQU7vUsX0Xp9HmkG6TBCa\n" + \
                                "655BsGkxwC3y04Png6HcY5nX3Y0XNkAPCjx5fnoRxYyZC92jnREs8rZ3odc5jRo=\n" + \
                                "=4fKp\n" + \
                                "-----END PGP SIGNATURE-----\n"


    assert "short_msg" in result
    assert result["short_msg"] == "Merge pull request #1 from kevindugan/travis-ci"
    assert "long_msg" in result
    assert result["long_msg"] == "Adding ci script"

    serial_result = GitObject.GitObject.serialize_commit_object(result)
    assert serial_result == contents

def test_create_commit_object(tmpdir):
    repo = GitRepository.GitRepository(os.path.join(tmpdir, "myTest"))
    repo.initializeGitDir()

    contents, expected_hash = get_complex_commit_data()

    obj = CommitObject.CommitObject(repo, contents)
    sha = obj.create_object(False)

    assert sha == expected_hash

    sha = obj.create_object(True)
    assert os.path.isfile(os.path.join(tmpdir, "myTest", ".git", "objects", expected_hash[0:2], expected_hash[2:]))

def test_read_commit_object(tmpdir):
    repo = GitRepository.GitRepository(os.path.join(tmpdir, "myTest"))
    repo.initializeGitDir()

    # Create File
    contents, expected_hash = get_complex_commit_data()

    obj = CommitObject.CommitObject(repo, contents)
    sha = obj.create_object(True)

    result = obj.read_object(sha).serializeData()
    assert result == contents


    


###############################################################################
# Data Setup
###############################################################################
def get_simple_commit_data():
    return "tree aa2fd36eabc0cdb0c629c3d164d81dc31c2aa8fb\n" + \
           "parent 6d2f5894d033a5c19cd8d3a41ab1626ab272ed51\n" + \
           "author Kevin J. Dugan <dugankj@ornl.gov> 1559970810 -0400\n" + \
           "committer Kevin J. Dugan <dugankj@ornl.gov> 1559970810 -0400\n" + \
           "\n" + \
           "Adding readme\n", "a62df6acda73871958f89e0346c97284d1a14f23"

def get_complex_commit_data():
    return "tree 025b46d991b8602e229fa477dbc50a98ee050dcf\n" + \
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
           "Adding ci script", "0b2076b2607785d7aa94eb7fd63689f679967c04"

