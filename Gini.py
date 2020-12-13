import pickle
import re
import math
import xml.etree.ElementTree as ET


# First, making the dataset from training data

num_features = n  # number of features you have in your data


training_dataset = dict()
dataset_file = open("train_data.txt")
match_list = dataset_file.readlines().copy()
for m in range(len(match_list)):
    q = match_list[m].strip().split(" ")[1][4:]  # q is a query
    d = match_list[m].strip().split(" ")[-1][8:]  # d is a document
    id = (q, d)
    label = match_list[m].strip().split(" ")[0]  # the rank label/score
    training_dataset[id] = dict()
    training_dataset[id]["label"] = label
    for f in range(num_features):
        training_dataset[id][str(f+1)] = float(match_list[m].strip().split(" ")[2 + f].split(":")[-1])



# Read the model and separate trees in xml files

path2model = "model.txt"  # the random forests model saved by RankLib
model_file = open(path2model)
model_lines = model_file.readlines().copy()
i = 0

for line in model_lines:
    line = line.rstrip()
    if len(line) == 0:
        continue
    if re.search("^#.*bags =", line):
        num_bags = re.findall("^#.*bags = ([0-9]+)", line)[0]
    if re.search("^#", line):
        continue
    if re.search("^<ensemble>", line):
        i += 1
        # if the tree is about to start, open an xml file for it
        if i % 2 == 1:
            tree_file = open("path_to_directory_of_trees\\tree" + str(math.trunc((i+1)/2)) + ".xml", "w")
            tree_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    # if the tree is about to end, close the xml file
    if re.search("^</ensemble>", line):
        i += 1
        if i & 2 == 0:
            tree_file.write(line)
            tree_file.close()
            continue
    # write the tree (lines from model) in the tree file
    line += "\n"
    tree_file.write(line)
print("Separation of trees is done")


def node_extraction(node):  # a split accounts for a node
    dict_help = dict()
    dict_help[node] = dict()
    if node.find("output") is None:
        node_type = "C"  # C as a connector
        dict_help[node]["feature"] = node[0].text.strip()
        dict_help[node]["threshold"] = float(node[1].text.strip())
        dict_help[node]["left"] = node[2]
        dict_help[node]["right"] = node[3]
    else:
        node_type = "L"  # L as a leaf
        dict_help[node]["output"] = float(node[0].text.strip())
    dict_help[node]["node_type"] = node_type
    dict_help[node]["parent_node"] = parent

    dict_help[node]["node_data"] = node_data.copy()

    return dict_help


def gini_importance(node):  # it must be a "C" type node
    main = [training_dataset[id]["label"] for id in node_dict[node]["node_data"]]
    left = [training_dataset[id]["label"] for id in node_dict[node_dict[node]["left"]]["node_data"]]
    right = [training_dataset[id]["label"] for id in node_dict[node_dict[node]["right"]]["node_data"]]
    main_dict = dict()
    letf_dict = dict()
    right_dict = dict()

    for i in main:
        main_dict[i] = main_dict.get(i, 0) + 1
    for i in left:
        letf_dict[i] = letf_dict.get(i, 0) + 1
    for i in right:
        right_dict[i] = right_dict.get(i, 0) + 1

    main_gini = 0
    for i in main_dict.keys():
        main_gini += (main_dict[i]/len(main))**2
    main_gini = 1 - main_gini

    left_gini = 0
    for i in letf_dict.keys():
        left_gini += (letf_dict[i]/len(left))**2
    left_gini = 1 - left_gini

    right_gini = 0
    for i in right_dict.keys():
        right_gini += (right_dict[i]/len(right))**2
    right_gini = 1 - right_gini

    gini_children = (len(left)*left_gini + len(right)*right_gini)/(len(left)+len(right))
    importance = main_gini - gini_children

    return len(main), importance


importance = dict()
how_many_trees = 0
for i in range(300):
    mark = 0
    print("tree" + str(i + 1))

    tree1 = ET.parse("path_to_directory_of_trees\\tree" + str(i + 1) + ".xml")
    tree1_root = tree1.getroot()

    root_parent = tree1_root[0][0]
    node = root_parent
    node_data = list(training_dataset.keys()).copy()
    parent = "tree"

    node_dict = dict()

    while True:
        if node not in node_dict.keys():  # if the node is not in the node-set
            node_dict = {**node_dict, **node_extraction(node)}  # read the node
        if node_dict[node]["node_type"] == "C":  # if the node is not a leaf node
            if node[2] not in node_dict.keys():  # if the left child is not in the node-set, read it
                parent = node
                node = node[2]

                newdata = [id for id in node_dict[parent]["node_data"] if training_dataset[id][node_dict[parent]["feature"]] <= node_dict[parent]["threshold"]]
                node_data = newdata.copy()

                continue
            elif node[3] not in node_dict.keys():  # if the right child is not in the node-set, read it
                parent = node
                node = node[3]

                newdata = [id for id in node_dict[parent]["node_data"] if training_dataset[id][node_dict[parent]["feature"]] > node_dict[parent]["threshold"]]
                node_data = newdata.copy()

                continue
            else:  # if both left and right nodes are read before, calculate gini and then go to the parent node

                # here starts to calculate gini index
                feature = node_dict[node]["feature"]
                if feature not in importance.keys():
                    importance[feature] = list()
                try:
                    count, importance_value = gini_importance(node)
                    importance[feature].append((count, importance_value))
                except:
                    mark = 1
                node = node_dict[node]["parent_node"]
                if node == "tree":
                    if mark == 1:
                        how_many_trees += 1
                    break
                continue
        else:  # if it's a leaf node
            node = node_dict[node]["parent_node"]
            continue

print("Processing ", how_many_trees, " trees are done.\n")



# Calculating weighted average of all the nodes split by the same feature over the entire trees

feature_importance = dict()
for f in range(num_features):
    feature = str(f+1)
    numerator = 0
    denominator = 0
    for (count, importance_value) in importance[feature]:
        numerator += count * importance_value
        denominator += count

    feature_importance[feature] = numerator/denominator

    print("gini importance of feature ", feature, " is ", feature_importance[feature])
