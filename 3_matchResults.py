# ------------------------------------------------------------------#
# AMPBA - 2021 Winter :: Data Collection assignment - PART1         #
# Group Id : 3                                                      #
# Authors:                                                          #
#       Nishant Jalasutram      -   PG ID: 012020051                #
#       Ila Barshilia           -   PG ID: 012020022                #
#       Deep Kamal Singh        -   PG ID: 012020053                #
# ------------------------------------------------------------------#

"""
Part 1:
From this page: https://www.espncricinfo.com/series/icc-cricket-world-cup-2019-1144415/match-results, scrap the following information
1. Match number
2. Location
3. Date
4. Winning country
5. Other country
6. Match result
7. Score by winning country
8. Score by other country
9. Link to match report
10. Link to match summary
11. Link to match scorecard

Save results in a file [your group no]_matchResults.csv.
Name the .py file as [your group no]_matchResults.py.

"""
import csv
import re
from datetime import datetime

import scrapy
from scrapy.crawler import CrawlerProcess

# As per Assignments requirement we need to start our file name with GROUP number, thus we have to use import this
# way, instead of simply writing from <File_name> import <ClassName>
CWC2019MatchStatsSpider = __import__('3_matchDetails').CWC2019MatchStatsSpider

csv.QUOTE_ALL = True

