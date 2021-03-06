# ------------------------------------------------------------------------------
# Script to setup the database 
# 
# Daniel Gale 2017 (c)
# ------------------------------------------------------------------------------

library(dplyr)
library(pitchRx)
library(baseballr)
library(DBI)
library(RSQLite)

source("db_functions.R")

# script params
database <- "../data/pitches.sqlite3"
start_date <- "2015-04-05"
end_date <- "2017-11-03"
scrape = TRUE
  
if (scrape){
  # toggle scraping data from pitchfx 
  getPitches(c(start_date, end_date), database)
}
addPlayers(database)
