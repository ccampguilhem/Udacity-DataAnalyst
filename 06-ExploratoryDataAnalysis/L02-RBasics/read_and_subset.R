#Change current workding directory

#Function to print strings to console
printf <- function(...)print(sprintf(...))

#Print current working directory
printf("Current working directory: %s", getwd())

#Change working directory
setwd('./dataset')

#Load data file
statesInfo <- read.csv('stateData.csv')

#Display info on dataframe
head(statesInfo, 10)

#Subset rows
subset(statesInfo, population >= 10000)

#Another way
statesInfo[statesInfo$population >= 10000, ]

#Now also subset columns and store into a new variable
population <- subset(statesInfo, population >= 10000, select=c(X, population))
head(population, 10)

#Or with other notation
population <- statesInfo[statesInfo$population >= 10000, c("X", "population")]
head(population, 10)

#Save the data frame to a file
write.csv(population, 'output.csv')

