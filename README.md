# RankLib-Gini
Gini feature importance for [RankLib](https://sourceforge.net/p/lemur/wiki/RankLib/) random forests:

Ranklib provides a feature manager that generates feature use statistics. This only provides the frequency of each feature used in the learning to rank model to identify which feature contributes more in the model. The importance or efficacy of the feature, however, might not be correlated with its frequency.

Gini importance of a feature is, on the other hand, more commonly used and accepted in learning to rank researches as the criterion of the most affective features.

## How to use

You can simply run the code in terminal by:
     
     python Gini.py

It will ask you for input. I provided my own dataset and model for an example. My answers are shown in <>, but you don't need these marks.

    number of features used in the dataset: <68>

Number of features you have in your dataset. Note that number of features existing in the dataset may differ from the features used in the model (i.e. not all the features necessarily used in the model).


    path_to_training_data\data.txt: <train_data.txt>

The data used for training the ranklib model
      
    path_to_model\model.txt: <model.txt>
    
The random forests model saved by RankLib
    
    Trees_directory: <trees>

The directory that trees will be saved. I suggest creating a new directory for this, because it will contain many tree files (300 trees in my example).

    output file name (e.g. gini.txt): <gini.txt>
    
Choose a name or directory(optional) for the output


