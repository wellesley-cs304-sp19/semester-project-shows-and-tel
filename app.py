'''Enables users to search and add TV shows to the database.

Written Spring 2019
Chloe Moon, Catherine Chen, Alice Zhou
'''
from flask import (Flask, render_template, make_response, url_for, request,
                   redirect, flash, session, send_from_directory, jsonify)
from werkzeug import secure_filename
import functions, random, math

import os
import bcrypt
import MySQLdb

app = Flask(__name__)
app.secret_key = 'qwygroyq34927843oew'
app.config['TRAP_BAD_REQUEST_ERRORS'] = True
app.config['UPLOADS'] = 'uploads'

#a list of common contentwarnings
#used in add() to allow users to choose from a set of warnings but also add new warnings
commonWarnings = ["Sex & Nudity","Violence & Gore","Profanity","Frightening & Intense Scenes"]
        
@app.route('/')
def index():
    '''Main page'''
    conn = functions.getConn('final_project')
    networks = functions.getAllNetworks(conn)
    contentwarnings = functions.getAllWarnings(conn)
    print 'app.py line 33 session ------'
    print session
    return render_template('home.html', networks=networks, 
                                        contentwarnings=contentwarnings)
    
@app.route('/add/', methods=['GET','POST'])
def add():
    '''Allows users to add a show to the database'''
    if request.method == 'GET':
        print 'app.py line 40 session ------'
        print session
        if 'username' not in session:
            flash('you are not logged in. Please login or join')
            return redirect( url_for('login') )
        conn = functions.getConn('final_project')
        contentwarnings = functions.getAllWarnings(conn)
        return render_template('add.html',contentwarnings=contentwarnings, 
                                commonWarnings=commonWarnings)
    if request.method == 'POST':
        conn = functions.getConn('final_project')
        title = request.form.get('title')
        year = request.form.get('year')
        genre = request.form.get('genre')
        script = request.form.get('script')
        try:
            script_file = request.files['file']
        except:
            script_file = False
        description = request.form.get('description')
        network = request.form.get('network')
        cwList = request.form.getlist('cw')
        creatorList=request.form.getlist('creator')
        genreList=request.form.getlist('genre')
        tag_names = request.form.getlist('tags')
        tag_vals = request.form.getlist('tag-args')
        filled = (title and year and genre and (script or script_file)
                and description and creatorList and network and cwList)
        if not(filled): # Should this be taken care on in front-end?
            flash("All fields should be completely filled")
            return redirect(request.referrer)
        else:
            if script_file:
                # Check to see if script file upload is a valid type
                filename = functions.isValidScriptType(script_file, title)
                if filename:
                    script = filename
                else: # file is not a valid type
                    return redirect(request.referrer)
            else:
                if 'http' not in script:
                    flash('''Invalid script link. Please include http:// at the 
                            beginning of the link.''')
                    return redirect(request.referrer)
            insert = functions.insertShows(conn, title, year, cwList, genreList, script, 
                                description, creatorList, network, 
                                tag_names, tag_vals)
            # locking failed
            if insert is False:
                flash("I'm sorry. This show already exists.")
            # locking succeeded
            else:
                insert
                print 'app.py linee 95 post session ----------'
                print session
                flash("TV show: " + title + " successfully inserted")
            return render_template('add.html')
    
@app.route('/displayAll/', methods=['GET'])
def displayAll():
    '''Displays all shows in the database'''
    if request.method == 'GET': # return all results
        conn = functions.getConn('final_project')
        shows = functions.getResultsByTitle(conn,"")
        return render_template('results.html', shows=shows)

@app.route('/profile/<int:sid>/', methods=['GET'])
def profile(sid):
    '''Displays profile page of the show based on show id (sid)'''
    if request.method == 'GET':
        conn = functions.getConn('final_project')
        show = functions.getShow(conn,sid)
        creators = functions.getCreators(conn,sid)
        warnings = functions.getWarnings(conn,sid)
        genres = functions.getGenres(conn,sid)
        tags = functions.getTags(conn,sid)
        username= session.get('username','')
        liked = functions.userLiked(conn,sid,username)
        return render_template('profile.html', show=show, creators=creators, 
                                warnings=warnings, tags=tags, genres=genres, username=username, liked=liked)
        

@app.route('/edit/<int:sid>/', methods=['GET','POST'])
def edit(sid):
    '''Edits/updates profile page of the show based on show id (sid)'''
    conn = functions.getConn('final_project')
    if request.method == 'GET':
        if 'username' not in session:
            flash('you are not logged in. Please login or join')
            return redirect( url_for('login') )
        show = functions.getShow(conn,sid)
        creators = functions.getCreators(conn,sid)
        warnings = functions.getWarnings(conn,sid)
        genres = functions.getGenres(conn,sid)
        tags = functions.getTags(conn, sid)
        return render_template('edit.html', show=show, creators=creators, 
                                warnings=warnings, tags=tags, genres=genres)
    if request.method == 'POST':
        newtitle = request.form['show-title']
        newnetwork = request.form['show-network']
        newyear = request.form['show-release']
        newdesc = request.form['show-description']
        newscript = request.form['show-script']
        try:
            newfile = request.files['file']
        except:
            newfile = False
        newgenrelist = request.form.getlist('show-genres')
        newcreators = request.form.getlist('show-creators')
        newcwList = request.form.getlist('show-warnings')
        tag_names = request.form.getlist('tags')
        tag_vals = request.form.getlist('tag-vals')
        if newfile:
            filename = functions.isValidScriptType(newfile, newtitle)
            if filename:
                newscript = filename
                print("*** NEW SCRIPT FILE ***")
                flash('''New script uploaded. Please hit SHIFT-REFRESH to refresh 
                the cache and see the new script if it has not updated.''')
            else: # file is not a valid type
                return redirect(request.referrer)
        else:
            print("No new script")
            if 'http' not in newscript:
                flash('''Invalid script link. Please include http:// at the 
                        beginning of the link.''')
                return redirect(request.referrer)
        functions.update(conn, sid, newtitle, newyear, newnetwork, 
                        newgenrelist, newcwList, newscript, newdesc,
                        newcreators, tag_names, tag_vals)
        return redirect(url_for('profile', sid=sid))


