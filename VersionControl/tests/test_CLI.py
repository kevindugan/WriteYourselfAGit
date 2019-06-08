import pytest
from VersionControl import WyagLib

def test_init_parser():
    myGit = WyagLib.wyag()

    with pytest.raises(SystemExit):
        myGit.processCLI()

    with pytest.raises(SystemExit):
        myGit.processCLI(['init'])

    with pytest.raises(SystemExit):
        myGit.processCLI(['init', 'path1', 'path2'])

    test1 = myGit.processCLI(['init', 'dir/path'])
    assert test1['path'] == 'dir/path'

def test_subparser():
    myGit = WyagLib.wyag()

    with pytest.raises(SystemExit):
        myGit.processCLI(['unknown'])