
"""
Basic statistical functions

Include:
Starters - line 13;
Data inspection - line 28;
Visualisation with ggplot - line 120;
Data analysis - line 158;

"""
##############################################################################
                              #Starters
##############################################################################

import os

#current working directory
directory_path = os.getcwd()
print(directory_path)
folder_name = os.path.basename(directory_path)
print(folder_name)

# Changing the CWD
os.chdir('/path-to-dir/')

##############################################################################
                              #Data inspection
##############################################################################

import datapackage
import pandas as pd

#data IRIS set
data_url = 'https://datahub.io/machine-learning/iris/datapackage.json'

# to load Data Package into storage
package = datapackage.Package(data_url)

# to load only tabular data
resources = package.resources
for resource in resources:
    if resource.tabular:
        data = pd.read_csv(resource.descriptor['path'])

#view data
print (data)

#view column names        
print(data.columns.values)

#Get the data shape(number of rows, of columns)
print(data.shape)

#view only part of data
#data[start:end] where end is not included
print(data[10:21]) #rows from 10 to 20

sliced_data=data[10:21] # saved in a variable

#view data by index of column 
data.iloc[5] #display records only with species "Iris-setosa".
data.loc[data["class"] == "Iris-setosa"]

#count number of times a particular species 
#has occurred in a column
data["class"].value_counts()#in descending order.

#Basic statisctics 
sum_data = data["sepallength"].sum()
mean_data = data["sepallength"].mean()
median_data = data["sepallength"].median()  
print("Sum:",sum_data, "\nMean:", mean_data, "\nMedian:",median_data)

min_data=data["sepallength"].min()
max_data=data["sepallength"].max()
print("Min:", min_data, "Max:", max_data)

#Add another column
data1 = data[data.columns[0:4]]#new dataframe variabe
data["total_values"]=data1[data.columns[0:4]].sum(axis=1)#add new column
#axis=1 rows, axis=0 columns

#rename column names
newcols={
"sepallength":"SepalLength",
"sepalwidth":"SepalWidth"}
  
data.rename(columns=newcols,inplace=True) 

#check if missing values
data.isnull()

#function to display basic statistics
import numpy as np
def Stats(a):
        import numpy as np
        a_min = np.min(a)
        a_max = np.max(a)
        a_mean = np.mean(a)
        a_med = np.median(a)
        a_std = np.std(a)
        a_var = np.var(a)
        
        print("Min:",a_min,
              "\nMax:",a_max,
              "\nMean:",a_mean,
              "\nMedian:", a_med,
              "\nStandard deviation:", a_std,
              "\nVariance:", a_var)

a=[5676,78,878,45,55,67878,34,67,8996,44,4,3,456,876]
Stats(a)

#75% of values are under resulting number ___
percentile_a75 = np.percentile(a,75)
print(percentile_a75)

##############################################################################
                              #Visualisation with ggplot!
##############################################################################

from plotnine import *
  
# passing the data to the ggplot 
# constructor
ggplot(iris)+ aes(x="class", y="SepalLength")+ geom_col()
ggplot(iris)+ aes(x="class", y="SepalLength")+ geom_point()


(
 ggplot(iris)
 + aes(x="class", y="SepalLength")
 + geom_boxplot(fill="yellow")
 + coord_flip()
 + theme_xkcd()
 )


(
 ggplot(iris) 
 + aes(x="SepalLength") 
 + geom_histogram(color="darkgrey", fill="lightgreen", alpha=0.6)
 )


plot=(
 ggplot(iris)
 + aes(x="petallength", y="SepalLength", fill="class")
 + geom_col()
 )
print(plot)

#save as png
plot.save(path="/path-to-dir/",filename="test_plot.png")

##############################################################################
                              #Data analysis
##############################################################################

#linear regression
import numpy as np
from sklearn.linear_model import LinearRegression

x=np.array(iris['SepalWidth']).reshape((-1, 1))
y=np.array(iris['SepalLength'])
sp=np.array(iris['class'])

x
y

model = LinearRegression()
model.fit(x, y)
model = LinearRegression().fit(x, y)
r_sq = model.score(x, y)
print(f"coefficient of determination: {r_sq}",
      "\n"f"intercept: {model.intercept_}",
      "\n"f"slope: {model.coef_}")

#predict response
y_pred = model.predict(x)
#print(f"predicted response:\n{y_pred}")
#y_pred = model.intercept_ + model.coef_ * x

(#visualise prediction
 ggplot()
 + aes(x="y", y="y_pred", color="sp") 
 + geom_point()
 + geom_line()
 + xlim(5, 8)
 + ylim(5, 8)
 )

#K-means
import matplotlib.pyplot as plt

x = [4, 5, 10, 4, 3, 11, 14 , 6, 10, 12]
y = [21, 19, 24, 17, 16, 25, 24, 22, 21, 21]

plt.scatter(x, y)
plt.show()

from sklearn.cluster import KMeans

#Turn the data into a set of points:
data = list(zip(x, y))

#In order to find the best value for K, 
#we need to run K-means across our data 
#for a range of possible values. 
#We only have 10 data points, 
#so the maximum number of clusters is 10. 
#So for each value K in range(1,11), 
#we train a K-means model and plot the intertia 
#at that number of clusters:
inertias = []

for i in range(1,11):
    kmeans = KMeans(n_clusters=i)
    kmeans.fit(data)
    inertias.append(kmeans.inertia_)

plt.plot(range(1,11), inertias, marker='o')
plt.title('Elbow method')
plt.xlabel('Number of clusters')
plt.ylabel('Inertia')
plt.show()

#We can see that the "elbow" on the graph above
#(where the interia becomes more linear) 
#is at K=2. We can then fit our K-means algorithm
#one more time and plot the different clusters
#assigned to the data:
kmeans = KMeans(n_clusters=2)
kmeans.fit(data)

plt.scatter(x, y, c=kmeans.labels_)
plt.show()
