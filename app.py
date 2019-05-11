'''Enables users to search and add TV shows to the database.

Written Spring 2019
Chloe Moon
'''
from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug import secure_filename
import functions, random, math


app = Flask(__name__)


app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])

app.config['TRAP_BAD_REQUEST_ERRORS'] = True

@app.route('/')
def index():
    '''Main page'''
    conn = functions.getConn('c9')
    networks = functions.getAllNetworks(conn)
    return render_template('home.html',networks=networks)
    
@app.route('/add/', methods=['GET','POST'])
def add():
    '''Allows users to add a show to the database'''
    conn = functions.getConn('c9')
    if request.method == 'GET':
        return render_template('add.html')
    if request.method == 'POST':
        conn = functions.getConn('c9')
        title = request.form.get('title')
        year = request.form.get('year')
        genre = request.form.get('genre')
        script = request.form.get('script')
        description = request.form.get('description')
        # creator = request.form.get('creator')
        network = request.form.get('network')
        # cw = request.form.get('contentwarning')
        cwList = request.form.getlist('cw')
        creatorList=request.form.getlist('creator')
        filled = (title and year and genre and script and description and creatorList[0] and network and cwList[0])
        if not(filled):
            flash("All fields should be completely filled")
            return redirect(request.referrer)
        else:
            databaseTitles = functions.getResultsByTitle(conn, title)
            if(len(databaseTitles)==0):
                functions.insertShows(conn, title, year, genre, cwList, script, description, creatorList, network)
                flash("TV show: " + title + " successfully inserted")
                return render_template('add.html')
            else:
                flash("TV Show already exists in database")
                return render_template('add.html')
        return render_template('add.html')

    
@app.route('/displayAll/', methods=['GET'])
def displayAll():
    '''Displays all shows in the database'''
    if request.method == 'GET': # return all results
        conn = functions.getConn('c9')
        shows = functions.getResultsByTitle(conn,"")
        return render_template('results.html', shows=shows)

@app.route('/profile/<int:sid>/', methods=['GET'])
def profile(sid):
    '''Displays profile page of the show based on show id (sid)'''
    if request.method == 'GET':
        conn = functions.getConn('c9')
        show = functions.getShow(conn,sid)
        creators = functions.getCreators(conn,sid)
        warnings = functions.getWarnings(conn,sid)
        # print show
        return render_template('profile.html', show=show, creators=creators, warnings=warnings)
        
@app.route('/edit/<int:sid>/', methods=['GET','POST'])
def edit(sid):
    '''Edits/updates profile page of the show based on show id (sid)'''
    conn = functions.getConn('c9')
    if request.method == 'GET':
        show = functions.getShow(conn,sid)
        creators = functions.getCreators(conn,sid)
        warnings = functions.getWarnings(conn,sid)
        return render_template('edit.html', show=show, creators=creators, warnings=warnings)
    if request.method == 'POST':
        oldshow = functions.getShow(conn,sid)
        newtitle = request.form['show-title']
        oldnetwork = oldshow['network']
        newnetwork = request.form['show-network']
        newyear = request.form['show-release']
        newdesc = request.form['show-description']
        newscript = request.form['show-script']
        newgenre = request.form['show-genre']
        newcreators = request.form['show-creators']
        oldcwList = functions.getWarnings(conn,sid)
        newcwList = request.form.getlist('show-warning')
        functions.update(conn, sid, newtitle, newyear,oldnetwork,newnetwork, newgenre, oldcwList, newcwList, newscript, newdesc, newcreators)
        return redirect(url_for('edit', sid=sid))
        
        
    
@app.route('/search/', methods=['POST'])
def search():
    '''Displays all the user requested search results'''
    if request.method == 'POST':
        conn = functions.getConn('c9')
        title = request.form['title']
        network = request.form['network']
        creator = request.form['creator']
        if title:
            shows = functions.getResultsByTitle(conn,title)
        if network:
            shows = functions.getResultsByNetwork(conn,network)
        if creator:
            shows = functions.getResultsByCreator(conn,creator)
        if title=='' and network=='' and creator=='':
            flash("Search using at least one criteria")
            return redirect(request.referrer)
        return render_template('results.html', shows=shows)

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8082)
