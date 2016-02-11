__author__ = 'Lindsay'
from trueskill import Rating, quality_1vs1, rate_1vs1, TrueSkill
import json
import sys
import requests
import os
import math
import time
import random


class Champion:

    def __init__(self, name, champ_id):
        self.name = name
        self.champ_id = champ_id
        self.total_matches = 0
        self.matches_won = 0
        self.matches_banned = 0


class Match:

    def __init__(self, match_id, losing_champs, winning_champs, timestamp):
        self.match_id = match_id
        self.losing_champs = losing_champs
        self.winning_champs = winning_champs
        self.timestamp = timestamp

    def __eq__(self, other):
        return self.match_id == other.match_id

    def __ne__(self, other):
        return self.match_id != other.match_id

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in

rel_matches_path = "matches.txt"
abs_matches_path = os.path.join(script_dir, rel_matches_path)

total_matches_recorded = 0

champion_database = {}
champion_list = {}
match_list = []
patch_list = {}

tResp = requests.get('https://global.api.pvp.net/api/lol/static-data/na/v1.2/champion?api_key=ad1973cd-b6bd-4def-b1b7-7982ab0957f7')
if tResp.status_code != 200:
    # This means something went wrong.
    print('stop that right now')
    print (tResp.status_code)
#print (resp.json())
data = json.dumps(tResp.json(), indent=2)
load = json.loads(data)

for key in load["data"]:
    champ_info = load["data"][key]
    champion_list[champ_info["id"]] = Champion(champ_info["name"], champ_info["id"])

for champ in champion_list:
    print(champ)
    print(champion_list[champ].total_matches)
    print(champion_list[champ].champ_id, "\n")



tResp = requests.get('https://na.api.pvp.net/api/lol/na/v2.2/matchlist/by-summoner/39628879?rankedQueues=RANKED_SOLO_5x5&seasons=SEASON3,PRESEASON2014,SEASON2014,PRESEASON2015,SEASON2015,PRESEASON2016,SEASON2016&api_key=ad1973cd-b6bd-4def-b1b7-7982ab0957f7')
if tResp.status_code != 200:
    # This means something went wrong.
    print('stop that right now')
    print (tResp.status_code)
#print (resp.json())
data = json.dumps(tResp.json(), indent=2)
load = json.loads(data)

'''
p = open(abs_matches_path, 'w')
p.write("timestamp")
p.write(",")
p.write("champion")
p.write(",")
p.write("matchId")
p.write('\n')
'''

player_list = []

for match in load["matches"]:
    match_list.append(Match(match["matchId"], [], [], match["timestamp"]))

counter = 0

for m in match_list:
    time.sleep(1)
    tResp = requests.get('https://na.api.pvp.net/api/lol/na/v2.2/match/'+str(m.match_id)+'?api_key=ad1973cd-b6bd-4def-b1b7-7982ab0957f7')
    if tResp.status_code != 200:
        # This means something went wrong.
        print('stop that right now')
        print(tResp.status_code)
    data = json.dumps(tResp.json(), indent=2)
    load = json.loads(data)
    for p in load["participantIdentities"]:
        if p["player"]["summonerId"] not in player_list:
            counter += 1
            print("Adding player Id "+str(p["player"]["summonerId"]))
            player_list.append(p["player"]["summonerId"])

print(str(counter)+" unique players found")
print(player_list)
print(str(len(player_list))+" players found")
print("Finding matches")
match_list = []
counter = 0
player_counter = 0

for p in player_list:
    player_counter += 1
    print("adding matches for player "+str(player_counter)+" id "+str(p))
    if player_counter>100:
        break
    time.sleep(1)
    tResp = requests.get('https://na.api.pvp.net/api/lol/na/v2.2/matchlist/by-summoner/'+str(p)+'?rankedQueues=RANKED_SOLO_5x5&seasons=SEASON3,PRESEASON2014,SEASON2014,PRESEASON2015,SEASON2015,PRESEASON2016,SEASON2016&api_key=ad1973cd-b6bd-4def-b1b7-7982ab0957f7')
    if tResp.status_code != 200:
        # This means something went wrong.
        print('stop that right now')
        print (tResp.status_code)
    #print (resp.json())
    data = json.dumps(tResp.json(), indent=2)
    load = json.loads(data)
    for match in load["matches"]:
        if random.randint(1,10) == 6:
            new_match = Match(match["matchId"], [], [], match["timestamp"])
            if new_match not in match_list:
                print("adding match id "+str(new_match.match_id))
                counter += 1
                match_list.append(new_match)

