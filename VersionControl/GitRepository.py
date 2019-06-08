import os, sys
import configparser

class GitRepository():

    def __init__(self, path):
        self.workTree = os.path.abspath(path)
        self.gitDir = os.path.join(self.workTree, ".git")

    def __eq__(self, other):
        return self.gitDir == other.gitDir

    def initializeGitDir(self):
        if os.path.isdir(self.gitDir):
            raise RuntimeError("Trying to reinitialize repository at: "+str(self.gitDir))

        if not os.path.isdir(self.gitDir):
            os.makedirs(self.gitDir)
            os.makedirs(os.path.join(self.gitDir, "branches"))
            os.makedirs(os.path.join(self.gitDir, "objects"))
            os.makedirs(os.path.join(self.gitDir, "refs", "tags"))
            os.makedirs(os.path.join(self.gitDir, "refs", "heads"))

        with open(os.path.join(self.gitDir, "description"), "w") as f:
            f.write("Unnamed repository; edit this file 'description' to name the repository.")

        with open(os.path.join(self.gitDir, "HEAD"), "w") as f:
            f.write("ref: refs/heads/master")

        with open(os.path.join(self.gitDir, "config"), "w") as f:
            config = self.getDefaultConfig()
            config.write(f)

    def getDefaultConfig(self):
        result = configparser.ConfigParser()

        result.add_section('core')
        result.set('core', 'repositoryformatversion', '0')
        result.set('core', 'filemode', 'false')
        result.set('core', 'bare', 'false')

        return result

    @staticmethod
    def find_repo(path):
        path = os.path.abspath(path)

        if os.path.isdir(os.path.join(path, ".git")):
            return GitRepository(path)

        parent = os.path.abspath(os.path.join(path, os.pardir))

        if parent == path:
            # Base case where we've reached the root dir
            print("Fatal: Not a git repository")
            sys.exit(1)

        return GitRepository.find_repo(parent)