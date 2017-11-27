# ------------------------------------------------------------------------------
# Script to build pitch trajectories (i.e. "snapshots")
# 
# Daniel Gale 2017 (c)
# ------------------------------------------------------------------------------

library(pitchRx)
library(DBI)
library(RSQLite)

# enter in pitch params as: c("x0", "y0", "z0", "vx0", "vy0", "vz0", "ax", "ay", "az")

# pull in pitch params from DB, along with identifier
# apply getSnapshots to each pitch
# store in separate table in DB

rm(list=ls())

query <- 'SELECT x0, y0, z0, vx0, vy0, vz0, ax, ay, az FROM pitch'

con <- dbConnect(SQLite(), '../data/pitches.sqlite3')
result <- dbSendQuery(con, query)
df <- dbFetch(result)

# snapshots <- apply(df, 1, function(x) getSnapshots(x))

snapshots <- list()
for (i in 1:nrow(df)){
  
  if (any(is.na(df[i,]))){
    snapshots[[i]] <- NA
    print(paste(i, "NA"))
  } else {
    snapshots[[i]] <- getSnapshots(df[i,])
    print(paste(i, "ok"))
  }
  
}
