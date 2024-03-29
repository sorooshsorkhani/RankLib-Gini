"""
Creator: Soroosh Sorkhani
Email: soroosh.sorkhani@gmail.com or soroosh.sorkhani@ryerson.ca
"""
import sys
from os import path
import re
import math
import xml.etree.ElementTree as ET


# First, check if the inputs are correct

try:
    num_features = int(sys.argv[1])  # number of features you have in your data
except:
    print('number of features must be an integer greater than 4')  # because ranklib model uses at least 4 features
    sys.exit()
try:
    dataset_file = open(sys.argv[2])  # the data used for training the ranklib model
except:
    print('dataset is missing')
    sys.exit()
try:
    model_file = open(sys.argv[3])  # the random forests model saved by RankLib
except:
    print('model is missing')
    sys.exit()
try:
    path2trees = sys.argv[4]  # the directory that trees will be saved
except:
    print("path to trees is missing")
    sys.exit()
if not path.exists(path2trees):
    print("path to trees doesn't exist")
    sys.exit()
try:
    gini_file_name = sys.argv[5]  # choose a name or directory(optional) for the output
except:
    print("the output file is not determined")
    sys.exit()
if gini_file_name.find(".txt") == -1:
    print("the output file must be a .txt file")
    sys.exit()


# making the dataset from training data
# the dataset format of ranklib is read and saved as a dictionary here:

training_dataset = dict()
match_list = dataset_file.readlines().copy()
d = 0  # helps to distinguish between each line (query-document pair) in the dataset
for m in range(len(match_list)):
    q = match_list[m].strip().split(" ")[1][4:]  # q is a query
    d += 1  # d is assigned to a document
    id = (q, str(d))  # combination of a query and a document is a record (match) in the dataset
    label = match_list[m].strip().split(" ")[0]  # the rank label/score
    training_dataset[id] = dict()
    training_dataset[id]["label"] = label
    for f in range(num_features):
        training_dataset[id][str(f+1)] = float(match_list[m].strip().split(" ")[2 + f].split(":")[-1])

# Read the model and save trees in separated xml files

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
            tree_file = open(path2trees + "\\tree" + str(math.trunc((i+1)/2)) + ".xml", "w")
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


def node_extraction(node):  # reading the information for each node from the parsed tree
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
    main_gini = 1 - main_gini  # gini impurity of the node

    left_gini = 0
    for i in letf_dict.keys():
        left_gini += (letf_dict[i]/len(left))**2
    left_gini = 1 - left_gini  # gini impurity of the left child

    right_gini = 0
    for i in right_dict.keys():
        right_gini += (right_dict[i]/len(right))**2
    right_gini = 1 - right_gini  # gini impurity of the right child

    gini_children = (len(left)*left_gini + len(right)*right_gini)/(len(left)+len(right))
    importance = main_gini - gini_children  # the change in gini impurity after the split = importance

    return len(main), importance

# steps are:
# parsing a tree
# read nodes and find out the portion of data that go to the nodes
# reading nodes include identifying their parent node and child nodes (if applicable)
# after going down the tree and reading all the nodes:
# go back up the tree and calculate gini for each feature in a split (node)
# the set of gini importances of a feature is saved as a dictionary called "importance"

importance = dict()
how_many_trees = 0
for i in range(int(num_bags)):
    mark = 0
    print("Parsing tree" + str(i + 1))

    tree1 = ET.parse(path2trees + "\\tree" + str(i + 1) + ".xml")
    tree1_root = tree1.getroot()

    root_parent = tree1_root[0][0]
    node = root_parent
    node_data = list(training_dataset.keys()).copy()
    parent = "tree"

    node_dict = dict()

    while True:
        if node not in node_dict.keys():  # if the node is not in the node-set
            node_dict = {**node_dict, **node_extraction(node)}  # read the node
        else:
            pass
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
        else:  # if it's a leaf node, go back to the parent node
            node = node_dict[node]["parent_node"]
            continue

print("Processing trees are done.\n")



# Calculating weighted average of all the nodes split by the same feature over the entire trees

features_list = list() #  this is the list of used features
for f in importance.keys():
    features_list.append(int(f))


gini_file = open(gini_file_name, "w")
feature_importance = dict()
for feature in sorted(features_list):
    feature = str(feature)
    numerator = 0
    denominator = 0
    for (count, importance_value) in importance[feature]:
        numerator += count * importance_value
        denominator += count

    feature_importance[feature] = numerator/denominator

    gini_file.write(feature + "\t" + str(feature_importance[feature]) + "\n")

gini_file.close()
print("gini file is ready")
