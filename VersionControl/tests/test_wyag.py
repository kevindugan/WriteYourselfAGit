import pytest
from VersionControl import WyagLib
import os

def test_init_command(tmpdir):
    
    myGit = WyagLib.wyag()
    myGit.run(['init', os.path.join(tmpdir, "myTest")])

    assert os.path.isfile(os.path.join(tmpdir, "myTest", ".git", "HEAD"))
    with open(os.path.join(tmpdir, "myTest", ".git", "HEAD")) as f:
        assert f.read().strip() == "ref: refs/heads/master"