'''Functions interacting with the backend that will be used in app.py.
Written Spring 2019
Chloe Moon
'''
import sys
import MySQLdb

def getConn(db):
    '''Connects to local host'''
    conn = MySQLdb.connect(host='localhost',
                           user='ubuntu',
                           passwd='',
                           db=db)
    conn.autocommit(True) 
    return conn
    
def getAllNetworks(conn):
    '''Returns all the networks in the database, for the dropdown menu in the home page (no multiple)'''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select name from networks group by networks.name')
    return curs.fetchall()
    
def getCreators(conn,sid):
    '''Returns all creators of the show'''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select creators.name from creators, shows, showsCreators '
                    +'where showsCreators.sid=shows.sid'+
                    ' and showsCreators.cid=creators.cid and shows.sid=%s', (sid,))
    return curs.fetchall()

def getShow(conn,sid):
    '''Returns show with network name given sid'''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select networks.name as network, shows.* from shows inner join networks on '+
                    'networks.nid = shows.nid where sid = %s', (sid,))
    return curs.fetchone()

def getResultsByCreator(conn,term):
    '''Returns all shows based on the search term using creator'''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    term = '%' + term + '%'
    curs.execute('select * from shows, showsCreators, creators '
                +'where showsCreators.sid=shows.sid and creators.cid=showsCreators.cid '
                +'and creators.name like %s group by shows.title', (term,))
    return curs.fetchall()
    
def getResultsByNetwork(conn,term):
    '''Returns all shows based on the search term using network'''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select networks.name as network, shows.* from shows '+
                'inner join networks on networks.nid=shows.nid where networks.name= %s', (term,))
    return curs.fetchall()
    
def getResultsByTitle(conn,term):
    '''Returns all shows based on the search term using title'''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    term = '%' + term + '%'
    curs.execute('select * from shows where title like %s', (term,))
    return curs.fetchall()

def getNid(conn,networkName):
    '''Returns nid based on network name'''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select nid from networks where name = %s',[networkName])
    return curs.fetchone()['nid']
    
def getSid(conn,showTitle):
    '''Returns sid based on show name'''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select sid from shows where title = %s',[showTitle])
    return curs.fetchone()['sid']

def getCid(conn,creatorName):
    '''Returns cid based on creator name'''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('select cid from creators where name = %s',[creatorName])
    return curs.fetchone()['cid']

def insertShows(conn, title, year, genre, script, description, creator, network):
    '''Inserts show, creator, show&creator relationship etc. to the database, given form values'''
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    curs.execute('insert into networks (name) values(%s)', [network])
    nid = getNid(conn,network)
    curs.execute('insert into shows (title, nid, year, genre, script, description) values(%s, %s, %s, %s, %s, %s)', [title, nid, year, genre, script, description])
    curs.execute('insert into creators (name) values(%s)', [creator])
    sid = getSid(conn,title)
    cid = getCid(conn,creator)
    # insert relationship
    curs.execute('insert into showsCreators (sid,cid) values(%s, %s)',[sid,cid])
    # curs.execute('select * from shows')
    # curs.execute('select * from creators')

    

if __name__ == '__main__':
    conn = getConn('c9')