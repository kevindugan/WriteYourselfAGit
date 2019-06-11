from VersionControl import GitObjectFactory
from datetime import datetime
import importlib
if importlib.util.find_spec("termcolor") is not None:
    from termcolor import colored
import re


def color_out(message, color):
    if importlib.util.find_spec("termcolor") is None:
        return message
    else:
        return colored(message, color)

class GitHistory(object):

    def __init__(self, repo, options={}):
        self.repository = repo
        self.options = options

    def fillCommitQueue(self, sha, queue):
        queue.add(sha)

        obj = GitObjectFactory.GitObjectFactory.factory("commit", self.repository)
        contents = obj.read_object(sha).data()

        if "parent" not in contents.keys():
            return
            
        parent = ""
        if type(contents["parent"]) == list:
            parent = contents["parent"][0]
        else:
            parent = contents["parent"]

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

        obj = GitObjectFactory.GitObjectFactory.factory("commit", self.repository)
        contents = obj.read_object(sha).data()


        if "parent" not in contents.keys():
            return result

        parents = contents["parent"]
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
            obj = GitObjectFactory.GitObjectFactory.factory("commit", self.repository)
            contents = obj.read_object(commit).data()
            if colored_output:
                message += color_out("commit " + commit + "\n", 'yellow')
            else:
                message += "commit " + commit + "\n"
            if "parent" in contents.keys():
                if type(contents["parent"]) == list:
                    message += "Merge:"
                    for p in contents["parent"]:
                        message += " " + p[:7]
                    message += "\n"
            header = contents["author"]
            CA = re.split('([0-9]+ -[0-9]+)', header)
            author = CA[0].strip()
            date = int(CA[1].split()[0])
            zone = CA[1].split()[1]
            message += "Author: " + author + "\n"

            date = datetime.utcfromtimestamp(date)
            message += "Date:   " + date.strftime("%a %b %-d %H:%M:%S %Y") + " " + zone + "\n"
            message += "\n"
            message += "    " + contents["short_msg"] + "\n"
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