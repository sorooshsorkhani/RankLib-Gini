# RankLib-Gini
Gini feature importance for [RankLib](https://sourceforge.net/p/lemur/wiki/RankLib/) random forest:

Ranklib provides a feature manager that generates feature use statistics. This only provides the frequency of each feature used in the learning to rank model to identify which feature contributes more in the model. The importance or efficacy of the feature, however, might not be correlated with its frequency.

Gini importance of a feature is, on the other hand, more commonly used and accepted in learning to rank researches as the criterion of the most affective features.

## How to Use

### Run
You will need python3 to run this code. The model used in this code is created by ranklib-2.1 or higher versions.

You can run the code in terminal by putting the inputs in the same order as below:
                 
    python Gini.py <num_features> <path_to\training_data> <path_to\RF_model> <trees directory> <output_file>

An example with the dataset and model provided in this repository:
     
    python Gini.py 67 train_data.txt model.txt trees gini.txt

This program is also tested on MQ2008 from the [LETOR](https://www.microsoft.com/en-us/research/project/letor-learning-rank-information-retrieval/?from=http%3A%2F%2Fresearch.microsoft.com%2Fen-us%2Fum%2Fbeijing%2Fprojects%2Fletor%2Fletor4dataset.aspx) 4.0 dataset.

### Input Description
* **num_features**: The number of features exist in your training data. Note that this is not necessarily equal to the number of features used in the model.

* **training data**: The training data used for the ranklib model.

* **RF model**: The model created by ranklib.

* **trees directory**: The directory that you want to save your trees. You may need an empty directory as usually many trees will be created.

* **output file**: A .txt file to save the results of the gini importance.


## Sponsor
Laboratory for Systems, Software and Semantics ([LS3](http://ls3.rnet.ryerson.ca/)), Ryerson University, ON, Canada
