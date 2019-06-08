import os
import hashlib
import zlib

class GitObject(object):

    def __init__(self, repo):
        self.repository = repo

    def create_object(self, path, actually_write=False):
        if not os.path.isabs(path):
            raise RuntimeError("Expected Absolute Path")

        contents = ""
        with open(path) as f:
            contents = f.read()

        header = "blob " + str(len(contents)) + '\0'
        storage = (header + contents).encode()

        sha = hashlib.sha1(storage).hexdigest()

        if actually_write:
            filePath = os.path.join(self.repository.gitDir, "objects", sha[0:2], sha[2:])
            os.makedirs(os.path.dirname(filePath))
            with open(filePath, "wb") as f:
                f.write(zlib.compress(storage))

        return sha

    def read_object(self, sha_hash):

        repoFilePath = os.path.join(self.repository.gitDir, "objects", sha_hash[0:2], sha_hash[2:])

        contents = ""
        with open(repoFilePath, "rb") as f:
            raw = zlib.decompress(f.read())

            x = raw.find(b' ')
            obj_format = raw[0:x].decode('ascii')

            y = raw.find(b'\x00', x)
            obj_size = int(raw[x:y].decode('ascii'))

            contents = raw[y+1:].decode('ascii')

            if len(contents) != obj_size:
                raise RuntimeError("Malformed Object {0}: bad length".format(sha_hash))

            assert obj_format == 'blob'

        return contents