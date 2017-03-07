import requests
import time
from collections import deque
import pickle

# Time to revisit a user
REFRESH_TIME = 12 * 3600 # 12 hours
SLEEP_TIME = .5

usersVisitedSet = set()
timeUsersVisited = deque()
replaysDownloaded = set()
replaysToDownload = set()
usersToVisit = deque()

def getReplayListForUser(userName):
    baseUrl = 'http://generals.io/api/replaysForUsername'
    data = {
        'u': userName,
        'offset': 0,
        'count': 20
    }
    return requests.get(baseUrl, params=data).json()

def getReplayIdsAndUsersFromReplayList(replayList):
    games = {}
    for game in replayList:
        games[game['id']] = []
        for user in game['ranking']:
            if 'name' in user and user['name'] != u'Anonymous':
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
            if (user in usersVisitedSet or
                    user in usersToVisit):
                continue
            # we haven't seen this user, so let's add them to the list of users to visit
            usersToVisit.append(user)

def addStaleUsers():
    global usersVisitedSet, timeUsersVisited, replaysDownloaded 
    global replaysToDownload, usersToVisit
    currTime = time.time() 
    done = False
    while not done:
        if len(timeUsersVisited) == 0:
            done = True
        elif timeUsersVisited[0][-1] + REFRESH_TIME < currTime:
            # add current user to refresh list:
            user = timeUsersVisited.popleft()
            usersToVisit.append(user[0])
        else:
            done = True

def downloadReplay(replayId):
    baseUrl = 'http://generals.io/{}.gior'
    data = requests.get(baseUrl.format(replayId)).content
    with open('replays/{}.gior'.format(replayId), 'w') as fileOut:
        fileOut.write(data)

def saveState():
    global usersVisitedSet, timeUsersVisited, replaysDownloaded 
    global replaysToDownload, usersToVisit
    state = {
        'usersVisitedSet':usersVisitedSet,
        'timeUsersVisited':timeUsersVisited,
        'replaysDownloaded':replaysDownloaded,
        'replaysToDownload':replaysToDownload,
        'usersToVisit':deque(set(usersToVisit))
    }
    with open('scraperState.p', 'w') as fileOut:
        pickle.dump(state, fileOut)

def loadState():
    global usersVisitedSet, timeUsersVisited, replaysDownloaded 
    global replaysToDownload, usersToVisit
    with open('scraperState.p', 'rb') as fileIn:
        state = pickle.load(fileIn)
    usersVisitedSet = state['usersVisitedSet']
    timeUsersVisited = state['timeUsersVisited']
    replaysDownloaded = state['replaysDownloaded']
    replaysToDownload = state['replaysToDownload']
    usersToVisit = deque(set(state['usersToVisit']))

def scrape():
    global usersVisitedSet, timeUsersVisited, replaysDownloaded 
    global replaysToDownload, usersToVisit
    userList = list(usersToVisit)
    addStaleUsers()
    for i, user in enumerate(userList):
        print u'Visiting {}'.format(user), 
        print i, '/', len(userList)
        usersToVisit.popleft()
        time.sleep(1)
        replayList = getReplayListForUser(user)
        games = getReplayIdsAndUsersFromReplayList(replayList)
        updateLists(user, games)
    
    replayList = list(replaysToDownload)
    for i, replayId in enumerate(replayList):
        time.sleep(1)
        print 'Downloading {}.gior'.format(replayId), 
        print i, '/', len(replayList)
        downloadReplay(replayId)

    replaysDownloaded = replaysDownloaded | replaysToDownload
    replaysToDownload = set()


    print 'Num Users To Visit', len(usersToVisit)
    print 'Num Users Visited:', len(usersVisitedSet)
    print 'Num replays to download', len(replaysToDownload)
    print 'Num replays downloaded', len(replaysDownloaded)

def scraperLoop():
    while True:
        scrape()
        saveState()