@app.route('/search/', methods=['POST'])
def search():
    '''Displays all the user requested search results'''
    if request.method == 'POST':
        conn = functions.getConn('final_project')
        title = request.form['title']
        network = request.form['network']
        creator = request.form['creator']
        genre = request.form['genre']
        contentwarning = request.form['contentwarning']
        tag_names = request.form.getlist('tags')
        tag_vals = request.form.getlist('tag-args')

        if (title=='' and network=='' and creator=='' and contentwarning==''
                      and tag_names=='' and tag_vals=='' and genre==''):
            flash("Search using at least one criteria")
            return redirect(request.referrer)
            
        if title:
            shows = functions.getResultsByTitle(conn,title)
            print shows
        elif network:
            shows = functions.getResultsByNetwork(conn,network)
        elif creator:
            shows = functions.getResultsByCreator(conn,creator)
        elif genre:
            shows = functions.getResultsByGenre(conn,genre)
        elif tag_names and tag_vals:
            shows = functions.getResultsByTags(conn, tag_names, tag_vals)
        elif contentwarning:
            shows = functions.getResultsByContentWarning(conn,contentwarning)
        return render_template('results.html', shows=shows)
        
# User session routes
@app.route('/login/', methods=['GET', 'POST'])
def login():
    '''lets a user log in'''
    if request.method=='GET':
        return render_template('login.html')
    if request.method=='POST':
        try:
            username = request.form['username']
            passwd = request.form['password']
            conn = functions.getConn('final_project')
            userRow = functions.checkPW(conn,username)
            if userRow is None:
                flash('login incorrect (app.py 201). Try again or join')
                return redirect(url_for('login'))
            hashed = userRow['hashed']
            #strings always come out as unicode, so have to encode
            if bcrypt.hashpw(passwd.encode('utf-8'),hashed.encode('utf-8')) == hashed:
                flash('successfully logged in as '+username)
                session['username'] = username
                session['logged_in'] = True
                return redirect(url_for('index'))
            else:
                flash('login incorrect. Try again or join')
                return redirect(url_for('login'))
        except Exception as err:
            print 'form submission error '+str(err)
            return redirect( url_for('login') )
            
@app.route('/logout/', methods=['POST','GET'])
def logout():
    '''lets a user log in'''
    try:
        if 'username' in session:
            # print session
            username = session['username']
            session.pop('username')
            session.pop('logged_in')
            flash('You are logged out')
            # print session
            return redirect(url_for('index'))
        else:
            flash('you are not logged in. Please login or join')
            return redirect( url_for('login') )
    except Exception as err:
        flash('some kind of error '+str(err))
        return redirect( url_for('index') )


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    '''lets a user to sign up/join'''
    if request.method=='GET':
        return render_template('signup.html')
    if request.method=='POST':
        try:
            username = request.form['username']
            passwd1 = request.form['password1']
            passwd2 = request.form['password2']
            if passwd1 != passwd2:
                flash('passwords do not match')
                return redirect( url_for('signup'))
            hashed = bcrypt.hashpw(passwd1.encode('utf-8'), bcrypt.gensalt())
            conn = functions.getConn('final_project')
            userRow = functions.checkUsername(conn,username)
            if userRow is not None: #check if username exists in the database
                flash('That username is taken')
                return redirect( url_for('signup') )
            functions.insertUser(conn,username,hashed)
            session['username'] = username
            session['logged_in'] = True
            flash('signed up and logged in as '+username)
            return redirect(url_for('index'))
        except Exception as err:
            print('form submission error '+str(err))
            return redirect( url_for('signup') )

# Other routes for non-templated pages
@app.route('/like/', methods=['POST'])
def like():
    '''Uses Ajax; return a json object instead of redirecting'''
    if request.method == 'POST': 
        conn = functions.getConn('final_project')
        #we need 3 pieces of information: 1) uid 2) showid (sid) 3) like or unlike
        username= session.get('username','')
        sid = request.form.get('sid')
        currentNum = request.form.get('currentNum')
        like = request.form.get('like')
        if like=='true':
            #like -- updating db
            like_updated = functions.addUserLikes(conn,sid,username)
        else:
            #unlike -- updating db
            like_updated = functions.deleteUserLikes(conn,sid,username)
        return jsonify(sid=sid, newNum=like_updated)
        
@app.route('/script/<sid>')
def script(sid):
    ''' This may be a kinda hacky thing to do, but if a script is local, aka
        stored in our filesystem, then we render it the normal way by passing
        the filepath to our profile template. If the script is external, aka
        we stored a http link in our database, then we do a straight redirect
        to that stored URL. '''
    conn = functions.getConn('final_project')
    curs = conn.cursor(MySQLdb.cursors.DictCursor)
    script, is_local = functions.getScript(conn, sid)
    print("**************** IN SCRIPT ROUTE ****************")
    print(script, is_local)
    print("ISSS LOCALL:", is_local)
    return script if (is_local=="local") else redirect(script)

if __name__ == '__main__':
    app.debug = True
    app.run('0.0.0.0',8082)
