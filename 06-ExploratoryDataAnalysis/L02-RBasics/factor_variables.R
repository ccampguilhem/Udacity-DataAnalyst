#Change working directory
if (basename(getwd()) != 'dataset') {
  setwd('./dataset')
}

#Load data file
redditInfo <- read.csv('reddit.csv')

#Structure of dataframe
str(redditInfo)
summary(redditInfo)
head(redditInfo, 10)

#Observe factor variables
table(redditInfo$age.range)
levels(redditInfo$age.range)

#Plotting
library(ggplot2)
qplot(data=redditInfo, x = age.range)
qplot(data=redditInfo, x = income.range)

#Re-ordering groups
redditInfo$age.range <- factor(redditInfo$age.range, levels=c("Under 18", "18-24", "25-34", "35-44", "45-54", 
                                                              "55-64", "65 or Above"), ordered = TRUE)
qplot(data=redditInfo, x = age.range)

levels(redditInfo$income.range)
redditInfo$income.range <- ordered(redditInfo$income.range, c("Under $20,000", "$20,000 - $29,999", 
                                                           "$30,000 - $39,999", "$40,000 - $49,999", 
                                                           "$50,000 - $69,999", "$70,000 - $99,999",
                                                           "$100,000 - $149,999", "$150,000 or more"))
qplot(data=redditInfo, x = income.range)

