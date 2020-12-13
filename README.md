# RankLib-Gini
Gini feature importance for [RankLib](https://sourceforge.net/p/lemur/wiki/RankLib/) random forests:

Ranklib provides a feature manager that generates feature use statistics. This only provides the frequency of each feature used in the learning to rank model to identify which feature contributes more in the model. The importance or efficacy of the feature, however, might not be correlated with its frequency.

Gini importance of a feature is, on the other hand, more commonly used and accepted in learning to rank researches as the criterion of the most affective features.

## How to use

Input:

    1- training data used as input for Ranklib
      
    2- random forests trained by Ranklib
      
    3- number of features you have in your data (num_features = n)
    
Note that number of features existing in the dataset may be differ from the features you (or Ranklib) actually used in the model (i.e. not all the features necessarily used in the model).

Output:

    1- prints the gini importance for each feature
