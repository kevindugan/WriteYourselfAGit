from VersionControl.GitObject import GitObject
import os

class BlobObject(GitObject):
    
    def getObjectType(self):
        return "blob"

    def serializeData(self):
        return self.blobData

    def deserializeData(self, data):
        self.blobData = data