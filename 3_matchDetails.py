# ------------------------------------------------------------------#
# AMPBA - 2021 Winter :: Data Collection assignment - PART2         #
# Group Id : 3                                                      #
# Authors:                                                          #
#       Nishant Jalasutram      -   PG ID: 012020051                #
#       Ila Barshilia           -   PG ID: 012020022                #
#       Deep Kamal Singh        -   PG ID: 012020053                #
# ------------------------------------------------------------------#

'''
Part 2:
For each match, go to the scorecard link like
https://www.espncricinfo.com/series/icc-cricket-world-cup-2019-1144415/india-vs-new-zealand-1st-semi-final-1144528/full-scorecard and extract the following:
1. Player of the match with the picture. Save the url to the picture in the csv.
2. Country that the player of the match belongs to.
3. Runs scored by every batsman.
4. Balls played by every batsman.
5. Strike rate for every batsman.
6. Wickets taken by every bowler.
7. Economy rate for every bowler.
8. which country won the toss.
9. who were the umpires?
10. who was the match referee

Save results in a file [your group no]_matchDetails.csv.
Name the .py file as [your group no]_matchDetails.py.

'''

import scrapy

# As per Assignments requirement we need to start our file name with GROUP number, thus we have to use import this
# way, instead of simply writing from <File_name> import <ClassName>
CricinfoPlayerProfileSpider = __import__(
    '3_playerDetails').CricinfoPlayerProfileSpider  # ,fromlist=['3_playerDetails'])


