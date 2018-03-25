#Updated: 
#Improved the regex to remove the URLs from the traffic tweets. 
#Added more data for building the trainingn anf testing data sets

require(futile.logger)
require(tm)
require(rmongodb)
require(RCurl)
require(jsonlite)
dummy <- Sys.setlocale("LC_TIME", "English_United Kingdom.1252")
dummy <- Sys.setlocale("LC_ALL", "English_United Kingdom.1252")
setwd("C:\\Users\\Ahmad\\Dropbox\\Work\\WolverhamptonUni\\docs\\D3.3\\Analysis\\RelevanceFiltration\\Try4MonkeyLearnNGramVariation")

#read the training anf testing datasets from CSV files

train <- read.table(file = "df_tweets_for_training.csv", 
            quote = "\"'", sep = ",", header = TRUE, fileEncoding = "utf8", stringsAsFactors = FALSE)

test <- read.table(file = "df_tweets_for_classification.csv", 
            quote = "\"'", sep = ",", header = TRUE, fileEncoding = "utf8", stringsAsFactors = FALSE)

#For the first experiment only:
test <- test[sample(nrow(test), 5000), ]
test$no <- seq.int(nrow(test))
rownames(test) = 1:nrow(test)
test$predictedClass <- rep("",nrow(test))
test$predictedClassProb <- rep(0.0,nrow(test))

#For the subsequent experiments:
rm(test)
load("classifications20160701UniBi.Rda")
test$predictedClass <- rep("",nrow(test))
test$predictedClassProb <- rep(0.0,nrow(test))

#Classify the testing dataset using MonkeyLearn classifier
#send 200 tweets with every request
#sleep for 65 seconds every 4000 classifications

classifications <- data.frame(
  predictedClass = character(0),
  predictedClassProb = numeric(0),
  stringsAsFactors = F
)
tweets <- character(0)
for (i in 1:nrow(test)) {
  if (i %% 200 == 0 | i == nrow(test)) {
    tweets <- c(tweets, test[test$no == i,c("text")])
    x= list(text_list=tweets)
    headers <- list('Authorization' = "Token xxx", 
                    'Content-Type' = 'application/json')
    response <- postForm("https://api.monkeylearn.com/v2/classifiers/XXX/classify/?sandbox=1", 
                         .opts=list(postfields=toJSON(x), httpheader=headers))
    
    responseJson <- fromJSON(response)
    
    for (j in 1:length(responseJson[[1]])) {
      classifications <- rbind(classifications, data.frame(
        predictedClass = responseJson[[1]][[j]]$label,
        predictedClassProb = responseJson[[1]][[j]]$probability,
        stringsAsFactors = FALSE
      ))
      # cat(paste0("Tweet ",j,":\n","\tLabel: ",responseJson[[1]][[j]]$label,"\t
						Probability: ",responseJson[[1]][[j]]$probability,"\n"))
    }
    tweets <- character(0)
    flog.info("No of tweets classified: %s (%s)", i, round(i/nrow(test) * 100.00, 2))
    if (i %% 4000 == 0) {
      flog.info("Sleeping for 65 seconds...")
      Sys.sleep(65)
    }
  } else {
    tweets <- c(tweets, test[test$no == i,c("text")])
  }
}

# Fill the data table with the classifications

for (i in 1:nrow(test)) {
  test$predictedClass[i] <- classifications$predictedClass[i]
  test$predictedClassProb[i] <- classifications$predictedClassProb[i]
}

# Save the data frame for evaluation metrics
save(test, file="classifications20160701Tri.Rda")

#Evaluation Metrics

# confusion matrix
cat("Confusion Matrix (Actual / Predicted:\n")
# table(test$actual,test$predictedClass)

true_positive <- nrow(test[test$actual == 'Good' & test$predictedClass == 'Good',])
false_positive <- nrow(test[test$actual == 'Bad' & test$predictedClass == 'Good',])

true_negative <- nrow(test$actual == 'Bad' & test$predictedClass == 'Bad')
false_negative <- nrow(test$actual == 'Good' & test$predictedClass == 'Bad')

cat("Good Class:\n")
cat(paste0("\tPrecision:"))




