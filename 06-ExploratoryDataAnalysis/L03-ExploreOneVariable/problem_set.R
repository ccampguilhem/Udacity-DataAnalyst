#Load the data

library(ggplot2) #must load the ggplot package first
data(diamonds) #loads the diamonds data set since it comes with the ggplot package
summary(diamonds)
str(diamonds)
?diamonds

# Get all colors
levels(diamonds$color)

#Price
qplot(x=price, data=diamonds, binwidth=500, color=I("black"), fill=I("magenta")) +
  scale_x_continuous(breaks=seq(0, 20000, 2000))
summary(diamonds$price)

less_than_500 <- nrow(diamonds[diamonds$price < 500,])
less_than_250 <- nrow(diamonds[diamonds$price < 250,])
more_than_15000 <- nrow(diamonds[diamonds$price >= 15000,])

qplot(x=price, data=diamonds, binwidth=50, color=I("black"), fill=I("magenta")) +
  scale_x_continuous(breaks=seq(0, 2000, 100), limits=c(0, 2000))
ggsave("dataset/price_peak.png")

qplot(x=price, data=diamonds, binwidth=100) +
  scale_x_continuous(breaks=seq(0, 20000, 5000)) +
  facet_wrap(~cut)
ggsave("dataset/price_per_cut.png")

diamonds[diamonds$price >= max(diamonds$price),][1, 2]

diamonds[diamonds$price <= min(diamonds$price),]

by(diamonds$price, diamonds$cut, summary)

# Distribution

qplot(x=price, data=diamonds, binwidth=100) +
  scale_x_continuous(breaks=seq(0, 20000, 5000)) +
  facet_wrap(~cut, scales="free")

# Price per carat faceted by cut

qplot(x=price/carat, data=diamonds, binwidth=100) +
  scale_x_continuous(breaks=seq(0, 16000, 4000)) +
  facet_wrap(~cut, scales="free") +
  labs(y="Price per carat")
ggsave("dataset/price_per_carat.png")

# Box plot with colors

qplot(x=color, y=price, data=diamonds, geom="boxplot")
ggsave("dataset/price_per_color.png")

summary(diamonds[diamonds$color == "D",]$price)
summary(diamonds[diamonds$color == "J",]$price)

#Interquartile range

IQR(subset(diamonds, color == "D")$price)
IQR(subset(diamonds, color == "J")$price)

# Price per carat box plot

qplot(x=color, y=price/carat, data=diamonds, geom="boxplot")
ggsave("dataset/price_per_carat_by_color.png")

# Frequency plot of diamonds
qplot(x=carat, data=diamonds, geom="freqpoly", binwidth=0.01) +
  scale_x_continuous(breaks=seq(0,3,0.1), limits=c(0., 3.))
ggsave("dataset/carat_frequency.png")

# New dataset (internet user per 100)

df = read.csv("dataset/Internet_user_per_100.csv", header = T, row.names = 1, check.names = F)
str(df)