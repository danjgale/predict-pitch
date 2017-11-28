# ------------------------------------------------------------------------------
# Script to build pitch trajectories (i.e. "snapshots")
# 
# Daniel Gale 2017 (c)
# ------------------------------------------------------------------------------

library(pitchRx)
library(DBI)
library(RSQLite)
library(jsonlite)

# enter in pitch params as: c("x0", "y0", "z0", "vx0", "vy0", "vz0", "ax", "ay", "az")

# pull in pitch params from DB, along with identifier
# apply getSnapshots to each pitch
# store in separate table in DB

rm(list=ls())

query <- 'SELECT gameday_link, event_num, play_guid, x0, y0, z0, vx0, vy0, vz0, ax, ay, az FROM pitch'

con <- dbConnect(SQLite(), '../data/pitches.sqlite3')
result <- dbSendQuery(con, query)
df <- dbFetch(result)
df <- df[complete.cases(df),]

test_df <- head(df)

make_snapshots <- function(x){
  toJSON(getSnapshots(x), matrix = 'rowmajor', pretty = TRUE)
}

snapshots <- vector("list", nrow(df))
for (i in c(1:nrow(df))){
  print(i)
  snapshots[[i]] <- make_snapshots(df[i, c(4:12)])
}

saveRDS(snapshots, '../data/shapshots.rds')

output_df <- cbind(df[,c(1:3)], 'trajectories'=unlist(snapshots, use.names=FALSE))
dbWriteTable(con, 'snapshots', output_df, overwrite=TRUE)
dbDisconnect(con)
