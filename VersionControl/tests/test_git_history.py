from VersionControl import GitHistory, GitRepository
from VersionControl import CommitObject
import pytest
import os

def test_commit_queue():
    
    queue = GitHistory.CommitQueue()
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

    queue = GitHistory.CommitQueue()
    history = GitHistory.GitHistory(repo)
    history.fillCommitQueue(historyData[-1][1], queue)
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

    history = GitHistory.GitHistory(repo)
    result = history.getLowestCommonAncestor(commits=[sha1, sha2])
    assert result == base

    result = history.getLowestCommonAncestor(commits=[sha1])
    assert result == sha1


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

    history = GitHistory.GitHistory(repo)
    shaList = history.getLog(head)
    print("\nLog")
    for result, expected in zip(shaList, reversed(historyData)):
        print("Result: "+result+"  Expected: "+expected[1])

    assert len(shaList) == len(historyData)
    for result, expected in zip(shaList,reversed(historyData)):
        assert result == expected[1]

    history.printLog(shaList)









###############################################################################
# Data Setup
###############################################################################
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