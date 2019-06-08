import os
import configparser

class GitRepository():

    def __init__(self, path):
        self.workTree = os.path.abspath(path)
        self.gitDir = os.path.join(self.workTree, ".git")

    def initializeGitDir(self):
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