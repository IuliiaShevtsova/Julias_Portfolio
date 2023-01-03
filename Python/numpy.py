
"""
Numpy
--------------

NumPy is much faster than lists because:
-it uses less bytes of memory
-no type checking there
-contiguous memory (SIMD vector processing, effective cache utilization)

Applications:
-maths
-plotting
-backend(pandas, connect 4, digital photography)
-machine learning

"""
import numpy as np

########## Basics ###############

##initialise an array
a = np.array([1,2,3])
print(a)

b = np.array([[3,5,4.9,6,7,3], [4,6,5,7,3,8]])
print(b)

#get dimension
a.ndim

#get shape
b.shape#(rows,columns)

#get type
a.dtype

#get size
a.itemsize

a.size

#get total size
a.nbytes
b.nbytes

##Accessing/changing specific elements, rows, columns, etc.

a = np.array([[3,4,6,6,4,8,4,9,3,2], [3,4,12,8,4,8,33,3,2,5]])
print(a)

#get a spezific element
a[1,9]#second row, column 10

#get a spezific row
a[0,:]

#get a column
a[:,1]

#all elements between spezific indexes by step
a[0,1:6:2]#2 is a step

#change elements
a[1,5] = 20

a[:,2] = [1,2]
print(a)

#3d example
c=np.array([[[1,5],[1,8]],[[1,5],[7,8]]])
print(c)

#get element(outside in)
c[1,1,0]#second block, second row, first row...first element
c[:,1,:]

##Initialise all types of Arrays
#All zero matrix
np.zeros(5)
np.zeros((2,2,2))
#All 1s
np.ones((4,3))
np.ones((4,2,3), dtype="int32")
#Any other number
np.full((2,2),88, dtype="float32")
#Any by reusing shapes
np.full_like(a,4)
#Random decimal numbers
np.random.rand(4,2,5)
np.random.random_sample(a.shape)
#Random integer values
np.random.randint(-7,6, size=(3,3))
np.random.randint(8, size=(3,3))
#Identity matrix
np.identity(5)

#Repeat an array
arr=np.array([[1,2,3]])
r1=np.repeat(arr,3, axis=0)


#------Example----------
""" Doing this matrix
array([[1., 1., 1., 1., 1.],
       [1., 0., 0., 0., 1.],
       [1., 0., 9., 0., 1.],
       [1., 0., 0., 0., 1.],
       [1., 1., 1., 1., 1.]])
"""
output= np.ones((5,5))
z=np.zeros((3,3))
z[1,1]=9
output[1:-1,1:-1]=z
output

#Copying arrays
a=np.array([1,2,3])
#b=a
b[0]=100#changes b AND a!!!
#insted use copy()
b=a.copy()

#Flattening the array: converting into one dimensional array
a1=np.array([[1,2,3],['a','b','c']])
a2=a1.flatten()
print(a2)

#Sorting the array
a1=np.array([4,21,2,5,10,6,2])
a1.sort()
print(a1)

##Mathematics
a=np.array([1,2,3,4])
a+2#each element +2
a-2#each element -2
a*2#each element is multiplied by 2
a/2#each element is devided by 2

b=np.array([2,4,5,3])

a+b#each element of a + each element of b which are on the same positions

a**2#each element is in second degree

#take the sin
np.sin(a)
np.cos(a)

#Linear algebra
a=np.ones((2,3))
a
b=np.full((3,2), 2)
b

np.matmul(a,b)#multiply a amd b

c=np.identity(3)
np.linalg.det(c)#determinant

"""
More: https://docs.scipy.org/doc/numpy/reference/routines.linalg.html
"""
##Statistics
stats=np.array([[1,2,4],[4,6,2]])
np.min(stats)#min of all elements
np.max(stats)#max of all elements
np.min(stats, axis=1)#min in every row
np.min(stats, axis=0)#min in every column
np.sum(stats)#sum of all elements in the matrix
np.sum(stats, axis=0)#sum by column
np.sum(stats, axis=1)#sum by row

#Reoeganizing arrays
before=np.array([[1,2,3,4],[3,4,6,2]])
after=before.reshape((4,2))
after2=before.reshape((2,2,2))

#Vertical stack
v1=np.array([1,2,3,4])
v2=np.array([8,9,3,3])

np.vstack([v1,v2])
np.vstack([v1,v2, v2])

#Horizontal stack
h1=np.array((2,4))
h2=np.array((2,2))

np.hstack((h1,h2))

########## Miscellaneous ##########

#Load file
filedata=np.genfromtxt("data_sample.txt", delimiter=",")
filedata=filedata.astype("int32")

#Boolean Masking and advanced indexing
filedata>50#boolean true of false matrix
filedata[filedata>50]#same as in R, choosing elements which are true by condition

#index with a list
a=np.array([1,2,3,5,6,7,8,4,3,3])
a[[1,2,8]]#gives a matrix with elements on places/indexes 1,2,8

np.any(filedata>50, axis=0)#any value bigger than 50 - True for the column
np.all(filedata>50, axis=0)#all values in the column bigger than 50 -> True, otherwise False

np.any(filedata>50, axis=1)#any in a row

~((filedata>30) & (filedata<1000))#not these which true by conditions

#Advanced indexing
a[2:4,0:2]
a[[0,1,2,3],[1,2,3,4]]
a[[0,4,5],3:]













