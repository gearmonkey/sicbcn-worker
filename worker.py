import sys, os, os.path, random, time
import logging

import simplejson
import requests
from firebase import firebase

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)

conn = firebase.FirebaseApplication('https://sonar-11442.firebaseio.com', None)

def collect_tracks(top='./sonar_data/albums/'):
    tracks = []
    for filepath in list(os.walk(top))[0][2]:
        if not filepath[-4:] == 'json':
            continue
        logging.debug( filepath )
        with open(os.path.join(top, filepath)) as rh:
            data = simplejson.loads(rh.read())
        for track in data['tracks']['data']:
            tracks.append(track)
    return tracks

def load_supplemental_data(filepath='sonar_data/sonar_metadata_all.json'):
    with open(filepath) as rh:
        supplement = simplejson.loads(rh.read())
    return supplement

def main(argv=sys.argv):
    """the business end of the situation"""
    logging.info( "loading tracks..." )
    teams_a_pool = collect_tracks(top='./sonar_data/albums/_day/')
    teams_b_pool = collect_tracks(top='./sonar_data/albums/_night/')
    random.shuffle(teams_a_pool)
    random.shuffle(teams_b_pool)
    logging.info( "loading supplemental track data.." )
    supplement = load_supplemental_data()
    logging.info( "listening..." )
    while True:
        for idx,(team_id, data) in enumerate(conn.get('/teams', None).items()):
            if data.get('findNextTrack', None):
                logging.info( 'grabbing a new track for team %s'%data['teamName'] )
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
                    logging.debug( 'candidate track has bpm of %s'% bpm )
                logging.info( "new track will be %s by %s"%(full_track_details['title'],  full_track_details['artist']['name']) )
                try:
                    full_track_details['crop'] = supplement[str(newTrack['id'])]['crop']
                except KeyError:
                    if full_track_details.get('duration', 0) < 30:
                        full_track_details['crop'] = [0.0, 30.0]
                    else:
                        midpoint = full_track_details['duration']/2.0
                        full_track_details['crop'] = [midpoint-15, midpoint+15]
                logging.debug(  'candidate track has crop points of %s'%full_track_details['crop'] )
                res = conn.put('/teams/%s'%team_id, 'nextTrack', full_track_details)
                res = conn.put('/teams/%s'%team_id, 'findNextTrack', False)
        time.sleep(.5)


if __name__ == '__main__':
    main()