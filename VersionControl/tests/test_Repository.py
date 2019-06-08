import pytest
import os
from VersionControl import GitRepository

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