# ------------------------------------------------------------------------------
# Script to build pitch trajectories (i.e. "snapshots")
# 
# Daniel Gale 2017 (c)
# ------------------------------------------------------------------------------

rm(list=ls())

# library(Lahman)
library(baseballr)
library(DBI)
library(RSQLite)

pitcher_stats <-  daily_pitcher_bref('2017-04-02', '2017-10-02')

con <- dbConnect(SQLite(), '../../data/pitches.sqlite3')
dbWriteTable(con, 'pitchers', pitcher_stats, overwrite=TRUE)
dbDisconnect(con)

