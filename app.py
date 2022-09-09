############################ U S U A L #########################################################################

from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc # for descending order in Scoreboard
from random import randrange
from datetime import datetime

############################ GLOBAL SPACE   #########################################################################


def reset_data():
    session.pop('name', None)
    session.pop('score', None)
    session.pop('life', None)
    session.pop('topleftcolor', None)
    session.pop('toprightcolor', None)
    session.pop('bottomleftcolor', None)
    session.pop('bottomrightcolor', None)
    session.pop('sol', None)
    session.pop('5050', None)
    session.pop('skip', None)
    session.pop('bonus', None)
    session.pop('5050running', None)

def save_data():
    result = scoreboard(name=session['name'],score=session['score'])
    if(scoreboard.query.filter_by(name=session['name']).first() == None):
        db.session.add(result)
        db.session.commit()
    else:
        x=scoreboard.query.filter_by(name=session['name']).first()
        if(x.score<session['score']):
            #delete
            db.session.delete(x)
            db.session.commit()
            #add
            db.session.add(result)
            db.session.commit()


def generate_colors():
    x=randrange(100000,999999)

    #select a random solution
    sol=randrange(1,5)
    session['sol']=sol

    x = str(x)

    #splice to change first 2 only (since that is related to color)
    first_2 = x[:2]
    last_4 = x[2:]

    first_2 = int(first_2)

    # since we dont want result to go beyond 99, reducing 30 from before itself
    if(first_2 >= 70):
        first_2 -= 30

    diff=(30-session['score'])
    # needed for when score goes beyond 30, so that diff doesnt go to 0
    if(diff<=1):
        diff=1
    # if some shitty players goes below 0, and random generates 99 for first 2, game will crash since difference can exceed 100. Hence it is needed to put upper bound
    if(diff>30):
        diff=30

    x = str(first_2) + last_4

    session['topleftcolor']=str(x)
    session['toprightcolor']=str(x)
    session['bottomleftcolor']=str(x)
    session['bottomrightcolor']=str(x)

    if sol==1:
        session['topleftcolor']=str(first_2+diff)+last_4
    elif sol==2:
        session['toprightcolor']=str(first_2+diff)+last_4
    elif sol==3:
        session['bottomleftcolor']=str(first_2+diff)+last_4
    else:
        session['bottomrightcolor']=str(first_2+diff)+last_4

############################ A P P   &   D B   #########################################################################

# Flask related stuffs
app = Flask(__name__)
app.secret_key = "avd" # THIS IS NEEDED TO VIEW SESSION VARIABLES AT USER END
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

############################# D A T A B A S E ######################################################################

# This creates a DB with name scoreboard
class scoreboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    score = db.Column(db.Integer)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # just to represent
    def __repr__(self):
        return '<Task %r %r %r>\n' % (self.id,self.name,self.score)

########################### H O M E P A G E  ########################################################################

# View for link '/' i.e.. home page is defined here
@app.route('/', methods=['POST', 'GET'])
def index():
    data = scoreboard.query.order_by(desc(scoreboard.score)).limit(25).all()
    return render_template('index.html',data=data)

############################ G A M E P A G E #################################################################

# View for link '/game' i.e.. game page is defined here
@app.route('/game', methods=['POST', 'GET'])
def game():

    # while user creation
    if request.method == 'POST':
        session['name']=request.form['name']
        session['score']=0
        session['life']=3
        session['5050']=2
        session['skip']=3
        session['bonus']=1
        session['5050running']=0
        generate_colors()
    return render_template('game.html')

###################################### V A L I D A T E #############################################################

# View for link '/validate' i.e.. validate operation is defined here
@app.route('/validate/<int:value>', methods=['POST', 'GET'])
def validate(value):
    if(session['5050running']==1):
        session['5050running']=0

    #if user exits
    if(value==0):
        save_data()
        dummydata= {'name': session['name'], 'score': session['score'] }
        reset_data()
        return render_template('gameover.html', data=dummydata)


    #if guess is correct
    if(session['sol']==value):
        if session['bonus']==0:
            session['score']+= (session['score']-20)
            session['bonus']=-1
        session['score'] += 1
        generate_colors()
        return redirect('/game')
    else:
        if session['bonus']==0:
            session['bonus']=-1
        session['score'] -= 5
        session['life'] -= 1

        #if lives are over
        if(session['life']==0):
            save_data()
            dummydata= {'name': session['name'], 'score': session['score'] }
            reset_data()
            return render_template('gameover.html', data=dummydata)

        generate_colors()
        return redirect('/game')

###################################### P O W E R U P S #############################################################

# View for link '/powerup' i.e.. validate operation is defined here
@app.route('/powerup/<int:value>', methods=['POST', 'GET'])
def powerup(value):
    # 50: 50

    if value==1:
        if session['5050']<=0:
            return redirect('/game')

        session['5050']-=1
        session['5050running']=1

        x=randrange(1,5)
        while x==session['sol']:
            x=randrange(1,5)
        y=randrange(1,5)
        while y==x or y==session['sol']:
            y=randrange(1,5)

        if x==1 or y==1:
            session['topleftcolor']="D3D3D3"
        if x==2 or y==2:
            session['toprightcolor']="D3D3D3"
        if x==3 or y==3:
            session['bottomleftcolor']="D3D3D3"
        if x==4 or y==4:
            session['bottomrightcolor']="D3D3D3"
        return redirect('/game')

    if value==2:
        if session['skip']<=0:
            return redirect('/game')

        session['skip']-=1

        generate_colors()

        return redirect('/game')

    if value==3:
        if session['bonus']>0:
            session['bonus']=0
            return redirect('/game')



######################### R U N     M A I N     P R O G R A M  ###################################################################

if __name__ == "__main__":
    app.run(debug=False)

##################################################################################################################