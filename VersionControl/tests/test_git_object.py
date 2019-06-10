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

def test_commit_queue():

    queue = GitObject.CommitQueue()
    assert queue.size() == 0
    assert queue.empty()

    queue.add("first")
    queue.add("second")
    queue.add("third")
    queue.add("fourth")
    queue.add("fifth")
    queue.add("sixth")
    assert queue.size() == 6

    assert queue.pop() == "first"
    assert queue.top() == "second"

    assert "second" in queue
    assert "fifth" in queue
    assert not "first" in queue

    with pytest.raises(AssertionError):
        queue.pop_until("feet")

    queue.pop_until("fourth")
    assert queue.top() == "fourth"

def test_fill_commit_queue(tmpdir):
    repo = GitRepository.GitRepository(os.path.join(tmpdir, "myTest"))
    repo.initializeGitDir()

    historyData = git_commit_history_data()
    for commit in historyData:
        obj = CommitObject.CommitObject(repo, commit[0])
        sha = obj.create_object(True)
        assert sha == commit[1]

    queue = GitObject.CommitQueue()
    obj = CommitObject.CommitObject(repo)
    obj.fillCommitQueue(historyData[-1][1], queue)
    assert queue.size() == 5
    assert queue.top() == historyData[-1][1]

def test_base_commit(tmpdir):
    repo = GitRepository.GitRepository(os.path.join(tmpdir, "myTest"))
    repo.initializeGitDir()

    historyData = git_commit_history_data()
    for commit in historyData:
        obj = CommitObject.CommitObject(repo, commit[0])
        sha = obj.create_object(True)
        assert sha == commit[1]

    sha1 = historyData[3][1]
    sha2 = historyData[4][1]
    base = historyData[1][1]

    obj = GitObject.GitObject(repo)
    result = obj.getLowestCommonAncestor(commits=[sha1, sha2])
    assert result == base


def test_log(tmpdir):
    repo = GitRepository.GitRepository(os.path.join(tmpdir, "myTest"))
    repo.initializeGitDir()

    historyData = git_commit_history_data()
    for commit in historyData:
        obj = CommitObject.CommitObject(repo, commit[0])
        sha = obj.create_object(True)
        assert sha == commit[1]

    head = historyData[-1][1]
    # print(head)

    obj = CommitObject.CommitObject(repo)
    shaList = obj.getLog(head)
    print("\nLog")
    for result, expected in zip(shaList, reversed(historyData)):
        print("Result: "+result+"  Expected: "+expected[1])

    # assert len(shaList) == len(historyData)
    # for result, expected in zip(shaList,reversed(historyData)):
    #     assert result == expected[1]
    


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