class CWC2019MatchStatsSpider(scrapy.Spider):
    name = "cwc_2019_Scorecard_spider"
    cricinfo_host = 'https://www.espncricinfo.com'
    playerProfileParser = CricinfoPlayerProfileSpider(scrapy.Spider)

    # This method will be called for every inning of the match , and it will extract Batsmen and Bowlers
    def parseInning(self, anInning):
        return {
            "batsmen": self.parseBatsmen(anInning.css("table[class='table batsman']")),
            "bowlers": self.parseBowler(anInning.css("table[class='table bowler']")),
        }

    # This method extracts match details - iterates over every TR and creates a KV Pair dictionary
    #    thus making it independent of sequence of occurrence
    def parseMatchDetails(self, matchDetailSection):
        trs = matchDetailSection.css("tbody").css("tr")
        returnDict = {}
        for aRow in trs:
            tds = aRow.css("td")

            if tds is not None and len(tds) > 1:
                returnDict[tds[0].css('::text').extract()[0]] = tds[1].css('::text').extract()[0] if len(
                    tds[1].css('::text').extract()) == 1 else ",".join(tds[1].css('::text').extract())

        return returnDict

    # This method extract Player of the match information
    # however, we found the player of the match image is lazy loaded and Scrapy is not good enough for this
    # we tried with Selenium as well as with Beautifulsoup which made the code messy and inconsistent,
    # so we are now getting player pic in PART3 execution,and setting it back inside PART2 data set
    def parsePlayerOfMatchSection(self, playerOfMatchSection):

        return {
            "player_of_the_match": playerOfMatchSection.css('div[class="best-player-name"]').css(
                'a::text').extract_first(),
            "player_of_the_match_profile": playerOfMatchSection.css('div[class="best-player-name"]').css(
                'a::attr(href)').extract_first(),
            "player_of_the_match_image_url": "",  # We are not loading image now, as it will be lazyimg.png anyway -
            # we will get the player image from PART3 output dictionary later
            "player_of_the_match_country": playerOfMatchSection.css(
                'span[class="best-player-team-name"]::text').extract_first()
        }

    # Extracts batsmen details, also takes care of batsmen who did not bat
    def parseBatsmen(self, battingTable):
        # batting table parsing
        batsmenList = []
        for aBattingRow in battingTable.css("tbody").css("tr"):
            tds = aBattingRow.css("td::text").extract()

            if aBattingRow.css('.batsman-cell').css("a::text").extract_first() is not None:
                # Found that when batsman is NOT out we get back "not out" in first element instead of RUNS,
                # handling this
                if tds[0].isnumeric():
                    batsmenList.append({
                        "name": aBattingRow.css('.batsman-cell').css("a::text").extract_first().strip(),
                        "profile_url": aBattingRow.css('.batsman-cell').css("a::attr('href')").extract_first(),
                        "runs": tds[0],
                        "balls_played": tds[1],
                        "strike_rate": tds[5]
                    })
                else:
                    batsmenList.append({
                        "name": aBattingRow.css('.batsman-cell').css("a::text").extract_first().strip(),
                        "profile_url": aBattingRow.css('.batsman-cell').css("a::attr('href')").extract_first(),
                        "runs": tds[1],
                        "balls_played": tds[2],
                        "strike_rate": tds[6]
                    })

        # Are there any "Yet to bat" players - lets add them too
        if len(batsmenList) < 11 and len(battingTable.css("tfoot").css("tr")) > 1:
            didNotBatLinks = battingTable.css("tfoot").css("tr")[1].css("td")[0].css("div")[0].css("a")
            for aPlayer in didNotBatLinks:
                batsmenList.append({
                    "name": aPlayer.css('span::text').extract_first().strip().replace("&nbsp;", ""),
                    "profile_url": aPlayer.css("::attr(href)").extract_first(),
                    "runs": "",
                    "balls_played": "",
                    "strike_rate": ""
                })
        return batsmenList

    # Extracts Bowler details
    def parseBowler(self, bowlingScores):
        # parsing bowling scores to extract each bowler
        bowlerList = []
        for aBowlingStatRow in bowlingScores.css("tbody").css("tr"):
            tds = aBowlingStatRow.css("td::text").extract()
            if aBowlingStatRow.css('.text-nowrap').css("a::text").extract_first() is not None:
                bowlerList.append({
                    "name": aBowlingStatRow.css('.text-nowrap').css("a::text").extract_first().strip(),
                    "profile_url": aBowlingStatRow.css('.text-nowrap').css("a::attr('href')").extract_first(),
                    "wickets": tds[3],
                    "econ": tds[4]
                })
        return bowlerList

    # This function is called when Part 1 yields a scrapy request
    # which is processed by Scrapy and response is handed over to this function
    # in addition it is passed with match_details_dict which is dictionary to store the match details
    # after crawling ends, the dictionary is used to output CSV file
    # This method checks whether Match is having an outcome or is it abandoned or draw
    def parse(self, resp, match_number, match_details_dict, match_players_dict):
        inning = {}
        batsmen = []
        bowlers = []
        # tsvDict = {}
        # checking if match is  abandoned
        if len(resp.css(".Collapsible").css(".Collapsible__contentInner").css(
                "table[class='w-100 table batsman']")) > 0:

            # Match seems abandoned, iterate over .batsman .small , to get player list
            for aBatsman in resp.css(".Collapsible").css(".Collapsible__contentInner"). \
                    css("table[class='w-100 table batsman']"). \
                    css("tbody").css("tr").css("td").css("a"):
                batsmen.append({
                    "name": aBatsman.css('::text').extract_first().strip().replace("&nbsp;", ""),
                    "profile_url": aBatsman.css('::attr(href)').extract_first(),
                    "runs": "",
                    "balls_played": "",
                    "strike_rate": ""
                })

            match_detail = self.parseMatchDetails(resp.css("table[class='w-100 table match-details-table']"))

            tsvDict = {
                "player_of_the_match": "",
                "player_of_the_match_image_url": "",
                "player_of_the_match_country": "",
                "batsmen_runs": "",
                "batsmen_ball_played": "",
                "batsmen_strike_rate": "",
                "bowlers_wickets": "",
                "bowlers_econ_rate": "",
                "toss_won_by": match_detail["Toss"].split(",")[0].strip(),
                "umpires": match_detail["Umpires"] + ",TV:" + match_detail["TV Umpire"] + ",Reserve:" + match_detail[
                    "Reserve Umpire"],
                "match_referee": match_detail["Match Referee"]
            }

        else:
            # valid non-abandoned match, follow normal processing

            best_player_details = self.parsePlayerOfMatchSection(resp.css("div[class='best-player']"))

            for anInning in resp.css(".Collapsible"):
                inningCountry = anInning.css("h5").css(".header-title.label::text").extract_first().split("INNINGS")[
                    0].strip()
                inning[inningCountry] = self.parseInning(anInning.css(".Collapsible__contentInner"))

                batsmen.extend(inning[inningCountry]["batsmen"])
                bowlers.extend(inning[inningCountry]["bowlers"])

            batsmen_run_csv = ",".join([batter["runs"] for batter in batsmen])
            batsmen_balls_csv = ",".join([batter["balls_played"] for batter in batsmen])
            batsmen_strike_rate_csv = ",".join([batter["strike_rate"] for batter in batsmen])

            bowlers_wickets_csv = ",".join([bowler["wickets"] for bowler in bowlers])
            bowlers_econ_rate_csv = ",".join([bowler["econ"] for bowler in bowlers])

            scrapedScorecard = {"innings": inning,
                                "match_detail": self.parseMatchDetails(
                                    resp.css("table[class='w-100 table match-details-table']"))}

            tsvDict = {
                "player_of_the_match": best_player_details["player_of_the_match"],
                "player_of_the_match_image_url": best_player_details["player_of_the_match_image_url"],
                "player_of_the_match_country": best_player_details["player_of_the_match_country"],
                "batsmen_runs": batsmen_run_csv,
                "batsmen_ball_played": batsmen_balls_csv,
                "batsmen_strike_rate": batsmen_strike_rate_csv,
                "bowlers_wickets": bowlers_wickets_csv,
                "bowlers_econ_rate": bowlers_econ_rate_csv,
                "toss_won_by": scrapedScorecard["match_detail"]["Toss"].split(",")[0].strip(),
                "umpires": scrapedScorecard["match_detail"]["Umpires"] + ",TV:" + scrapedScorecard["match_detail"][
                    "TV Umpire"] + ",Reserve:" + scrapedScorecard["match_detail"]["Reserve Umpire"],
                "match_referee": scrapedScorecard["match_detail"]["Match Referee"]
            }

        match_details_dict[match_number] = tsvDict

        players = batsmen
        players.extend(bowlers)
        # Invoke processing for part 3 for every player
        for aPlayer in players:
            # Duplication check :: SCRAPY checks that automatically,
            #           will fetch only if the new request is not already fetched
            yield scrapy.Request(resp.urljoin(aPlayer["profile_url"]), callback=self.playerProfileParser.parse,
                                 cb_kwargs={'match_players_dict': match_players_dict})
