import requests
import json


def getReplayListForUser(userName):
    baseUrl = 'http://generals.io/api/replaysForUsername'
    data = {
        'u': userName,
        'offset': 0,
        'count': 200
    }
    return requests.get(baseUrl, params=data).json()


def downloadReplay(replayId):
    baseUrl = 'https://generalsio-replays-na.s3.amazonaws.com/{}.gior'
    data = requests.get(baseUrl.format(replayId)).content
    with open('replays/replay{}.gior'.format(replayId), 'wb') as fileOut:
        fileOut.write(data)


filename = "generals.io _ Season Rankings.json"
with open(filename, 'r') as f:
    data = json.load(f)
duelData = data["rankings"][0]
for i in range(0, 1):
    if duelData[i]["username"]:
        gameList = getReplayListForUser(duelData[i]["username"])
        for replay in gameList:
            if replay["type"] == "1v1":
                downloadReplay(replay["id"])
