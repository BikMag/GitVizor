import os
import re
import sys
from hashlib import sha1
import graphviz
import zlib

graph = graphviz.Digraph("GitVizor")


class Node:
    def __init__(self, id, message):
        self.id = id
        self.message = message
        self.branches = []
        self.parents = []
        self.changed_files = dict()

    def add_branch(self, branch):
        self.branches.append(branch)

    def add_parents(self, parents):
        self.parents = parents

    def add_changed_files(self, changed_files):
        self.changed_files = changed_files


# repository = "D:/МИРЭА/Фронт/Мой сайт/.git/"
repository = sys.argv[1]


def newDECODE(object_filename):
    compressed_contents = open(object_filename, 'rb').read()
    decompressed_contents = zlib.decompress(compressed_contents)

    text = [word for word in re.split(b'\x00| ', decompressed_contents)]

    changed_files = dict()
    # print(text[3:])

    blob = ""
    for word in text[3:]:
        try:
            blob = word.decode()
        except UnicodeDecodeError:
            # print(len(word))
            if len(blob) > 0:
                if len(word) > 20:
                    word = word[:20]

                # blob += ": " + sha1(word).hexdigest()
                changed_files[blob] = sha1(word).hexdigest()
                # print(blob)
            blob = ""

    print(changed_files)
    return changed_files


def decode(object_filename):  # Расшифровка данных из объекта Git
    with open(object_filename, 'rb') as object_file:
        bin_content = zlib.decompress(object_file.read())

    text = bin_content.split(b'\x00', maxsplit=1)

    obj_type = text[0].decode().split()[0]
    obj_content = text[1].decode()

    # print(obj_type)
    # print(obj_content)

    return obj_content


def get_field(key_word, content):
    indices = [i for i, x in enumerate(content.split()) if x == key_word]
    hashcodes = [content.split()[i + 1] for i in indices]
    return hashcodes


def draw_graph(nodes):
    for commit in nodes.values():
        print(vars(commit))
        content = f"{commit.id}:\n{commit.message}\n({', '.join(commit.branches)})"
        graph.node(commit.id, content)

    for commit in nodes.values():
        print(f"\n==={commit.message}===")
        for parent_commit in commit.parents:
            if parent_commit in nodes:
                # Ищем измененные файлы
                files = ""
                child_commit = commit.id

                hashfile1 = ""
                hashfile2 = ""
                for file in commit.changed_files.keys():
                    print(f"{file}:", end=" ")
                    if file in commit.changed_files.keys():
                        print(commit.changed_files[file], end=" ")
                        hashfile1 = commit.changed_files[file]
                    else:
                        print("NONE")
                    if file in nodes[parent_commit].changed_files.keys():
                        print(nodes[parent_commit].changed_files[file])
                        hashfile2 = nodes[parent_commit].changed_files[file]
                    else:
                        print("NONE")

                    if hashfile1 != hashfile2:
                        files += f"{file}: {commit.changed_files[file]}\n"

                graph.edge(child_commit, parent_commit, files)

    graph.render(directory="graph-output", view=True)


def main():
    nodes = dict()
    edges = []

    first_path = open(repository + "HEAD", "r").read().split()[1]

    print(os.listdir(f"{repository}refs/heads/"))

    branches = os.listdir(f"{repository}refs/heads/")
    i = 0  # Вытаскиваем ветки из подкаталогов
    while i < len(branches):
        branch = branches[i]
        if os.path.isdir(f"{repository}logs/refs/heads/{branch}"):
            branches.pop(i)
            for new_branch in os.listdir(f"{repository}logs/refs/heads/{branch}"):
                branches.append(f"{branch}/{new_branch}")
        i += 1

    for branch in branches:
        hashcode = open(repository + "refs/heads/" + branch, "r").read()[:-1]
        # hashcode = "1ba34fcbfca2e2afd3c8d2dcf51676367f906438"
        prev_commit = ""

        while hashcode is not None:
            object_file = repository + "objects/" + hashcode[:2] + "/" + hashcode[2:]
            content = decode(object_file)
            commit_message = content.split('\n')[-2]

            if hashcode not in nodes.keys():
                nodes[hashcode] = Node(hashcode, commit_message)
            nodes[hashcode].add_branch(branch)
            nodes[hashcode].add_parents(get_field("parent", content))

            # tree
            # print(commit_message + ':')
            trees = get_field("tree", content)
            print(f"{trees=}")
            for tree in trees:
                files = newDECODE(repository + "objects/" + tree[:2] + "/" + tree[2:])
                nodes[hashcode].add_changed_files(files)

                print('-' * 20)
                print(files)
                print('-' * 20)

            cur_commit = hashcode
            if prev_commit != "" and f"{cur_commit} {prev_commit}" not in edges:
                edges.append(f"{cur_commit} {prev_commit}")

            prev_commit = cur_commit

            if len(get_field("parent", content)) == 0:
                break

            hashcode = get_field("parent", content)[0]

    draw_graph(nodes)


if __name__ == '__main__':
    main()

