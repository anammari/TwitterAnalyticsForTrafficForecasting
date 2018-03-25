require(futile.logger)
require(wordcloud)
require(RColorBrewer)
require(scales)
require(ggplot2)
dummy <- Sys.setlocale("LC_TIME", "English_United Kingdom.1252")
dummy <- Sys.setlocale("LC_ALL", "English_United Kingdom.1252")

setwd("C:\\Users\\Ahmad\\Dropbox\\Work\\WolverhamptonUni\\docs\\D3.3\\Analysis\\SentimentClassification")

#test
# a <- 1:10
# b <- sqrt(1:200)
# c <- log2(1:500)
# z <- c("a", "b", "c")
# dataList <- lapply(z, get, envir=environment())
# names(dataList) <- z
# boxplot(dataList)


#read the tweets
load(file="relevanceClassificationEnriched20160603.Rda")
#read the sentiment scores
sentiments <- read.csv(file = "TrafficSentimentOutput20160603.csv", header = T, stringsAsFactors = F)

#merge into 1 dataframe
df_senti <- merge(unique_tweets_df, sentiments, by.x = "tweet_no", by.y = "id")

# traffic_terms <- c("congestion", "delays", "accident", "roadworks", "road", "works", "repairs", "barrier", 
#                    "bridge", "management", "safe", "traffic", "drive", "open", "cleared", "flowing", "easing", "ease", "reopened", 
#                    "completed", "remains", "released", "spillage", "closed")

traffic_terms <- c("Congestion", "Delays", "Traffic","Flowing", "Roadworks","Bridge", "Management", "Released", "Accident", "Moving","Open", "Cleared", "Flowing", "Easing", "Flooding")
dataList <- list()
for (i in 1:length(traffic_terms)) {
  vec <- df_senti[grepl(paste0("\\<",traffic_terms[i],"\\>"), df_senti$cleaned_text, ignore.case = TRUE),c("sentiment")]
  dataList[[i]] <- vec
}
names(dataList) <- traffic_terms
#boxplot(dataList)

df <- melt(dataList)
colnames(df) <- c("sentiment","term")
# df$sent_class <- rep("",nrow(df))
# #generate the sentiment class column based on the sentiment score sign:
# for (i in 1:nrow(df)) {
#   if (df$sentiment[i] <= -0.08) {
#     sent_class <- -1
#   } else if (df$sentiment[i] > -0.08 & df$sentiment[i] < 0.08) {
#     sent_class <- 0
#   } else {
#     sent_class <- 1
#   }
#   df$sent_class[i] <- sent_class
# }
df$term <- as.factor(df$term)
#df$sent_class <- as.numeric(df$sent_class)
p <- ggplot(df,aes(x = term, y = sentiment)) + geom_boxplot(aes()) + xlab("Term") + ylab("Sentiment Score")
p <- p + theme(axis.text.x = element_text(size = 16),
               axis.title.x = element_text(size = 14),
               axis.text.y = element_text(size = 16),
               axis.title.y = element_text(size = 16))
print(p)

traffic_terms <- c("Bridge", "Management", "Released", "Accident", "Moving","Open", "Cleared", "Flowing", "Easing", "Flooding")
dataList <- list()
for (i in 1:length(traffic_terms)) {
  vec <- df_senti[grepl(paste0("\\<",traffic_terms[i],"\\>"), df_senti$cleaned_text, ignore.case = TRUE),c("sentiment")]
  dataList[[i]] <- vec
}
names(dataList) <- traffic_terms
df <- melt(dataList)
colnames(df) <- c("sentiment","term")
df$term <- as.factor(df$term)
p <- ggplot(df,aes(x = term, y = sentiment)) + geom_boxplot(aes()) + xlab("Term") + ylab("Sentiment Score")
p <- p + theme(axis.text.x = element_text(size = 14),
               axis.title.x = element_text(size = 14),
               axis.text.y = element_text(size = 14))
print(p)

traffic_terms <- c("Open", "Cleared", "Flowing", "Easing", "Flooding")
dataList <- list()
for (i in 1:length(traffic_terms)) {
  vec <- df_senti[grepl(paste0("\\<",traffic_terms[i],"\\>"), df_senti$cleaned_text, ignore.case = TRUE),c("sentiment")]
  dataList[[i]] <- vec
}
names(dataList) <- traffic_terms
df <- melt(dataList)
colnames(df) <- c("sentiment","term")
df$term <- as.factor(df$term)
p <- ggplot(df,aes(x = term, y = sentiment)) + geom_boxplot(aes()) + xlab("Term") + ylab("Sentiment Score")
p <- p + theme(axis.text.x = element_text(size = 14),
               axis.title.x = element_text(size = 14),
               axis.text.y = element_text(size = 14))
print(p)

