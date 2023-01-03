
"""
Pandas
"""
import pandas as pd

##reading files
df = pd.read_csv("data.csv") #--------------csv
#df = pd.read_excel("data.xlsx")#-----------excel
#df = pd.read_csv("data.txt", delimeter =";")#----txt with delimitor ;
#df = pd.read_csv("data.txt", delimeter ="\t")#---tab delimited

##preview data
print(df.head(3))#------first free rows + header

##read headers
df.columns
#Result:Index(['Car', 'Model', 'Volume', 'Weight', 'CO2'], dtype='object')

##read each column
df["Model"]
df.Model#does work only for one-word names
df[["Model", "Volume"]]#multiple columns

##read each row
df.iloc[0]#information from the row with index 0: same as first row
df.iloc[1]#information from the row with index 1: same as second row
df.iloc[2:5]#multiple rows, end NOT included:3 to 5 with indexes 2 to 4

for index, row in df.iterrows():
    print(index,row ["Model"])
    
df.loc[df["Car"]=="Skoda"]#only info for those cars, which Skoda
df.loc[df["Volume"]==1000]#only info for those cars, which Volume is 1000
df.loc[df["Volume"]>1000]#only info for those cars, which Volume is more than 1000

##read a specific location
df.iloc[2,1]#get smth in the row with index 2, column with index 1

##basic stats overview
df.describe()

##sorting
df.sort_values("CO2")#ascending
df.sort_values("CO2", ascending=False)#descending
df.sort_values(["Car", "Volume"])#alphabetically ascending
df.sort_values(["Car", "Volume"], ascending=[1,0])#by car ascending, volume - descending

##adding colums
df["Name"] = df["Car"]+ " " + df["Model"]#create column which combine name from car and model

df["Total"] = df.iloc[:,2:5].sum(axis=1)#summarising values from columns with indexes from 2 to 4 in a new column

##delete column
df = df.drop(columns=["Name"])#delete by name of the column: in this case column with the name "Name"

##reorder columns
#cols = list(df.columns.values)
#df = df[cols[0:2]+[cols[-1]]+[cols[3]]]

##save to csv
df.to_csv("data_modified.csv", sep=";", index=False)#separated by ";" to read right in excel
df.to_excel("data_mod.xlsx", index=False)
df.to_csv("modified.txt", index=False, sep="\t")

#########Filtering data############
df.loc[(df["Weight"]>900) & (df["Car"]=="Ford")]# one condition and another condition

df.loc[(df["Weight"]>900) | (df["Car"]=="Ford")]#one or another

new_df = df.loc[(df["Weight"]>900) & (df["Car"]=="Ford")]

##reset index
new_df = new_df.reset_index(drop=True)
new_df.reset_index(drop=True, inplace=True)#same as above withount creating new df

##filter by parts in string 
df.loc[df["Car"].str.contains("d")]#only cars which contain "d" in name
df.loc[~df["Car"].str.contains("d")]#all cars with name which does NOT contain "d"

df.loc[df["Car"].str.contains("yo|at",regex=True)]#car which contain in name either "yo" or "at"
import re
df.loc[df["Car"].str.contains("to|at", flags=re.I, regex=True)]# same, but also ignore capitalisation

df.loc[df["Car"].str.contains("^M[a-z]*", flags=re.I, regex=True)]#all car names, which start with M

##conditional changes
df.loc[df["Car"]=="Mini", "Car"]="MINI"#in the column "Car" if "Car" labeled "Mini" change it to "MINI"
df.loc[df["Car"]=="MINI", "Car"]="Mini"

df.loc[df["Car"]=="Mini", ["Volume", "CO2"]]= "UNKNOWN"#put unknown CO2 and Volume if the Car is Mini

#agregate statistics
df.groupby(["Car"]).mean()#mean statistics for each Car
df.groupby(["Car"]).mean().sort_values("Volume", ascending=False)#sorted by Volume from the biggest

df.groupby(["Car"]).sum()

#counting occurence in df
df["count"]=1
df.groupby(["Car", "Model"]).count()["count"]#count number of cars

######BIG DATA
#reading in chunks
for df in pd.read_csv("data.csv", chunksize=5):
    print("CHUNK DF")
    print(df)
    
new_df= pd.DataFrame(columns=df.columns)

for df in pd.read_csv("data.csv", chunksize=5):
    results = df.groupby(["Car"]).count()
    
    new_df = pd.concat([new_df, results])































