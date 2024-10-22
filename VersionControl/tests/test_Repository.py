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