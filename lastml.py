# -*- coding: utf-8 -*-
"""LastML.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10pSK-P95n-qMarxEz-87KqMlkziElsP3

Importing library
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import seaborn as sns
pd.set_option('display.max_columns', None)
import plotly.express as px
import matplotlib.pyplot as plt
# %matplotlib inline
import warnings
warnings.filterwarnings('ignore')

"""data and test data(read)"""

data = pd.read_csv('/content/kaggle_train_data_public.csv')
test_data = pd.read_csv('/content/kaggle_test_features_public.csv')

"""feature of data"""

def getDataframeOverview(df, message):
    print(message)
    print('Number of rows: ', df.shape[0])
    print('Number of features:', df.shape[1])
    print('Data Features:')
    print(df.columns.tolist())
    print('Missing values:', df.isnull().sum().values.sum())
    print('Unique values:')
    print(df.nunique())

getDataframeOverview(data, 'Overview of the train dataset')
print('-'*100)
getDataframeOverview(test_data, 'Overview of the test dataset')

"""data.columns

remove columns
"""

data.drop(['CustomerID', 'Count', 'Country', 'State', 'City', 'Zip Code', 'Lat Long', 'Latitude', 'Longitude', 'Churn Score', 'CLTV', 'Churn Reason'],axis=1,inplace = True)
test_data.drop(['CustomerID', 'Count', 'Country', 'State', 'City', 'Zip Code', 'Lat Long', 'Latitude', 'Longitude'],axis=1,inplace = True)

data['Total Charges'] = data['Tenure Months'] + data['Monthly Charges']
test_data['Total Charges'] = test_data['Tenure Months'] + test_data['Monthly Charges']

data['Sub Charges'] =data['Monthly Charges'] - data['Tenure Months']
test_data['Sub Charges'] =test_data['Monthly Charges'] - test_data['Tenure Months']

"""change boolen to 0 and 1"""

binary_list = ['Senior Citizen', 'Partner', 'Dependents', 'Phone Service', 'Paperless Billing']

def binary_map(feature):
    return feature.map({'Yes':1, 'No':0})

data['Gender'] = data['Gender'].map({'Male':1, 'Female':0})
test_data['Gender'] = test_data['Gender'].map({'Male':1, 'Female':0})

data[binary_list] = data[binary_list].apply(binary_map)
test_data[binary_list] = test_data[binary_list].apply(binary_map)

data = pd.get_dummies(data, drop_first=True)
test_data = pd.get_dummies(test_data, drop_first=True)

"""minmax scaler(between 0 and 1)"""

from sklearn.preprocessing import MinMaxScaler,StandardScaler
mms = MinMaxScaler() # Normalization

data['Tenure Months'] = mms.fit_transform(data[['Tenure Months']])
data['Monthly Charges'] = mms.fit_transform(data[['Monthly Charges']])
data['Total Charges'] = mms.fit_transform(data[['Total Charges']])
data['Sub Charges'] = mms.fit_transform(data[['Sub Charges']])

test_data['Tenure Months'] = mms.fit_transform(test_data[['Tenure Months']])
test_data['Monthly Charges'] = mms.fit_transform(test_data[['Monthly Charges']])
test_data['Total Charges'] = mms.fit_transform(test_data[['Total Charges']])
test_data['Sub Charges'] = mms.fit_transform(test_data[['Sub Charges']])

churnValue = data['Churn Value']
data.drop(['Churn Value'], axis = 1, inplace = True)
data['Churn Value'] = churnValue

data.shape

"""imbalance"""

import imblearn
from collections import Counter
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline

over = SMOTE(sampling_strategy='auto')

x = data.iloc[:,:31].values
y = data.iloc[:,31].values

x, y = over.fit_resample(x, y)
Counter(y)

print(data.shape)
print(test_data.shape)

# Import Machine learning algorithms
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from xgboost import XGBClassifier
#Neural Networks(din't do)
from keras.models import Sequential
from keras.layers import Dense

# Import metric for performance evaluation
from sklearn.metrics import accuracy_score
from sklearn.metrics import RocCurveDisplay

# Model selection
from sklearn.model_selection import RepeatedStratifiedKFold

# Split data into train and test sets
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.001, random_state=42)

def model(classifier,x_train,y_train,x_test,y_test):
  mod = classifier.fit(x_train,y_train)
  prediction = classifier.predict(x_test)
  cv = RepeatedStratifiedKFold(n_splits = 10,n_repeats = 3,random_state = 1)
  print("Accuracy: {:.2%}".format(accuracy_score(y_test, prediction)))
  RocCurveDisplay.from_estimator(classifier, x_test,y_test)
  return mod

#kNN
knn_classifier = KNeighborsClassifier(n_neighbors=3)
knn_model = model(knn_classifier,X_train,y_train,X_test,y_test)

# XGBClassifier
classifier_xgb = XGBClassifier(learning_rate= 0.01,max_depth = 5,n_estimators = 10000,booster='gbtree',objective='binary:logistic', random_state=82)
xgb_model = model(classifier_xgb,X_train,y_train,X_test,y_test)

#Logistic Regression
classifier_lg = LogisticRegression(tol=0.0034, C=2.1, intercept_scaling=10)
lg_model = model(classifier_lg,X_train,y_train,X_test,y_test)

# DecisionTreeClassifier
classifier_dt = DecisionTreeClassifier(random_state = 100,max_depth = 4,min_samples_leaf = 1)
dt_model = model(classifier_dt,X_train,y_train,X_test,y_test)

# RandomForestClassifier

classifier_rf = RandomForestClassifier(max_depth = 4,random_state = 42)
rf_model = model(classifier_rf,X_train,y_train,X_test,y_test)

# SVC

classifier_svc = SVC(probability=True)
svc_model = model(classifier_svc,X_train,y_train,X_test,y_test)

# Naive bayes

classifier_gnb = GaussianNB()
gnb_model = model(classifier_gnb,X_train,y_train,X_test,y_test)

predictions_proba = lg_model.predict_proba(test_data)[:, 1]
submission_df = pd.DataFrame({'ID': range(len(test_data)), 'Churn Value': predictions_proba})
submission_df.to_csv("submission_file_name.csv", index=False)