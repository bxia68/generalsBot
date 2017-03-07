import requests
import time

REFRESH_TIME = 12 * 3600 # 12 hours

usersVisitedSet = {}
timeUsersVisited = []
replaysDownloaded = {}
replaysToDownload = {}
usersToVisit = []

def getReplayListForUser(userName):
    baseUrl = 'http://generals.io/api/replaysForUsername'
    data = {
        'u': userName,
        'offset': 0,
        'count': 20
    }
    print 'Getting replay list for', userName
    return requests.get(baseUrl, params=data).json()

def getReplayIdsAndUsersFromReplayList(replayList):
    games = {}
    for game in replayList:
        games[game['id']] = []
        for user in game['ranking']:
            if user['name'] != u'Anonymous':
                games[game['id']].append(user['name'])

    return games

def updateLists(visitedUser, gameList):
    global usersVisitedSet, timeUsersVisited, replaysDownloaded 
    global replaysToDownload, usersToVisit
    currTime = time.time()

    # Add the current user to the visited users list
    usersVisitedSet = usersVisitedSet | {visitedUser}
    timeUsersVisited.append((visitedUser, currTime))

    for replayId in gameList:
        if (replayId in replaysToDownload or 
                replayId in replaysDownloaded):
            continue

        # We haven't seen this replayId so let's add it to the list of 
        # replays to download
        replaysToDownload = replaysToDownload | {replayId}

        for user in gameList[replayId]:
            if user in usersVisitedSet:
                continue
            # we haven't seen this user, so let's add them to the list of users to visit
            usersToVisit.append(user)

def scrape():
    global usersVisitedSet, timeUsersVisited, replaysDownloaded 
    global replaysToDownload, usersToVisit
    userList = list(usersToVisit)
    for user in userList:
        time.sleep(1)
        replayList = getReplayListForUser(user)
        games = getReplayIdsAndUsersFromReplayList(replayList)
        updateLists(user, games)
            

