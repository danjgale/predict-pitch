# ------------------------------------------------------------------------------
# Scrape Pitchf/x data into local sqlite database
# 
# Daniel Gale 2017 (c)
# ------------------------------------------------------------------------------

library(dplyr)
library(pitchRx)
library(baseballr)
library(DBI)
library(RSQLite)

populatePitchDB <- function(timerange){
  con <- dbConnect(SQLite(), dbname = "../data/pitches.sqlite3")
  scrape(start = timerange[1], end = timerange[2], connect = con)
  dbDisconnect(con)
}

start_date <- "2016-04-03"
end_date <- "2017-11-03"
populatePitchDB(c(opening_2016,end_date))
