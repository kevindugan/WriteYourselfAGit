from VersionControl.GitObject import GitObject

class CommitObject(GitObject):

    def getObjectType(self):
        return "commit"

    def serializeData(self):
        return GitObject.serialize_commit_object(self.commitData)

    def deserializeData(self, data):
        self.commitData = GitObject.parse_commit_object(data)