# ------------------------------------------------------------------#
# AMPBA - 2021 Winter :: Data Collection assignment - PART3         #
# Group Id : 3                                                      #
# Authors:                                                          #
#       Nishant Jalasutram      -   PG ID: 012020051                #
#       Ila Barshilia           -   PG ID: 012020022                #
#       Deep Kamal Singh        -   PG ID: 012020053                #
# ------------------------------------------------------------------#

'''
Part 3:
For each player across all matches (using the player page like https://www.espncricinfo.com/newzealand/content/player/506612.html) extract the following:
1. Full name of player.
2. Date and place of birth.
3. Current age.
4. Major teams.
5. Playing role.
5. Batting style.
6. Bowling style.
7. Highest ODI batting score.
8. ODI debut information.
9. Profile information.
10. Pic of the player. Save the url of the image in the csv.
11. Country of the player.

Save results in a file [your group no]_playerDetails.csv.
Name the .py file as [your group no]_playerDetails.py.

'''

import scrapy

class CricinfoPlayerProfileSpider(scrapy.Spider):

    # This function is called by `parse` method, it extracts Player's information from profile page with selector
    # `.ciPlayerinformationtxt` , it returns a Dictionary containing named values for profile attributes
    def parsePlayerProfile(self, playerSection):
        playerInfoText = playerSection.css(".ciPlayerinformationtxt")

        player_info_kv={}

        for aPlayerInfo in playerInfoText:
            player_info_kv[aPlayerInfo.css("b::text").extract_first().strip()] = \
                aPlayerInfo.css("span::text").extract_first().strip() if aPlayerInfo.css("b::text").extract_first().strip()!="Major teams" \
                    else ",".join(aPlayerInfo.css("span::text").extract()).strip()

        debutTable = playerSection.css('table[class="engineTable"]')[0]

        career_stats = {"highest_odi_batting_score": debutTable.css("tbody").css("tr")[1].css("td")[5].css(
            "::text").extract_first()}

        for tds in playerSection.css('table[class="engineTable"]')[2].css("tr"):
            odi_debut = tds.css("::text").extract()
            if odi_debut[1] == "ODI debut":
                career_stats["odi_debut_information"] = odi_debut[3].strip()
                break

        return {
            "player_name": player_info_kv["Full name"],
            "player_dob_place": player_info_kv["Born"],
            "current_age": player_info_kv["Current age"],
            "major_teams": player_info_kv["Major teams"],
            "playing_role": player_info_kv["Playing role"],
            "batting_style": player_info_kv["Batting style"],
            "bowling_style": player_info_kv["Bowling style"] if "Bowling style" in player_info_kv else "N/A",
            "highest_odi_batting_score": career_stats["highest_odi_batting_score"],
            "odi_debut_information": career_stats["odi_debut_information"],
            "profile_information": playerSection.css("#shrtPrfl").css("p::text").extract_first().strip().replace("\n",
                                   ",") if playerSection.css(
                "#shrtPrfl").css("p::text").extract_first() is not None else "",
            "player_pic": playerSection.css("img::attr(src)").extract_first(),
            "player_country": playerSection.css("h3[class='PlayersSearchLink']").css("b::text").extract_first()
        }

    # This is main function invoked after Scrapy request invoked from PART2 is processed, the response is passed,
    # along with match_players_dict which is dictionary store for all players, eventually after crawling finishes,
    # this dictionary will be used to obtain player of the match images, and then it will be written out in TSV file
    def parse(self, resp, match_players_dict):
        tsv_players = self.parsePlayerProfile(resp.css(".pnl490M"))
        match_players_dict[resp.css(".pnl490M").css(".ciPlayernametxt").css("h1::text").extract_first()] = tsv_players