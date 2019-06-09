from VersionControl import BlobObject

class GitObjectFactory(object):
    
    @staticmethod
    def factory(type, repository, data=None):
        if type == "blob":
            return BlobObject.BlobObject(repository, data)
        else:
            raise RuntimeError("Unknown Object Type: "+str(type))