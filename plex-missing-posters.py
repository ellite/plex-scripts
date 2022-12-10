# This script goes through a library, finds unmatched content and tries to match it,
# after that finds content missing posters. Triggers a metadata refresh and selects the first available poster
# Replace everything in <> with your own data

# Dependencies:
# pip install alive-progress
# pip install plexapi

from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from alive_progress import alive_bar
from datetime import datetime
import time, requests, urllib

start = datetime.now()

baseurl = 'http://plex.ip:42000'
token = '<YOUR_TOKEN_HERE>'
print("Connecting to ", baseurl)
plex = PlexServer(baseurl, token)
library = "<LIBRARY_NAME>"
print("Connected to ", plex)
logFile = "<LOG_FILE_NAME>"

open(logFile, 'w').close()
f = open(logFile, "a")
f.write("Started: " + start.strftime("%H:%M:%S") + "\n")

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36' }
missing = 0
valid = 0

print("Finding unmatched content in " + library + " ...")
tv = plex.library.section(library)
tvSearch = tv.search(unmatched=True)
if (len(tvSearch) > 0):
    with alive_bar(len(tvSearch), enrich_print=False) as bar:
        bar.title = library
        for unmatched in tvSearch:
            print(bcolors.WARNING + "Unmatched found: " + bcolors.ENDC + unmatched.title)
            try:
                unmatched.fixMatch(auto=True)
            except:
                print(bcolors.FAIL + "Couldn't match: " + unmatched.title + bcolors.ENDC)
                f.write("\nUnmatched content: " + unmatched.title)
            bar()

print("Finding missing posters in " + library + " ...")
tvSearch = tv.search(unmatched=False)
with alive_bar(len(tvSearch), enrich_print=False) as bar:
    bar.title = library
    for video in tvSearch:
        statusCode = 0
        if (str(video.posterUrl) != 'None'):
            try:
                statusCode = requests.get(video.posterUrl, headers=headers).status_code
            except:
                statusCode = 404
        else:
            statusCode = 404

        if (statusCode == 404):
            print(bcolors.WARNING + video.title + ": " + bcolors.FAIL + "Missing Poster" + bcolors.ENDC)
            f.write("\nMissing poster: " + video.title)
            if (len(video.posters()) > 0):
                video.setPoster(video.posters()[0])
            video.refresh()
            missing = missing + 1
        else:
            print(bcolors.WARNING + video.title + ": " + bcolors.OKGREEN + "Valid Poster" + bcolors.ENDC)
            valid = valid + 1
        bar()

end = datetime.now()
f.write("\nEnded: " + end.strftime("%H:%M:%S"))
print("Total misisng posters: ", missing)
f.write("\nTotal missing posters: " + str(missing))
print("Total valid posters: ", valid)
f.write("\nTotal valid posters: " + str(valid))
f.close()
