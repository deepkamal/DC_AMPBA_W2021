# AMPBA - 2021 Winter :: Data Collection assignment

## Authors

 **Deep Kamal Singh     - 012020053**

 **Ila Barshilia        - 012020022** 

 **Nishant Jalasutram   - 012020051** 

## Pre-requisites

* Choose any empty user directory 

* Download the code and place 3 python code files _viz._ `3_matchResults.py` , `3_matchDetails.py` and `3_playerDetails.py` in above mentioned directory 

* python version higher than 3.5 should be installed on local system - verify by running command `python -V` in system command prompt/shell

* The code used for the assignment depends upon `scrapy`, `csv`, `re` and `datetime` python libraries 
  
* The scrapy (https://scrapy.org/), csv, re, datetime libraries must be installed on system, verify by running command 
      
      python -c "import scrapy;import datetime;import re;import csv"
  in system command prompt/shell, this command should not return any output or error
        
    - if scrapy or any other library is not installed, you can run `pip install "library_name"` e.g. `pip install scrapy` and verify again.
    
* The system must be connected to internet and must have access to `https://www.espncricinfo.com/**`

* The system must have more than 10 MB disk space available.

* The system user must have execute permission on `python` and must have the file write permission on the directory where code files are placed

## How to Run

Open system command prompt/shell. Switch working directory to the location where you saved python code files and simply run the command
         
      python 3_matchResults.py 

It will start executing and will show `scrapy` generated logs after the crawling begins. Once the crawling is finished, summary like this can be seen.
```json5
{'downloader/request_bytes': 200319,
 'downloader/request_count': 357,
 'downloader/request_method_count/GET': 357,
 'downloader/response_bytes': 6645881,
 'downloader/response_count': 357,
 'downloader/response_status_count/200': 203,
 'downloader/response_status_count/301': 154,
 'dupefilter/filtered': 1440,
 'elapsed_time_seconds': 18.322206,
 'finish_reason': 'finished',
 'finish_time': datetime.datetime(2021, 2, 22, 12, 22, 29, 706762),
 'log_count/DEBUG': 358,
 'log_count/INFO': 10,
 'memusage/max': 45449216,
 'memusage/startup': 45445120,
 'request_depth_max': 2,
 'response_received_count': 203,
 'scheduler/dequeued': 357,
 'scheduler/dequeued/memory': 357,
 'scheduler/enqueued': 357,
 'scheduler/enqueued/memory': 357,
 'start_time': datetime.datetime(2021, 2, 22, 12, 22, 11, 384556)}
2021-02-22 17:52:29 [scrapy.core.engine] INFO: Spider closed (finished)

```
Do note that all crawling is linked through Scrapy parse and yield process, thus above single command triggers PART1 of assignment process ,and invokes PART2, which inturn yields and invokes PART3 in a chain.
All duplicated requests are handled by Scrapy

## Output files

Once the process is complete, you will find 3 output files generated in same directory _viz._ `3_matchResults.tsv`, `3_matchDetails.tsv`  and `3_playerDetails.tsv`
These files are TAB separated files. 

 **3_MatchResults.tsv :: Match Result**

* This is output of PART1 of assignment - it's a tab separated file, with single match result info per row

* File contains Header 
        
        match_number    location	date	winner_country	other_country	result	winner_score	other_score	match_report_url	match_summary_url	match_scorecard_url

* Matches are listed in reverse chronological order

* Match number is taken out from match description string. Match number is either a number or label if it is semi-final or final.

* There are also 4 matches where there is no winner, in that case winner_country column is left blank, and other country contains comma separated list of team A and team B both.

 **3_matchDetails.tsv :: Match Details**

* This is output of PART2 of assignment - it's a tab separated file, with single match detail per row

* File contains Header 
        
        player_of_the_match	player_of_the_match_image_url	player_of_the_match_country	batsmen_runs	batsmen_ball_played batsmen_strike_rate	bowlers_wickets	bowlers_econ_rate	toss_won_by	umpires	match_referee


* Match details are listed in same order as generated in `3_matchResults.tsv`

* There are 3 matches which were abandoned and 1 match with no result. Corresponding to these matches, most of the data is blank. 

* For runs scored, balls played, strike rate, wickets taken and economy rate the values in a cell are comma separated with no value if the player didn't get a chance to bat or bowl.
   
 **3_playerDetails :: Player Details**

* This is output of PART3 of assignment - it's a tab separated file, with single player details per row

* File contains Header.   
        
        player_of_the_match	player_of_the_match_image_url	player_of_the_match_country	batsmen_runs	batsmen_ball_played batsmen_strike_rate	bowlers_wickets	bowlers_econ_rate	toss_won_by	umpires	match_referee
---------------------
* 5 players do not have place of birth mentioned in the link, hence for them only date of birth is listed.

## About the code

The code consists of three files  _viz._ `3_matchResults.py` , `3_matchDetails.py` and `3_playerDetails.py` , 

While `3_matchResults.py` contains the main code to start the execution and crawling - the other two files just contain Spider classes for Match details and Player details crawling,

This is how we are starting the crawl process - this is independent of Scrapy shell, also it does not need any `settings.py` or `pipeline.py` 
```python
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(CWC2019Spider)
    process.start()
```

we are storing output of every Match result processing in `match_results_list` list of dictionary, 
every match detail result is stored in `match_details_dict` dictionary , 
and every player profile details are stored in `match_players_dict` , when the crawling finishes these are used to output into TSV files using python `csv` lib

```python
    for aMatch in match_results_list:
        part1_csv_writer.writerow(aMatch)
        match_details_dict[aMatch["match_number"]]["player_of_the_match_image_url"] = \
            match_players_dict[match_details_dict[aMatch["match_number"]]["player_of_the_match"]]["player_pic"] if \
                match_details_dict[aMatch["match_number"]]["player_of_the_match"] != "" else ""
        part2_csv_writer.writerow(match_details_dict[aMatch["match_number"]])

    # This iteration writes into PART3 outfile 3_playerDetails.tsv
    for aPlayer in match_players_dict:
        part3_csv_writer.writerow(match_players_dict[aPlayer])
```

------------------------

 **Class `CWC2019Spider` in `3_matchResults.py`**

This class takes care of PART1 of assignment, there are three methods defined in class to handle specific parsing operation for working on an individual section of entire response

* `parseTeams` : The `parseFixture` function calls this and passes `div[class="teams"]` selector - which is further dissected to get the TEAMs playing the match, this method finds out winning and other team, also when there is Draw or play is cancelled/abandoned, winner country will be blank and other country will contain both the countries separated by comma  - in this case Winner and Other country score should be read as Team A and Team B scores

* `parseFixture` : This function is called through `parse` method. It extracts out Description of match (Selector `div[class="description"]::text`), Teams of the match (Object with Selector `div[class="teams"]` is passed on to `parseTeams` function) and Result of the match (selector `'div[class="status-text"]`)

* `parseCTA` : CTA stands for Call to Action , which is the name used in `cricinfo.com` website for this block, this is the method which extracts out Match Detail (Scorecard) URL


**`CWC2019Spider.parse` method** :

The Parse function is main method which is called by `SCRAPY` once the request is executed and response is received, we are identifying repeating blocks of all matches through the selector `.match-score-block`; 
which gives us 48 items, each item contains a Match's Team details, description, result-details and a Call-To-Action block which also has URL to Match Details. 
This function then iterates over each item and for each item it calls respective methods as listed above to extract necessary details required.
Once details are available it stores them in a `list[{}]` variable which will be later used to write TSV file, 
for every iteration this method `yields` another `Scrapy.Request` to Match Score card page - the yielded request is assigned a parser from class `CWC2019MatchStatsSpider`, more about this is explained below

 **Class `CWC2019MatchStatsSpider` in `3_matchDetails.py`**

This class takes care of PART2 of assignment, i.e. fetching match details from scorecard URL,and then extracting required fields further, there are five 
methods defined in class to handle specific parsing operation for working on an individual section of entire response, explained below:

  * `parseInning` : This method extracts match details - iterates over every `TR` and creates a `KV Pair` dictionary thus making it independent of sequence of occurrence

  * `parseMatchDetails`:  This method extracts Player of the match information however, we found the player of the match image is lazy loaded and `Scrapy` is not good enough for this. We tried with `Selenium` as well as with `BeautifulSoup` which made the code messy and inconsistent, so we are now getting player profile in PART3 execution,and setting it back inside PART2 data set

  * `parsePlayerOfMatchSection`: This method extract Player of the match information. We found the player of the match image is lazy loaded and `Scrapy` is not good enough for this, we tried with `Selenium` as well as with `Beautifulsoup` which made the code messy and inconsistent, 
    so we are now getting player pic in PART3 execution,and setting it back inside PART2 data set

  * `parseBatsmen`: Extracts batsmen details, also takes care of batsmen who did not bat

  * `parseBowler`: Extracts Bowler details

  **`CWC2019MatchStatsSpider.parse` method** is called when Part 1 yields a scrapy request
 which is processed by `Scrapy` and response is handed over to this function, in addition it is passed with `match_details_dict` which is the dictionary to store the match details
 after crawling ends, the dictionary is used to output CSV file. This method also checks whether Match is having an outcome or is it abandoned or draw

 **Class `CricinfoPlayerProfileSpider` in `3_playerDetails.py`**

This class takes care of PART3 of assignment, i.e. it fetches player details from profile URL formed in `scrapy.Request` and yieled in PART2,
to extract necessary details from page, there is one method named `parsePlayerProfile` defined in class,other than `parse`:

* `parsePlayerProfile` : This function is called by `parse` method, it extracts Player's information from profile page with selector `.ciPlayerinformationtxt` , it returns a Dictionary containing named values for profile attributes 

 **`CricinfoPlayerProfileSpider.parse` Method** is main function invoked after `Scrapy` request invoked from PART2 is processed, the response is passed, 
 along with `match_players_dict` which is dictionary store for all players, eventually after crawling finishes, 
 this dictionary will be used to obtain player of the match images, and then it will be written out in TSV file

## References and readings

* Data Science from Scratch by Joel Grus ( Publisher(s): O'Reilly Media, Inc. ISBN: 9781491901427)

* Scrapy documentation - https://docs.scrapy.org/en/latest/intro/tutorial.html

* Term1 DC course sessions (https://elearn.isb.edu)
