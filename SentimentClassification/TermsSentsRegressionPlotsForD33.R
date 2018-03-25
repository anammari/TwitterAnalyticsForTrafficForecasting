require(ggplot2)
dataDir <- "C:/Users/Ahmad/Dropbox/Work/WolverhamptonUni/data/twitter/"
setwd("C:\\Users\\Ahmad\\Dropbox\\Work\\WolverhamptonUni\\docs\\D3.3\\Analysis\\SentimentClassification")

sentiments_tfidf_df <- read.csv(file = paste0(dataDir,"TrafficPosTFIDFSentiment20160411.csv"), header = T, stringsAsFactors = F)

for (i in 1:nrow(sentiments_tfidf_df)) {
  if (sentiments_tfidf_df$sentiment[i] < 0) {
    sent_class <- "Negative"
  } else if (sentiments_tfidf_df$sentiment[i] == 0) {
    sent_class <- "Neutral"
  } else if (sentiments_tfidf_df$sentiment[i] > 0) {
    sent_class <- "Positive"
  }
  sentiments_tfidf_df$sent_class[i] <- sent_class
}

lm_eqn <- function(df){
  m <- lm(y ~ x, df);
  eq <- substitute(italic(y) == a + b %.% italic(x)*","~~italic(r)^2~"="~r2, 
                   list(a = format(coef(m)[1], digits = 2), 
                        b = format(coef(m)[2], digits = 2), 
                        r2 = format(summary(m)$r.squared, digits = 3)))
  as.character(as.expression(eq));                 
}

traffic_terms <- c("congestion", "delays", "accident", "roadworks", "road", "works", "repairs", "barrier", 
                   "bridge", "management", "safe", "traffic", "drive", "open", "cleared", "flowing", "easing", "ease", "reopened", 
                   "completed", "remains", "released", "spillage", "closed")

# i <- traffic_terms[]
i <- "reopened"

vars <- c(i, "sentiment", "sent_class")
sentiments_tfidf_df_sub <- sentiments_tfidf_df[, vars]
colnames(sentiments_tfidf_df_sub) <- c("x","y","Sentiment")
sentiments_tfidf_df_sub$Sentiment <- as.factor(sentiments_tfidf_df_sub$Sentiment)
sentiments_tfidf_df_sub <- sentiments_tfidf_df_sub[sentiments_tfidf_df_sub$x > 0, ]
p <- ggplot(sentiments_tfidf_df_sub, aes(x=x, y=y, group=Sentiment)) + 
  geom_point(aes(shape=Sentiment, color=Sentiment),size = 2) + 
  scale_shape_manual(values=c(3,16,17)) +
  scale_color_manual(values=c('red','green', 'grey')) +
  geom_smooth(method = "lm", se=F, color="black", formula = y ~ x) +
  xlab("TF-IDF Weight") +
  ylab("Sentiment Score") +
  ggtitle(paste0("Term: ",i)) +
  geom_text(x = 0.5, y = 0.0, 
            label = lm_eqn(sentiments_tfidf_df_sub), size=10, colour = "black", parse = TRUE) +
  theme(plot.title = element_text(color="black", face="bold", size=14),
        axis.text.x=element_text(size=14), 
        axis.text.y=element_text(size=14),
        axis.title.x=element_text(size=14,face="bold"),
        axis.title.y=element_text(size=14,face="bold"),
        legend.text=element_text(size=12),
        legend.position="top") 

print(p)