print(str(counter)+" unique matches found")
counter = 0
for m in match_list:
    counter += 1
    if counter > 2000:
        break
    time.sleep(1)
    print("Recording data from match "+str(m.match_id))
    total_matches_recorded +=1
    tResp = requests.get('https://na.api.pvp.net/api/lol/na/v2.2/match/'+str(m.match_id)+'?api_key=ad1973cd-b6bd-4def-b1b7-7982ab0957f7')
    if tResp.status_code != 200:
        # This means something went wrong.
        print('stop that right now')
        print (tResp.status_code)
        time.sleep(5)
        tResp = requests.get('https://na.api.pvp.net/api/lol/na/v2.2/match/'+str(m.match_id)+'?api_key=ad1973cd-b6bd-4def-b1b7-7982ab0957f7')

    #print (resp.json())
    data = json.dumps(tResp.json(), indent=2)
    load = json.loads(data)

    patch = load["matchVersion"]

    print("Before "+patch)
    first = patch.find(".")
    end = patch.find(".", first+1)
    patch = patch[:end]
    print("After "+patch)

    if patch not in patch_list:
        patch_list[patch] = 0
    patch_list[patch] += 1

    player_list = []

    for player in load["participants"]:
        champId = player["championId"]
        teamId = player["teamId"]
        player_list.append((champId, teamId))

    for p in player_list:
        if (champion_list[p[0]].name,p[0], patch) not in champion_database:
            champion_database[(champion_list[p[0]].name, p[0], patch)] = Champion(champion_list[p[0]].name, p[0])
        champion_database[(champion_list[p[0]].name, p[0], patch)].total_matches += 1

    for team in load["teams"]:
        for ban in team["bans"]:
            if (champion_list[ban["championId"]].name,ban["championId"], patch) not in champion_database:
                print("Adding "+champion_list[ban["championId"]].name+" to the database on patch "+patch)
                champion_database[(champion_list[ban["championId"]].name, ban["championId"], patch)] = Champion(champion_list[p[0]].name, p[0])
            champion_database[(champion_list[ban["championId"]].name, ban["championId"], patch)].matches_banned += 1
        if team["winner"]:
            for p in player_list:
                if p[1] == team["teamId"]:
                    champion_database[(champion_list[p[0]].name, p[0], patch)].matches_won += 1

print(str(champion_database.keys()))

for champ in sorted(champion_database.keys()):
    print(champ[0])
    print("Patch: "+champ[2])
    print("Total: "+str(champion_database[champ].total_matches))
    print("Won: "+str(champion_database[champ].matches_won))
    print("Banned: "+str(champion_database[champ].matches_banned))
    if champion_database[champ].total_matches == 0:
        print("Winrate: {:.1%}".format(champion_database[champ].total_matches))
    else:
        print("Winrate: {:.1%}".format(champion_database[champ].matches_won / champion_database[champ].total_matches))
    if champion_database[champ].total_matches == 0:
        print("Pickrate: {:.1%}".format(champion_database[champ].total_matches))
    else:
        print("Pickrate: {:.1%}".format(champion_database[champ].total_matches / patch_list[champ[2]]))
    if champion_database[champ].matches_banned == 0:
        print("Banrate: {:.1%}".format(champion_database[champ].matches_banned))
    else:
        print("Banrate: {:.1%}".format(champion_database[champ].matches_banned / patch_list[champ[2]]))
    print("\n")
