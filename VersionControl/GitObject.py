import os
import hashlib
import zlib
import re
import collections

class GitObject(object):

    def __init__(self, repo):
        self.repository = repo

    def create_object(self, path, actually_write=False):
        if not os.path.isabs(path):
            path = os.path.abspath(path)

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

    @staticmethod
    def parse_commit_object(data):
        # Commit object consists of two parts. The first part is a key value pair list
        # where keys and values are separated by a space. The key starts at the line begining
        # until the first space. The value is all that remains. Values can continue after line
        # ends where a space will start the next line.
        # The second part consists of a short commit message and an optional long commit message

        # Split the lines of data if the character following the newline is not a space
        # Keep the split string because it will contain the first character of a key
        SD = re.split("(\n[^ ])", data)

        # Add the first character of the key back to that key value pair
        splitData = [""]
        for item in SD:
            if item[0] != '\n':
                splitData[-1] += item
            else:
                splitData.append(item[1:])

        # Add all key value pairs along with long and short messages to an ordered
        # dictionary
        result = collections.OrderedDict()
        key_values_done = False
        for item in splitData:

            # The commit messages start after a blank line. This shows up as the first
            # character being a new line
            if item[0] == '\n':
                key_values_done = True

            if not key_values_done:
                # Split the key value pair by the key and the remaining
                split_item = item.split(" ", 1)
                key = split_item[0]
                value = split_item[1]

                # Take care of line continuation
                value = value.replace("\n ", "\n")

                # Don't overwrite data in the dictionary. Append it
                if key in result:
                    if type(result[key]) == list:
                        result[key].append(value)
                    else:
                        result[key] = [ result[key], value ]
                else:
                    result[key] = value
            else:
                # Add short message and keep going
                if "short_msg" not in result:
                    result["short_msg"] = item.strip()
                    continue

                # Add all remaining lines as long message
                if "long_msg" not in result:
                    result["long_msg"] = item.strip()
                else:
                    result["long_msg"] += '\n' + item.strip()

        return result

    @staticmethod
    def serialize_commit_object(data):

        result = ""

        for key, value in data.items():

            if key == "short_msg" or key == "long_msg":
                continue

            if type(value) != list:
                value = [ value ]

            for v in value:
                result += key + " " + v.replace("\n", "\n ") + "\n"

        if "short_msg" in data:
            result += "\n" + data["short_msg"]
        if "long_msg" in data:
            result += "\n\n" + data["long_msg"]

        return result