if __name__ == '__main__':

    match_results_list = []
    match_details_dict = {}
    match_players_dict = {}

    # We are using csv lib to read from Dictionary and output data in TSV format - the delimiter is set to TAB ~ \t
    part1_header_fields = [
        "match_number",
        "location",
        "date",
        "winner_country",
        "other_country",
        "result",
        "winner_score",
        "other_score",
        "match_report_url",
        "match_summary_url",
        "match_scorecard_url",
    ]
    part1_csv_writer = csv.DictWriter(open('3_matchResults.tsv', 'w', newline=''), fieldnames=part1_header_fields,
                                      delimiter='\t')
    part1_csv_writer.writeheader()

    part2_header_fields = [
        "player_of_the_match",
        "player_of_the_match_image_url",
        "player_of_the_match_country",
        "batsmen_runs",
        "batsmen_ball_played",
        "batsmen_strike_rate",
        "bowlers_wickets",
        "bowlers_econ_rate",
        "toss_won_by",
        "umpires",
        "match_referee"
    ]
    part2_csv_writer = csv.DictWriter(open('3_matchDetails.tsv', 'w', newline=''), fieldnames=part2_header_fields,
                                      delimiter='\t')
    part2_csv_writer.writeheader()

    part3_header_fields = [
        "player_name",
        "player_dob_place",
        "current_age",
        "major_teams",
        "playing_role",
        "batting_style",
        "bowling_style",
        "highest_odi_batting_score",
        "odi_debut_information",
        "profile_information",
        "player_pic",
        "player_country"
    ]
    part3_csv_writer = csv.DictWriter(open('3_playerDetails.tsv', 'w', newline=''), fieldnames=part3_header_fields,
                                      delimiter='\t')
    part3_csv_writer.writeheader()


    class CWC2019Spider(scrapy.Spider):
        name = "cwc_2019_spider"
        cricinfo_host = 'https://www.espncricinfo.com'
        start_urls = ['https://www.espncricinfo.com/series/icc-cricket-world-cup-2019-1144415/match-results']
        matchDetailsParser = CWC2019MatchStatsSpider(scrapy.Spider)

        def start_requests(self):
            return [
                scrapy.Request('https://www.espncricinfo.com/series/icc-cricket-world-cup-2019-1144415/match-results')]

        # The `parseFixture` function calls this and passes `div[class="teams"]` selector - which is further
        # dissected to get the TEAMs playing the match, this method finds out winning and other team, also when there
        # is Draw or play is cancelled/abandoned - it marks no winner for the match, in this case Winner and Other
        # country score should be read as Team A and Team B scores
        def parseTeams(self, teams):
            # loop over items in Teams, extract score and yield teams with score
            teamA = teams.css('div[class="team"]')
            teamB = teams.css('div[class="team"]')

            if len(teams.css('div[class="team"]')) > 1:
                # both TeamA and TeamB are in this selector - match is either draw or abandoned/cancelled, NO Winner
                teamA = teams.css('div[class="team"]')[0]
                teamB = teams.css('div[class="team"]')[1]
            else:
                # teamA is winner,
                teamA = teams.css('div[class="team"]')[0]
                teamB = teams.css('div[class="team team-gray"]')[0]

            return {
                "teamA": {
                    "name": teamA.css('.name::text').extract()[0],
                    "score-info": teamA.css('span[class="score-info"]::text').extract()[0] if len(
                        teamA.css('span[class="score-info"]::text').extract()) == 1 else "",
                    "score": teamA.css('span[class="score"]::text').extract()[0] if len(
                        teamA.css('span[class="score"]::text').extract()) > 0 else "",
                },
                "teamB": {
                    "name": teamB.css('.name::text').extract()[0],
                    "score-info": teamB.css('span[class="score-info"]::text').extract()[0] if len(
                        teamB.css('span[class="score-info"]::text').extract()) == 1 else "",
                    "score": teamB.css('span[class="score"]::text').extract()[0] if len(
                        teamB.css('span[class="score"]::text').extract()) > 0 else "",
                },
                "winner": teamA.css('.name::text').extract()[0] if len(teams.css('div[class="team"]')) == 1 else ""
            }

        # This function is called through `parse` method. It extracts out Description of match (Selector `div[
        # class="description"]::text`), Teams of the match (Object with Selector `div[class="teams"]` is passed on to
        # `parseTeams` function) and Result of the match (selector `'div[class="status-text"]`)
        def parseFixture(self, aMatch):
            return {
                "description": aMatch.css('div[class="description"]::text').extract()[0],
                "teams": self.parseTeams(aMatch.css('div[class="teams"]')),
                "result": aMatch.css('div[class="status-text"]').css('span::text').extract()[0]
            }

        # CTA stands for Call to Action , which is the name used in `cricinfo.com` website for this block,
        # this is the method which extracts out Match Detail (Scorecard) URL
        def parseCTA(self, ctaContainer):
            retDict = {}
            for aURL in ctaContainer.css("a"):
                retDict[aURL.css('a::text').extract()[0]] = aURL.css("a::attr(href)").extract()[0]
            return retDict

        def parse(self, resp):

            for aMatch in resp.css('.match-score-block'):
                # every loop gives one match result, we use BS4 to parse and record entries in our Dict
                statusText = aMatch.css('span[class="summary"]::text').extract_first()
                match_number = list(map(int, re.findall(r'\d+', statusText)))

                # above regex extraction will extract Number from statement and return the Match number
                # however Final match dont have any number, so we are handling it here

                if len(match_number) == 0 or statusText.find("Semi") >= 0:
                    match_number = [
                        str(aMatch.css('span[class="summary"]::text').extract_first()).replace(
                            "ICC Cricket World Cup ",
                            "").replace("match",
                                        "").strip()]

                match_details = self.parseFixture(aMatch.css('div[class="match-info match-info-FIXTURES"]'))
                match_urls = self.parseCTA(aMatch.css('div[class="match-cta-container"]'))

                start_time = aMatch.css('.dtstart::text').extract_first()
                matchLocation = aMatch.css('.location::text').extract_first().split(',')
                match_result_data = {
                    "match_number": match_number[0],
                    "location": matchLocation[0].strip() + "," + matchLocation[1].strip(),
                    "date": datetime.fromisoformat(start_time).date() if start_time != "" else "Not Started",
                    "winner_country": match_details["teams"]["winner"],
                    "other_country": match_details["teams"]["teamB"]["name"] if
                    match_details["teams"]["winner"] != "" else (
                            match_details["teams"]["teamA"]["name"] + "," + match_details["teams"]["teamB"][
                        "name"]),
                    "result": match_details["result"],
                    "winner_score": match_details["teams"]["teamA"]["score"],
                    "other_score": match_details["teams"]["teamB"]["score"],
                    "match_report_url": self.cricinfo_host + match_urls["Report"],
                    "match_summary_url": self.cricinfo_host + match_urls["Summary"],
                    "match_scorecard_url": self.cricinfo_host + match_urls["Scorecard"]
                }
                match_results_list.append(match_result_data)
                # this is Part 2 of assignment - we have identified the link for Scorecard and now we are invoking
                # request and parsing for Scorecard Page, we are passing match_details_dict and match_players_dict
                # with every yield, this way we get the data filled in the Dictionary, which we are using below to
                # output data in TSV file
                yield scrapy.Request(resp.urljoin(match_urls["Scorecard"]), callback=self.matchDetailsParser.parse,
                                     cb_kwargs={'match_number': match_number[0],
                                                'match_details_dict': match_details_dict,
                                                'match_players_dict': match_players_dict})


    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })
    # Crawling process is assigned the Spider
    process.crawl(CWC2019Spider)

    # Crawling begins
    process.start()

    # Now we have completed the crawling process, and we have Data ready to be written in TSV files
    # Except we dont yet have PLAYER_OF_THE_MATCH's profile pic
    #           - we will get that from PART3 output dataset and store it in PART2

    # This iteration writes into PART1 outfile 3_3_MatchResults.tsv and adds POTM profile pic,
    #               then it writes in to 3_matchDetails.tsv
    for aMatch in match_results_list:
        part1_csv_writer.writerow(aMatch)
        match_details_dict[aMatch["match_number"]]["player_of_the_match_image_url"] = \
            match_players_dict[match_details_dict[aMatch["match_number"]]["player_of_the_match"]]["player_pic"] if \
                match_details_dict[aMatch["match_number"]]["player_of_the_match"] != "" else ""
        part2_csv_writer.writerow(match_details_dict[aMatch["match_number"]])

    # This iteration writes into PART3 outfile 3_playerDetails.tsv
    for aPlayer in match_players_dict:
        part3_csv_writer.writerow(match_players_dict[aPlayer])
