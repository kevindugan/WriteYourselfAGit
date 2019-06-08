import pytest
from VersionControl import GitRepository, GitObject
import os

def test_create_blob_object(tmpdir):
    repo = GitRepository.GitRepository(os.path.join(tmpdir, "myTest"))
    repo.initializeGitDir()

    # Create File
    contents = 'blah\nblahblah\nblah blah blah\n\nblah\n'
    expected_hash = '5e9548362714d1cef162e97a23a7a42f7311e54d'

    filePath = os.path.join(tmpdir, "myTest", "test.txt")
    with open(filePath, "w") as f:
        f.write(contents)

    obj = GitObject.GitObject(repo)
    sha = obj.create_object(filePath, False)

    assert sha == expected_hash

    sha = obj.create_object(filePath, True)
    assert os.path.isfile(os.path.join(tmpdir, "myTest", ".git", "objects", expected_hash[0:2], expected_hash[2:]))

def test_read_blob_object(tmpdir):
    repo = GitRepository.GitRepository(os.path.join(tmpdir, "myTest"))
    repo.initializeGitDir()

    # Create File
    contents = 'blah\nblahblah\nblah blah blah\n\nblah\n'
    expected_hash = '5e9548362714d1cef162e97a23a7a42f7311e54d'

    filePath = os.path.join(tmpdir, "myTest", "test.txt")
    with open(filePath, "w") as f:
        f.write(contents)

    obj = GitObject.GitObject(repo)
    sha = obj.create_object(filePath, True)

    result = obj.read_object(sha)
    assert result == contents