print(patch_list)
'''
p.close()


pURLs = []
for i in tId:
    pURLs.append("https://wpismash:3mfdkkeh4CfXzug8VBDXPyI7Hi1CntMzfyIeYhSZ@api.challonge.com/v1/tournaments/"+str(i)+"/participants.json")

def standardizeName(str):
    str = str.lower().replace(" ","")
    tagEnd = str.find('(', 0, len(str))
    #print(tagEnd)
    if tagEnd != -1:
        str = str[:tagEnd]
    #print("New name is {}".format(str))
    return str

playerNames = []
pURL = "https://wpismash:3mfdkkeh4CfXzug8VBDXPyI7Hi1CntMzfyIeYhSZ@api.challonge.com/v1/tournaments/"+str(tId[1])+"/participants.json"
for count, pURL in enumerate(pURLs):
    pResp = requests.get(pURL)
    pdata = json.dumps(pResp.json(), indent=2)
    pload = json.loads(pdata)
    for participant in pload:
        #print(participant)
        #print(participant["participant"]["name"])
        x = Player(participant['participant']['name'])
        if "Bye" not in participant['participant']['name']:
            tempName = standardizeName(participant['participant']['name'])
            if tempName not in playerNames:
                playerNames.append(tempName)
                for t, i in enumerate(tList):
                    x.playerIDs[t] = 0
                x.playerIDs[count] = participant['participant']['id']
                playerList.append(x)
            else:
                #print(participant['participant']['name'])
                for player in playerList:
                    if standardizeName(player.name) == tempName:
                        player.playerIDs[count] = participant['participant']['id']
                        player.place[count] = participant['participant']['final_rank']
'''
'''
for name in playerNames:
    print (name)

for player in playerList:
    for x in range(0,len(player.playerIDs)):
        print(player.playerIDs[x])
'''
'''

for x in range(0, len(tId)):
    print("Tournament # " + str(x))
    mURL = "https://wpismash:3mfdkkeh4CfXzug8VBDXPyI7Hi1CntMzfyIeYhSZ@api.challonge.com/v1/tournaments/"+str(tId[x])+"/matches.json"
    mResp = requests.get(mURL)
    mdata = json.dumps(mResp.json(), indent=2)
    mload = json.loads(mdata)
    for match in mload:
        #print(match['match'])
        #print(match['match']['winner_id'])
        #print(match['match']['loser_id'])
        for count, player in enumerate(playerList, start=0):
            if player.playerIDs[x] == match['match']['winner_id']:
                winnerindex = count
            if player.playerIDs[x] == match['match']['loser_id']:
                loserindex = count
        #if playerList[loserindex].name == "Stormcloud (Lindsay)":
            #print("old : " +str(playerList[loserindex].rank.sigma))

        score1 = match['match']['scores_csv'].split('-')[0]
        score2 = match['match']['scores_csv'].split('-')[1]
        score = match['match']['scores_csv']
        if score1 < score2:
            score = score2+"-"+score1
        #print(score1)
        #print(score2)
        loserScore = min(int(score1), int(score2))
        winnerScore = max(int(score1), int(score2))
        newr1 = playerList[loserindex].rank
        newr2 = playerList[winnerindex].rank
        for j in range(0, loserScore):
            playerList[loserindex].rank, playerList[winnerindex].rank = rate_1vs1(newr1, newr2)
            newr1 = playerList[loserindex].rank
            newr2 = playerList[winnerindex].rank
        for k in range(0, winnerScore):
            playerList[winnerindex].rank, playerList[loserindex].rank = rate_1vs1(newr2, newr1)
            newr1 = playerList[loserindex].rank
            newr2 = playerList[winnerindex].rank
        playerList[loserindex].lost+=1
        playerList[winnerindex].won+=1

        playerList[loserindex].matches.append(Match(playerList[winnerindex].name,
                                                    score,
                                                    "Lost",
                                                    x))
        playerList[winnerindex].matches.append(Match(playerList[loserindex].name,
                                                    score,
                                                    "Won",
                                                     x))
        print("score was "+match['match']['scores_csv'])

        #newr2, newr1 = rate_1vs1(playerList[winnerindex].rank, playerList[loserindex].rank)
        #playerList[winnerindex].rank = newr2
        #playerList[loserindex].rank = newr1
        #if playerList[loserindex].name == "Stormcloud (Lindsay)":
            #print("new : " +str(playerList[loserindex].rank.sigma))
'''
'''
for player in playerList:
    if player.name == "Stormcloud (Lindsay)":
        for x in range(0, len(player.playerIDs)):
            print(str(player.playerIDs[x]))
'''
'''

sortList = []

#Eligibility
for player in playerList:
    t = 0
    recent = 0
    for tournamentID in player.playerIDs:
        if player.playerIDs[tournamentID] != 0:
            t+=1
    x=0
    for tournamentID in player.playerIDs:
        if player.playerIDs[tournamentID] != 0 and x>12:
            recent+=1
        x+=1
    print(player.name +" attended "+str(t)+" tournaments")
    if (recent != 0) and (t >= 3):
        sortList.append(player)


for passnum in range(len(sortList)-1,0,-1):
        for i in range(passnum):
            if (sortList[i].rank.mu - sortList[i].rank.sigma*3)<(sortList[i+1].rank.mu - sortList[i+1].rank.sigma*3):
                temp = sortList[i]
                sortList[i] = sortList[i+1]
                sortList[i+1] = temp

for player in playerList:
    for m in player.matches:
        stats = player.record.get(m.opponent)
        if stats is None:
            if m.result == "Won":
                player.record[m.opponent] = Stats(1, 0)
            else:
                player.record[m.opponent] = Stats(0, 1)
        else:
            if m.result == "Won":
                player.record[m.opponent].wins += 1
            else:
                player.record[m.opponent].losses += 1


f = open(abs_file_path, 'w')

f.write("Name")
f.write(",")
f.write("Mu")
f.write(",")
f.write("Sigma")
f.write(",")
f.write("TrueSkill")
f.write(",")
f.write("Total Wins")
f.write(",")
f.write("Total Losses")
f.write('\n')

for player in sortList:
    f.write(player.name)
    f.write(",")
    f.write(str(player.rank.mu))
    f.write(",")
    f.write(str(player.rank.sigma))
    f.write(",")
    f.write(str(player.rank.mu - player.rank.sigma*3))
    f.write(",")
    f.write(str(player.won))
    f.write(",")
    f.write(str(player.lost))
    f.write('\n')
    #print(player.name+"             "+str(player.rank.mu))
f.close()
print(abs_file_path)

s = open(abs_stats_path, 'w')
s.write("Name")
s.write(",")
s.write("Opponent")
s.write(",")
s.write("Score")
s.write(",")
s.write("Result")
s.write(",")
s.write("Tournament ID#")
s.write('\n')

for player in sortList:
    for m in player.matches:
        s.write(player.name)
        s.write(",")
        s.write(m.opponent)
        s.write(",")
        s.write(m.score)
        s.write(",")
        s.write(m.result)
        s.write(",")
        s.write(str(m.tIndex))
        s.write('\n')

s.write('\n')
s.write("Name")
s.write(",")
s.write("Opponent")
s.write(",")
s.write("Wins")
s.write(",")
s.write("Losses")
s.write(",")
s.write("Winrate")
s.write(",")
s.write("Total Winrate")
s.write('\n')

for player in sortList:
    doneWinrate = False
    for oppo in player.record:
        s.write(player.name)
        s.write(",")
        s.write(oppo)
        s.write(",")
        s.write(str(player.record[oppo].wins))
        s.write(",")
        s.write(str(player.record[oppo].losses))
        s.write(",")
        s.write(str(player.record[oppo].wins/(player.record[oppo].wins + player.record[oppo].losses)))
        if not doneWinrate:
            s.write(",")
            s.write(str(player.won/(player.won+player.lost)))
            doneWinrate = True
        s.write('\n')

s.close()
p = open(abs_place_path, 'w')
for player in sortList:
    for r in player.place:
        p.write(player.name)
        p.write(",")
        p.write(str(r))
        p.write(",")
        p.write(str(player.place[r]))
        p.write('\n')

p.close()



print(abs_stats_path)
'''
print(sys.version)


