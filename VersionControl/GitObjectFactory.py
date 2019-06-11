from VersionControl import BlobObject, CommitObject

class GitObjectFactory(object):
    
    @staticmethod
    def factory(type, repository, data=None):
        if type == "blob":
            return BlobObject.BlobObject(repository, data)
        elif type == "commit":
            return CommitObject.CommitObject(repository, data)
        else:
            raise RuntimeError("Unknown Object Type: "+str(type))