import sys, os, os.path, random, time

import simplejson
import requests
from firebase import firebase

conn = firebase.FirebaseApplication('https://sonar-11442.firebaseio.com', None)

def collect_tracks(top='./sonar_data/albums/'):
    tracks = []
    for filepath in list(os.walk(top))[0][2]:
        if not filepath[-4:] == 'json':
            continue
        print filepath
        with open(os.path.join(top, filepath)) as rh:
            data = simplejson.loads(rh.read())
        for track in data['tracks']['data']:
            tracks.append(track)
    return tracks

def main(argv=sys.argv):
    """the business end of the situation"""
    print "loading tracks..."
    teams_a_pool = collect_tracks(top='./sonar_data/albums/_day/')
    teams_b_pool = collect_tracks(top='./sonar_data/albums/_night/')
    random.shuffle(teams_a_pool)
    random.shuffle(teams_b_pool)
    print "listening..."
    while True:
        for idx,(team_id, data) in enumerate(conn.get('/teams', None).items()):
            if data.get('findNextTrack', None):
                print 'grabbing a new track for team', data['teamName']
                bpm = None
                while not bpm > 0:
                    try:
                        if idx%2 == 0:
                            newTrack = teams_a_pool.pop()
                        else:
                            newTrack = teams_b_pool.pop()
                    except IndexError:
                        if idx%2 == 0:
                            teams_a_pool = collect_tracks()
                            random.shuffle(teams_a_pool)
                            newTrack = teams_a_pool.pop()
                        else:
                            teams_b_pool = collect_tracks()
                            random.shuffle(teams_b_pool)
                            newTrack = teams_b_pool.pop()
                    full_track_details = requests.get('http://api.deezer.com/track/%s'%newTrack['id']).json()
                    bpm = full_track_details.get('bpm', None)
                    print 'candidate track has bpm of', bpm
                print "new track will be", full_track_details['title'], 'by', full_track_details['artist']['name']
                res = conn.put('/teams/%s'%team_id, 'nextTrack', full_track_details)
                res = conn.put('/teams/%s'%team_id, 'findNextTrack', False)
        time.sleep(.5)


if __name__ == '__main__':
    main()