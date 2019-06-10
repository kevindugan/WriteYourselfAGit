import pytest
import os
from VersionControl import GitRepository, GitObjectFactory

def test_init_repo(tmpdir):
    repo = GitRepository.GitRepository(os.path.join(tmpdir, "myTest"))

    assert repo.workTree == os.path.join(tmpdir, "myTest")
    assert os.path.isabs(repo.workTree)
    assert repo.gitDir == os.path.join(tmpdir, "myTest", ".git")
    assert os.path.isabs(repo.gitDir)

    assert not os.path.exists(repo.workTree)
    assert not os.path.exists(repo.gitDir)

    repo2 = GitRepository.GitRepository("./myTest")

    assert repo2.workTree == os.path.join(os.getcwd(), "myTest")
    assert os.path.isabs(repo2.workTree)
    assert repo2.gitDir == os.path.join(os.getcwd(), "myTest", ".git")
    assert os.path.isabs(repo2.gitDir)

    assert not os.path.exists(repo2.workTree)
    assert not os.path.exists(repo2.gitDir)

def test_create_repo(tmpdir):

    repo = GitRepository.GitRepository(os.path.join(tmpdir,"myTest"))

    repo.initializeGitDir()

    assert os.path.isdir(os.path.join(tmpdir, "myTest"))
    assert os.path.isdir(os.path.join(tmpdir, "myTest", ".git"))
    assert os.path.isdir(os.path.join(tmpdir, "myTest", ".git", "branches"))
    assert os.path.isdir(os.path.join(tmpdir, "myTest", ".git", "objects"))
    assert os.path.isdir(os.path.join(tmpdir, "myTest", ".git", "refs", "tags"))
    assert os.path.isdir(os.path.join(tmpdir, "myTest", ".git", "refs", "heads"))

    assert os.path.isfile(os.path.join(tmpdir, "myTest", ".git", "description"))
    with open(os.path.join(tmpdir, "myTest", ".git", "description")) as f:
        contents = f.read()
        assert contents.strip() == "Unnamed repository; edit this file 'description' to name the repository."

    assert os.path.isfile(os.path.join(tmpdir, "myTest", ".git", "HEAD"))
    with open(os.path.join(tmpdir, "myTest", ".git", "HEAD")) as f:
        contents = f.read()
        assert contents.strip() == "ref: refs/heads/master"

    assert os.path.isfile(os.path.join(tmpdir, "myTest", ".git", "config"))
    with open(os.path.join(tmpdir, "myTest", ".git", "config")) as f:
        contents = f.read()
        assert contents.strip() == "[core]\nrepositoryformatversion = 0\nfilemode = false\nbare = false"

def test_repo_comparison(tmpdir):
    repo1 = GitRepository.GitRepository(os.path.join(tmpdir, "repo1"))
    repo1.initializeGitDir()
    repo1_bis = GitRepository.GitRepository(os.path.join(tmpdir, "repo1"))

    # Try to reinitialize repo
    with pytest.raises(RuntimeError):
        repo1_bis.initializeGitDir()

    # Should show equality
    assert repo1 == repo1_bis

    repo2 = GitRepository.GitRepository(os.path.join(tmpdir, "repo2"))
    assert not repo1 == repo2

def test_find_repo(tmpdir):
    repo = GitRepository.GitRepository(os.path.join(tmpdir, "myTest"))
    repo.initializeGitDir()

    # Create subdirs
    os.makedirs(os.path.join(tmpdir, "myTest", "dir1", "dir11", "dir13"))

    # Test outside git repo
    with pytest.raises(SystemExit):
        GitRepository.GitRepository.find_repo(tmpdir)

    # Test in root dir
    result = GitRepository.GitRepository.find_repo(os.path.join(tmpdir, "myTest"))
    assert result == repo

    # Test in subdir
    result = GitRepository.GitRepository.find_repo(os.path.join(tmpdir, "myTest", "dir1", "dir11", "dir13"))
    assert result == repo

    # Test cwd
    os.chdir(os.path.join(tmpdir, "myTest", "dir1", "dir11", "dir13"))
    assert os.getcwd() == os.path.join(tmpdir, "myTest", "dir1", "dir11", "dir13")
    result = GitRepository.GitRepository.find_repo(os.getcwd())
    assert result == repo

def test_set_head(tmpdir):
    repo = GitRepository.GitRepository(os.path.join(tmpdir, "myTest"))

    with pytest.raises(RuntimeError):
        repo.setHeadCommit("blah")

    repo.initializeGitDir()

    commitData = ["tree aff72e7367c3ae1928decc25272ec334a805e618\n" + \
                  "author Kevin J. Dugan <dugankj@ornl.gov> 1560083980 -0400\n" + \
                  "committer Kevin J. Dugan <dugankj@ornl.gov> 1560083980 -0400\n" + \
                  "\n" + \
                  "Initial Commit\n", "d228dfd0601080af1af564eb7a3bc6fbb7a2696f"]

    obj = GitObjectFactory.GitObjectFactory.factory("commit", repo, commitData[0])
    sha = obj.create_object(True)
    assert sha == commitData[1]

    headPath = os.path.join(tmpdir, "myTest", ".git", "refs", "heads", "master")
    assert not os.path.isfile(headPath)
    repo.setHeadCommit(sha)
    assert os.path.isfile(headPath)
    with open(headPath) as f:
        assert sha == f.read().strip()

    assert repo.getHeadCommit() == sha

def test_commit_queue():

    queue = GitRepository.CommitQueue()
    assert queue.size() == 0

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