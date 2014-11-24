setwd("/Users/andylee/_Social_Network_Analysis/ifttt")
d <- read.table("user_services_hist.txt",col.name=c("services","users"))
plot(log10(d$users), type="o", col="blue", axes=FALSE, ann=FALSE)

title(main="IFTTT channels used", col.main="black", font.main=1)

services <- range(1, d$services)
users <- range(0, d$users)

axis(1, at=c(1,2,3,4,5,10,20,30,40,50,60,70,80,90,services[2]),
     lab=c(1, 2, 3, 4, 5, 10,20,30,40,50,60,70,80,90,services[length(services)])  )
axis(2, at=1*0:5, lab=c(1,10,100,1000,10000,100000)) 

title(xlab="Channel Count", col.lab="black")
title(ylab="Users", col.lab="black")

text(d$services[1], log10(d$users[1]), labels=d$users[1], cex=0.7, col=rgb(0.6,0,0), pos="1")
text(d$services[2], log10(d$users[2]), labels=d$users[2], cex=0.7, col=rgb(0.6,0,0), pos="4")
text(d$services[3], log10(d$users[3]), labels=d$users[3], cex=0.7, col=rgb(0.6,0,0), pos="2", offset="0.25")
text(d$services[4], log10(d$users[4]), labels=d$users[4], cex=0.7, col=rgb(0.6,0,0), pos="4", offset="0.5")
text(d$services[5], log10(d$users[5]), labels=d$users[5], cex=0.7, col=rgb(0.6,0,0), pos="4")
text(d$services[10], log10(d$users[10]), labels=d$users[10], cex=0.7, col=rgb(0.6,0,0), pos="4")
text(d$services[15], log10(d$users[15]), labels=d$users[15], cex=0.7, col=rgb(0.6,0,0), pos="4", offset="1")
text(d$services[20], log10(d$users[20]), labels=d$users[20], cex=0.7, col=rgb(0.6,0,0), pos="4", offset="1.6")
text(d$services[25], log10(d$users[25]), labels=d$users[25], cex=0.7, col=rgb(0.6,0,0), pos="4", offset="1.6")
text(d$services[services[2]], log10(d$users[services[2]]), labels=d$users[services[2]], pos="3",
     cex=0.7, col=rgb(0.6,0,0))

box()
