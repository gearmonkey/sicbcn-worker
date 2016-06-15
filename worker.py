import sys, os, os.path, random, time

import simplejson
from firebase import firebase

conn = firebase.FirebaseApplication('https://sonar-11442.firebaseio.com', None)

def collect_tracks(top='./sonar_data/albums/'):
    tracks = []
    for filepath in list(os.walk(top))[0][2]:
        print filepath
        with open(os.path.join(top, filepath)) as rh:
            data = simplejson.loads(rh.read())
        for track in data['tracks']['data']:
            tracks.append(track)
    return tracks

def main(argv=sys.argv):
    """the business end of the situation"""
    print "loading tracks..."
    tracks = collect_tracks()
    random.shuffle(tracks)
    teams_a_pool = tracks[:len(tracks)/2]
    teams_b_pool = tracks[len(tracks)/2:]
    print "listening..."
    while True:
        for team_id, data in conn.get('/teams', None).items():
            if data['findNextTrack']:
                print 'grabbing a new track for team', data['teamName']
                try:
                    newTrack = tracks.pop()
                except IndexError:
                    tracks = collect_tracks()
                    random.shuffle(tracks)
                    newTrack = tracks.pop()
                print "new track will be", newTrack['title'], 'by', newTrack['artist']['name']
                res = conn.put('/teams/%s'%team_id, 'nextTrack', newTrack)
                res = conn.put('/teams/%s'%team_id, 'findNextTrack', False)
        time.sleep(.5)


if __name__ == '__main__':
    main()