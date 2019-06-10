import os
import hashlib
import zlib
import re
import collections
from VersionControl import GitObjectFactory
from datetime import datetime
from termcolor import colored

class GitObject(object):

    def __init__(self, repo, data=None):
        self.repository = repo
        if data is not None:
            self.deserializeData(data)
    
    def getObjectType(self):
        raise NotImplementedError()

    def serializeData(self):
        raise NotImplementedError()

    def deserializeData(self, path):
        raise NotImplementedError()

    def create_object(self, actually_write=False):

        contents = self.serializeData()
        header = self.getObjectType() + " " + str(len(contents)) + '\0'
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
            assert obj_format in ['blob', 'commit']

            y = raw.find(b'\x00', x)
            obj_size = int(raw[x:y].decode('ascii'))

            contents = raw[y+1:].decode('ascii')

            if len(contents) != obj_size:
                raise RuntimeError("Malformed Object {0}: bad length".format(sha_hash))

        return GitObjectFactory.GitObjectFactory.factory(obj_format, self.repository, contents)

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

        # last_key = next(reversed(result))
        # result[last_key] += '\n'

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
            result += "\n" + data["short_msg"] + '\n'
        if "long_msg" in data:
            result += "\n" + data["long_msg"]

        # result += '\n'

        return result

    def fillCommitQueue(self, sha, queue):
        queue.add(sha)

        contents = self.read_object(sha)
        assert contents.getObjectType() == "commit"
        if "parent" not in contents.commitData.keys():
            return
            
        parent = ""
        if type(contents.commitData["parent"]) == list:
            parent = contents.commitData["parent"][0]
        else:
            parent = contents.commitData["parent"]

        self.fillCommitQueue(parent, queue)

    def getLowestCommonAncestor(self, commits):
        assert len(commits) > 0

        queue = CommitQueue()
        self.fillCommitQueue(commits[0], queue)
        assert queue.size() > 0

        for other in commits[1:]:
            otherQueue = CommitQueue()
            self.fillCommitQueue(other, otherQueue)
            while(not otherQueue.empty()):
                if otherQueue.top() in queue:
                    break
                else:
                    otherQueue.pop()

            queue = otherQueue

        return queue.top()

    def getLog(self, sha, result=[], LCA=None):

        if sha in result:
            return result
        result.append(sha)

        contents = self.read_object(sha)
        assert contents.getObjectType() == "commit"

        if "parent" not in contents.commitData.keys():
            return result

        parents = contents.commitData["parent"]
        if type(parents) != list:
            parents = [ parents ]
        
        if len(parents) > 1:
            LCA = self.getLowestCommonAncestor(parents)

        for p in parents:
            if p == LCA:
                return result
            result = self.getLog(p, result, LCA)

        if not LCA is None:
            result = self.getLog(LCA, result)

        return result

    def printLog(self, sha_history, colored_output=True):
        message = ""
        for commit in sha_history:
            contents = self.read_object(commit)
            if colored_output:
                message += colored("commit " + commit + "\n", 'yellow')
            else:
                message += "commit " + commit + "\n"
            if "parent" in contents.commitData:
                if type(contents.commitData["parent"]) == list:
                    message += "Merge:"
                    for p in contents.commitData["parent"]:
                        message += " " + p[:7]
                    message += "\n"
            header = contents.commitData["author"]
            CA = re.split('([0-9]+ -[0-9]+)', header)
            author = CA[0].strip()
            date = int(CA[1].split()[0])
            zone = CA[1].split()[1]
            message += "Author: " + author + "\n"

            date = datetime.fromtimestamp(date)
            message += "Date:   " + date.strftime("%a %b %-d %H:%M:%S %Y") + " " + zone + "\n"
            message += "\n"
            message += "    " + contents.commitData["short_msg"] + "\n"
            message += "\n"
        
        # Remove last new line
        print(message.rstrip('\n'))



class CommitQueue(object):

    def __init__(self):
        self.queue = []

    def size(self):
        return len(self.queue)

    def empty(self):
        return len(self.queue) == 0

    def add(self, item):
        self.queue.append(item)

    def pop(self):
        return self.queue.pop(0)

    def top(self):
        return self.queue[0]

    def pop_until(self, item):
        assert item in self.queue, "Item not in queue"
        while (len(self.queue) > 0):
            if self.top() == item:
                return
            else:
                self.pop()

    def __contains__(self, item):
        return item in self.queue