# ------------------------------------------------------------------------------
# Functions to populate and setup the database
# 
# Daniel Gale 2017 (c)
# ------------------------------------------------------------------------------

library(dplyr)
library(pitchRx)
library(baseballr)
library(DBI)
library(RSQLite)

getPitches <- function(timerange, db){
  con <- dbConnect(SQLite(), dbname = db)
  scrape(start = timerange[1], end = timerange[2], connect = con)
  dbDisconnect(con)
}

addPlayers <- function(db){
  con <- dbConnect(SQLite(), dbname = db)
  dbWriteTable(con, value = players, name = "players", append = TRUE)
  dbDisconnect(con)
}

addGameDays <- function(db){
  con <- dbConnect(SQLite(), dbname = db)
  dbWriteTable(con, value = gids, name = "gamedays", append = TRUE)
  dbDisconnect(con)
}

