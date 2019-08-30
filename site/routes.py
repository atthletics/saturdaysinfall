from flask import Flask, render_template, request, session, redirect, url_for
from forms import SignupForm, SigninForm, SubmitEmail, PwdEmail, PwdSession
from forms import ProfileForm, CreateLeague, CreateSquad, LeaguePwd, SquadPwd
import smtplib, os, random, string
from models import db, User, League, LeagueUser, Squad

app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')
APP_TEMPLATE = os.path.join(APP_ROOT, 'template')

SQLALCHEMY_DATABASE_URI = 
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["DEBUG"] = False
db.init_app(app)

# ---------------- #
# manual .csv load #
# ---------------- #

# 1. Open Bash terminal (not MySQL terminal)
# 2. Connect to DB:
#   - mysql -h atthletics.mysql.pythonanywhere-services.com -u atthletics 'atthletics$mysql' -p --local-infile=1
# 3. Load file in static files dir:
#   - /home/atthletics/site/static/files/
# 4. Execute load:
#   - LOAD DATA LOCAL INFILE '/home/atthletics/site/static/files/ENTER_YOUR_FILE_NAME.csv' INTO TABLE users FIELDS TERMINATED BY ',' ENCLOSED BY '"' LINES TERMINATED BY '\r\n';

app.secret_key = 

# ------------------------ #
# 1. Index                 #
# 2. Authentication Routes #
# 3. Profile Routes        #
# 4. League Routes         #
# 5. Basic Routes          #
# ------------------------ #

@app.route('/')
@app.route('/index')
def index():
    # articles for homepage
    qry = db.session.execute("""
        select
          article_id,
          article_name,
          article_desc,
          create_ts,
          article_file,
          slide_id
        from articles
        where is_archived = 0
    """)
    return render_template("index.html", articles=qry.fetchall())


# --------------------- #
# Authentication Routes #
# ----------------------#

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # check if already a user
    if 'user_id' in session:
        return redirect(url_for('index'))

    # registration form
    register = SignupForm()
    if request.method == 'POST':
        if register.validate() == False:
            return render_template('users/signup.html', form=register)
        else:
            try:
                # write user to database
                newuser = User(register.first_name.data, register.last_name.data, register.email.data, register.username.data, register.password.data)
                db.session.add(newuser)
                db.session.commit()
                # create session
                session['user_id'] = newuser.user_id
                session['email'] = newuser.email
                session['username'] = newuser.username
                session['logged_in'] = True
                return redirect(url_for('index'))
            except Exception as err:
                e = list(register.email.errors)
                e.append('Email address already exists.')
                register.email.errors = tuple(e)
                return render_template('users/signup.html', form=register)

    elif request.method == 'GET':
        return render_template("users/signup.html", form=register)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    # check if already logged in
    if 'user_id' in session:
        return redirect(url_for('index'))

    # login form
    login = SigninForm()
    if request.method == "POST":
        if login.validate() == False:
            return render_template("users/signin.html", form=login)
        else:
            email = login.email.data
            password = login.password.data
            user = User.query.filter_by(email=email).first()
            if not user:
                e = list(login.email.errors)
                e.append('Invalid email.')
                login.email.errors = tuple(e)
                return render_template('users/signin.html', form=login)
            elif user.pwdhash == 'FORCE_RESET':
                token = SubmitEmail()
                force_reset = """
                    We need you to reset your password.
                    There is nothing to worry about, it is just part of the website revamp.
                    You may use the same password as before.
                """
                return render_template('users/reset_token.html', form=token, message=force_reset)
            elif user is not None and user.check_password(password):
                session['user_id'] = user.user_id
                session['email'] = login.email.data
                session['username'] = user.first_name + ' ' + user.last_name
                session['logged_in'] = True
                return redirect(url_for('index'))
            else:
                e = list(login.password.errors)
                e.append('Incorrect password.')
                login.password.errors = tuple(e)
                return render_template('users/signin.html', form=login)

    elif request.method == "GET":
        return render_template('users/signin.html', form=login)

@app.route('/password_reset', methods=['GET', 'POST'])
def password_reset():
    known = PwdSession()
    unknown = PwdEmail()
    # check if already logged in
    if 'user_id' in session:
        if request.method == "POST":
            if known.validate() == False:
                return render_template('users/password_reset.html', form=known)
            else:
                current = known.current.data
                new = known.new.data
                user = User.query.filter_by(user_id=int(session['user_id'])).first()
                newPwd = User(user.first_name, user.last_name, user.email, new, )
                if user.check_password(current):
                    User.query.filter_by(user_id=int(session['user_id'])).update( dict(pwdhash=newPwd.pwdhash, reset_token=None) )
                    db.session.commit()
                    return redirect(url_for('profile'))
                else:
                    e = list(known.current.errors)
                    e.append('Incorrect password.')
                    known.email.errors = tuple(e)
                    return render_template('users/password_reset.html', form=known)

        elif request.method == "GET":
            return render_template('users/password_reset.html', form=known)

    else:
        if request.method == "POST":
            if unknown.validate() == False:
                return render_template('users/password_reset.html', form=unknown)
            else:
                email = unknown.email.data
                valid = unknown.reset_token.data
                password = unknown.password.data
                user = User.query.filter_by(email=email, reset_token=valid).first()
                newPwd = User(user.first_name, user.last_name, user.email, user.username, password)
                if user is not None:
                    User.query.filter_by(email=email).update( dict(pwdhash=newPwd.pwdhash, reset_token=None) )
                    db.session.commit()
                    return redirect(url_for('signin'))
                else:
                    e = list(unknown.reset_token.errors)
                    e.append('Invalid reset token.')
                    unknown.email.errors = tuple(e)
                    return render_template('users/password_reset.html', form=unknown)

        elif request.method == "GET":
            return render_template('users/password_reset.html', form=unknown)

@app.route('/reset_token', methods=['GET', 'POST'])
def reset_token():

    token = SubmitEmail()
    known = PwdSession()
    unknown = PwdEmail()
    def token_generator(size=20, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
	    return ''.join(random.choice(chars) for _ in range(size))

    # check if logged in
    if 'user_id' in session:
        return render_template('users/password_reset.html', form=known)
    else:
        if request.method == "POST":
            # check if valid email
            if token.validate() == False:
                return render_template('users/reset_token.html', form=token)
            else:
                # query email
                email = token.email.data
                user = User.query.filter_by(email=email).first()

                # verify email is used
                if user is not None:

                    # write reset_token to user table
                    username = user.first_name + ' ' + user.last_name
                    usertoken = token_generator()
                    User.query.filter_by(user_id=user.user_id).update( dict(reset_token = usertoken) )
                    db.session.commit()

                    # email token to provided email
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.ehlo()
                    server.starttls()
                    server.login('atthletics@gmail.com', 'Pk%&ZYYsGN&OrtTya5Zp')
                    sender = 'DoNotReply@atthletics.com'
                    receivers = [email]
                    message = """
Hello %s,

Here is the password reset token you requested:
%s

After sending this, we redirected you to the reset page. Just paste that token in the applicable field.
If you did not request this token, or requested by accident, you can ignore this email!

If you need help, do not reply to this email. This is our monitored email:
atthletics@gmail.com
                    """ % (username, usertoken)
                    server.sendmail(sender, receivers, message)
                    server.quit()

                    # redirect user to password reset form
                    return render_template('users/password_reset.html', form=unknown)
                else:
                    e = list(token.email.errors)
                    e.append('Email was not found.')
                    token.email.errors = tuple(e)
                    return render_template('users/reset_token.html', form=token)

        elif request.method == "GET":
            return render_template('users/reset_token.html', form=token)


# -------------- #
# Profile Routes #
# -------------- #

@app.route('/profile', methods=['GET','POST'])
def profile():
    # must be signed in
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    profile = ProfileForm()
    if request.method == "GET":
        # get user data
        qry = db.session.execute("""
            select
                user_id,
                first_name,
                last_name,
                email,
                SUBSTR(username,2) as username,
                create_ts
            from users
            where
                user_id = :user
        """, {'user': int(session['user_id'])})
        user = qry.first()

        # profile form
        profile.first_name.default = user.first_name
        profile.last_name.default = user.last_name
        profile.email.default = user.email
        profile.username.default = user.username
        profile.create_ts.default = user.create_ts
        profile.process()
        return render_template('users/profile.html', form=profile)

    elif request.method == "POST":
        if profile.validate() == False:
            return render_template('users/profile.html', form=profile)
        else:
            User.query.filter_by(user_id=int(session['user_id'])).update(
                dict(
                    first_name = profile.first_name.data,
                    last_name = profile.last_name.data,
                    email = profile.email.data,
                    username = '@' + profile.username.data
                )
            )
            db.session.commit()
            return redirect(url_for('index'))

# ------------ #
# Squad Routes #
# ------------ #

@app.route('/create_squad', methods=['GET', 'POST'])
def create_squad():
    # must be signed in
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    # registration form
    squad = CreateSquad()
    if request.method == 'POST':
        if squad.validate() == False:
            return render_template('create_squad.html', form=squad)
        else:
            try:
                # write squad to database
                newSquad = Squad(squad.squad_name.data, squad.squad_pwd.data, int(session['user_id']))
                db.session.add(newSquad)
                db.session.commit()
                # update user squad
                userSquad = Squad.query.filter_by(squad_name=squad.squad_name.data).first()
                User.query.filter_by(user_id=int(session['user_id'])).update( dict(squad_id = userSquad.squad_id) )
                db.session.commit()
                return redirect(url_for('index'))
            except:
                e = list(squad.squad_name.errors)
                e.append('This squad already exists.')
                squad.email.errors = tuple(e)
                return render_template('create_squad.html', form=squad)

    elif request.method == 'GET':
        return render_template("create_squad.html", form=squad)

@app.route('/squad', methods=['GET'])
def squad():
    # must be signed in
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    # squad check query
    user = User.query.filter_by(user_id=int(session['user_id'])).first()
    if user.squad_id == 1:
        # free agent query
        fa = db.session.execute("""
            select
                s.squad_id,
                s.squad_name,
                u.email as leader,
                m.member_cnt,
                if(ifnull(s.squad_pwd,'') = '', 'No', 'Yes') is_private
            from squads s
            left join users u
              on s.leader_id = u.user_id
            left join (
              select
                squad_id,
                count(*) as member_cnt
              from users
              group by
                squad_id
            ) m
              on s.squad_id = m.squad_id
        """)
        return render_template('join_squad.html', squads=fa.fetchall(), squad_id=user.squad_id)

    else:
        # member query
        squad = Squad.query.filter_by(squad_id=user.squad_id).first()
        mbr = db.session.execute("""
            select
                user_id,
                concat(first_name, ' ', last_name) as member,
                username,
                email
            from users
            where
              squad_id = :squad
        """
        , {'squad': user.squad_id})
        return render_template('squad.html', members=mbr.fetchall(), squad_name=squad.squad_name)

@app.route('/squad_profile/<int:squad_id>', methods=['GET','POST'])
def squad_profile(squad_id):
    # must be signed in
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    password_form = SquadPwd()
    # get squad data
    squad = Squad.query.filter_by(squad_id=int(squad_id)).first()
    if request.method == "GET":
        return render_template('squad_profile.html',
            form=password_form,
            squad_id=squad.squad_id,
            squad_name=squad.squad_name)

    elif request.method == "POST":
        if squad.squad_pwd == password_form.password.data:
            User.query.filter_by(user_id=int(session['user_id'])).update( dict(squad_id = squad.squad_id) )
            db.session.commit()
            return redirect(url_for('index'))
        else:
            e = list(password_form.password.errors)
            e.append('The password was incorrect.')
            password_form.password.errors = tuple(e)
            return render_template("squad_profile.html",
                form=password_form,
                squad_id=squad.squad_id,
                squad_name=squad.squad_name)

@app.route('/leave_squad', methods=['POST'])
def leave_squad():
    # must be signed in
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    User.query.filter_by(user_id=int(session['user_id'])).update( dict(squad_id = 1) )
    db.session.commit()
    return redirect(url_for('index'))

# ------------- #
# League Routes #
# ------------- #

@app.route('/create_league', methods=['GET', 'POST'])
def create_league():
    # must be signed in
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    # registration form
    league = CreateLeague()
    if request.method == 'POST':
        if league.validate() == False:
            return render_template('create_league.html', form=league)
        else:
            try:
                # write league to database
                newLeague = League(league.league_name.data, league.league_pwd.data, int(session['user_id']))
                db.session.add(newLeague)
                db.session.commit()
                lid = League.query.filter_by(league_name=league.league_name.data).first()

                # add users
                addUser = LeagueUser(lid.league_id, int(session['user_id']))
                db.session.add(addUser)
                db.session.commit()
                return redirect(url_for('index'))
            except:
                e = list(league.league_name.errors)
                e.append('This league already exists.')
                league.email.errors = tuple(e)
                return render_template('create_league.html', form=league)

    elif request.method == 'GET':
        return render_template("create_league.html", form=league)

@app.route('/league', methods=['GET'])
def league():
    # must be signed in
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    # league query
    qry = db.session.execute("""
        select
            l.league_id,
            l.league_name,
            u.email as owner,
            lu.entrant_id
        from leagues_users lu
        inner join leagues l
          on lu.league_id = l.league_id
        inner join users u
          on l.owner_id = u.user_id
        where lu.user_id = :user
    """
    , {'user': int(session['user_id'])})
    return render_template('league.html', leagues=qry.fetchall())

@app.route('/league_profile/<int:league_id>', methods=['GET','POST'])
def league_profile(league_id):
    # must be signed in
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    password_form = LeaguePwd()
    # get league data
    league = League.query.filter_by(league_id=int(league_id)).first()
    if request.method == "GET":
        return render_template('league_profile.html',
            form=password_form,
            league_id=league.league_id,
            league_name=league.league_name)

    elif request.method == "POST":
        if league.league_pwd == password_form.password.data:
            league_user = LeagueUser(league.league_id, int(session['user_id']))
            db.session.add(league_user)
            db.session.commit()
            return redirect(url_for('index'))
        else:
            e = list(password_form.password.errors)
            e.append('The password was incorrect.')
            password_form.password.errors = tuple(e)
            return render_template("league_profile.html",
                form=password_form,
                league_id=league.league_id,
                league_name=league.league_name)

@app.route('/join_league', methods=['GET', 'POST'])
def join_league():
    # must be signed in
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    if request.method == 'GET':
        # league query
        qry = db.session.execute("""
            select
                l.league_id,
                l.league_name,
                if(l.league_pwd = '', 'No', 'Yes') is_private,
                u.email as owner,
                count(tu.user_id) as members_cnt,
                max(if(lu.league_id is null, 'No', 'Yes')) is_member
            from leagues l
            inner join users u
              on l.owner_id = u.user_id
            inner join leagues_users tu
              on l.league_id = tu.league_id
            left join leagues_users lu
              on l.league_id = lu.league_id
              and lu.user_id = :user
            group by
                l.league_id,
                l.league_name,
                if(l.league_pwd is null, 'Yes', 'No'),
                u.email
        """
        , {'user': int(session['user_id'])})
        return render_template('join_league.html', leagues=qry.fetchall())

    elif request.method == 'POST':
        league_user = LeagueUser(int(request.form['league_id']), int(session['user_id']))
        db.session.add(league_user)
        db.session.commit()

        # league query
        qry = db.session.execute("""
            select
                l.league_id,
                l.league_name,
                u.email as owner,
                lu.entrant_id
            from leagues_users lu
            inner join leagues l
              on lu.league_id = l.league_id
            inner join users u
              on l.owner_id = u.user_id
            where lu.user_id = :user
        """
        , {'user': int(session['user_id'])})
        return render_template('league.html', leagues=qry.fetchall())

# ---------------- #
# Standings Routes #
# ---------------- #

@app.route('/standings/<int:league_id>', methods=['GET','POST'])
def standings(league_id):
    # must be signed in
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    if request.method == 'GET':
        league = League.query.filter_by(league_id=league_id).first()
        scores = db.session.execute("""
            select
              *, cast(@rank := @rank + 1 as char) AS rank
            from (
                select
                    lu.user_id,
                    u.username,
                    ifnull(sum(if(s.is_upset = True, s.spread, 0)),0) as score,
                    ifnull(count(if(s.is_upset = True, s.game_id, null)),0) as picks
                from leagues_users lu
                inner join users u
                  on lu.user_id = u.user_id
                left join ud_picks p
                  on lu.user_id = p.user_id
                  and p.is_invalid = False
                left join ud_games g
                  on p.game_id = g.game_id
                left join ud_spreads s
                  on g.game_id = s.game_id
                where
                  lu.league_id = 1
                group by
                    lu.user_id,
                    u.username
                order by 3 desc, 4 desc, 2
            ) scores
            cross join (SELECT @rank := 0) r
        """
        , {'league': league_id})
        return render_template('standings.html', standing=scores.fetchall(), user_id=session['user_id'],
                                league_id=league_id, league_name=league.league_name, week=0)

    elif request.method == 'POST':
        week = int(request.form.get('week'))
        league = League.query.filter_by(league_id=league_id).first()

        if week == 0:
            scores = db.session.execute("""
                select
                  *, cast(@rank := @rank + 1 as char) AS rank
                from (
                    select
                        lu.user_id,
                        u.username,
                        ifnull(sum(if(s.is_upset = True, s.spread, 0)),0) as score,
                        ifnull(count(if(s.is_upset = True, s.game_id, null)),0) as picks
                    from leagues_users lu
                    inner join users u
                      on lu.user_id = u.user_id
                    left join ud_picks p
                      on lu.user_id = p.user_id
                      and p.is_invalid = False
                    left join ud_games g
                      on p.game_id = g.game_id
                    left join ud_spreads s
                      on g.game_id = s.game_id
                    where
                      lu.league_id = 1
                    group by
                        lu.user_id,
                        u.username
                    order by 3 desc, 4 desc, 2
                ) scores
                cross join (SELECT @rank := 0) r
            """
            , {'league': league_id})
        else:
            scores = db.session.execute("""
                select
                  user_id,
                  username,
                  sum(
                    case
                      when is_upset = True and is_special = True then spread*2
                      when is_upset = True then spread
                      else 0
                    end
                  ) as total_points,

                  max(
                    case
                      when pick_number = 1 and is_special = True
                        then concat(underdog, ': ', spread * 2, ' (special)')
                      when pick_number = 1
                        then concat(underdog, ': ', spread)
                      else null
                    end
                  ) as pick_1,
                  max(
                    case
                      when pick_number = 1 and is_upset = True then 1
                      else 0
                    end
                  ) as p1_upset,

                  max(
                    case
                      when pick_number = 2 and is_special = True
                        then concat(underdog, ': ', spread * 2, ' (special)')
                      when pick_number = 2
                        then concat(underdog, ': ', spread)
                      else null
                    end
                  ) as pick_2,
                  max(
                    case
                      when pick_number = 2 and is_upset = True then 1
                      else 0
                    end
                  ) as p2_upset,

                  max(
                    case
                      when pick_number = 3 and is_special = True
                        then concat(underdog, ': ', spread * 2, ' (special)')
                      when pick_number = 3
                        then concat(underdog, ': ', spread)
                      else null
                    end
                  ) as pick_3,
                  max(
                    case
                      when pick_number = 3 and is_upset = True then 1
                      else 0
                    end
                  ) as p3_upset,

                  max(
                    case
                      when pick_number = 4 and is_special = True
                        then concat(underdog, ': ', spread * 2, ' (special)')
                      when pick_number = 4
                        then concat(underdog, ': ', spread)
                      else null
                    end
                  ) as pick_4,
                  max(
                    case
                      when pick_number = 4 and is_upset = True then 1
                      else 0
                    end
                  ) as p4_upset,

                  max(
                    case
                      when pick_number = 5 and is_special = True
                        then concat(underdog, ': ', spread * 2, ' (special)')
                      when pick_number = 5
                        then concat(underdog, ': ', spread)
                      else null
                    end
                  ) as pick_5,
                  max(
                    case
                      when pick_number = 5 and is_upset = True then 1
                      else 0
                    end
                  ) as p5_upset

                from (
                    select
                        p.user_id,
                        u.username,
                        r.pick_number,
                        t.espn_team_name as underdog,
                        coalesce(s.spread, 0) as spread,
                        s.is_upset,
                        p.is_special
                    from ud_picks p
                    inner join users u
                      on p.user_id = u.user_id
                    inner join (
                        select
                            a.user_id,
                            a.pick_id,
                            count(*) AS pick_number
                        from ud_picks a
                        inner join ud_picks b
                          on a.user_id = b.user_id
                          and a.pick_id >= b.pick_id
                          and b.league_id = :league
                          and b.is_invalid = False
                        where
                          a.is_invalid = False
                          and a.league_id = :league
                        group by
                          a.user_id,
                          a.pick_id
                    ) r
                      on r.pick_id = p.pick_id
                    inner join ud_games g
                      on p.game_id = g.game_id
                    inner join ud_spreads s
                      on g.game_id = s.game_id
                    inner join teams t
                      on s.team_id = t.atthletics_team_id
                    where
                      p.league_id = :league
                      and g.week_id = :week
                      and p.is_invalid = False
                      and (
                        date_add(now(), interval -4 hour) >= g.game_ts
                        or p.user_id = :user
                      )
                ) picks

                group by
                  username,
                  user_id
                order by 3 desc
            """
            , {'league': league_id, 'week': int(week), 'user': session['user_id']})

        return render_template('standings.html', standing=scores.fetchall(), user_id=session['user_id'],
                                league_id=league_id, league_name=league.league_name, week=week)

# ------------ #
# Picks Routes #
# ------------ #

@app.route('/picks/<int:league_id>', methods=['GET', 'POST'])
def picks(league_id):
    # must be signed in
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    if request.method == 'GET':
        games = db.session.execute("""
            select
                g.game_id,
                date_format(g.game_ts,"%W, %b. %e, %Y") as game_dt,
                date_format(g.game_ts,"%r") as game_ts,
                g.week_id,
                t1.espn_team_name as home_team,
                g.home_score,
                t2.espn_team_name as away_team,
                g.away_score,
                g.is_final,
                case
                  when coalesce(s1.spread, s2.spread) is null then 'N/A'
                  when coalesce(s1.spread, s2.spread) = 0 then 'EVEN'
                  when s1.spread is not null then t1.espn_team_name
                  else t2.espn_team_name
                end as underdog,
                if(date_add(now(), interval -4 hour) >= g.game_ts,'Y','N') as is_locked,
                if(p.game_id is not null, 'Y','N') as picked,
                if(p.is_special = 1, 'Y','N') as is_special,
                coalesce(s1.spread, s2.spread, 0) as spread
            from ud_games g
            inner join teams t1
              on g.home_id = t1.atthletics_team_id
            inner join teams t2
              on g.away_id = t2.atthletics_team_id
            left join ud_picks p
              on g.game_id = p.game_id
              and p.user_id = :user
              and p.league_id = :league
              and p.is_invalid = False
            left join ud_spreads s1
              on g.game_id = s1.game_id
              and g.home_id = s1.team_id
            left join ud_spreads s2
              on g.game_id = s2.game_id
              and g.away_id = s2.team_id
            where
              g.game_ts <> 0
              and (
                date_add(now(), interval -4 hour) < g.game_ts
                or p.game_id is not null)
            order by
              p.game_id desc,
              g.game_ts
        """,
        {'league': league_id, 'user': session['user_id']})

        # week query
        week_qry = db.session.execute("""
            select
                min(g.week_id) as week_id
            from ud_games g
            where
              date_add(now(), interval -4 hour) < g.game_ts
        """)
        current_week = week_qry.first()
        return render_template("underdog/picks.html", games=games.fetchall(), default=current_week.week_id, league_id=league_id)

    elif request.method == 'POST':
        pick_list = request.form.getlist('pick')
        picks = { i : pick_list[i] for i in range(0, len(pick_list) ) }

        locked_special = db.session.execute("""
            select
              p.game_id,
              case
                when coalesce(s1.spread, s2.spread) is null then 'N/A'
                when coalesce(s1.spread, s2.spread) = 0 then 'EVEN'
                when s1.spread is not null then t1.espn_team_name
                else t2.espn_team_name
              end as underdog
            from ud_picks p
            inner join ud_games g
              on p.game_id = g.game_id
            inner join teams t1
              on g.home_id = t1.atthletics_team_id
            inner join teams t2
              on g.away_id = t2.atthletics_team_id
            left join ud_spreads s1
              on g.game_id = s1.game_id
              and g.home_id = s1.team_id
            left join ud_spreads s2
              on g.game_id = s2.game_id
              and g.away_id = s2.team_id
            where
              p.user_id = :user
              and p.league_id = :league
              and p.is_special = 1
              and p.is_invalid = False
              and date_add(now(), interval -4 hour) >= g.game_ts
        """,
        {'league': league_id, 'user': session['user_id']}).first()

        games = db.session.execute("""
            select
                g.game_id,
                date_format(g.game_ts,"%W, %b. %e, %Y") as game_dt,
                date_format(g.game_ts,"%r") as game_ts,
                g.week_id,
                t1.espn_team_name as home_team,
                g.home_score,
                t2.espn_team_name as away_team,
                g.away_score,
                g.is_final,
                case
                  when coalesce(s1.spread, s2.spread) is null then 'N/A'
                  when coalesce(s1.spread, s2.spread) = 0 then 'EVEN'
                  when s1.spread is not null then t1.espn_team_name
                  else t2.espn_team_name
                end as underdog,
                if(date_add(now(), interval -4 hour) >= g.game_ts,'Y','N') as is_locked,
                if(p.is_special = 1, 'Y','N') as is_special,
                coalesce(s1.spread, s2.spread, 0) as spread
            from ud_games g
            inner join teams t1
              on g.home_id = t1.atthletics_team_id
            inner join teams t2
              on g.away_id = t2.atthletics_team_id
            left join ud_picks p
              on g.game_id = p.game_id
              and p.user_id = :user
              and p.league_id = :league
              and p.is_invalid = False
            left join ud_spreads s1
              on g.game_id = s1.game_id
              and g.home_id = s1.team_id
            left join ud_spreads s2
              on g.game_id = s2.game_id
              and g.away_id = s2.team_id
            where
              g.game_id in (:p1, :p2, :p3, :p4, :p5)
              and date_add(now(), interval -4 hour) < g.game_ts
            order by
              g.game_ts
        """,
        {'league': league_id, 'user': session['user_id'],
            'p1': picks.get(0, 0),
            'p2': picks.get(1, 0),
            'p3': picks.get(2, 0),
            'p4': picks.get(3, 0),
            'p5': picks.get(4, 0)})
        return render_template("underdog/submit_picks.html", picks=games.fetchall(), league_id=league_id, special=locked_special)

@app.route('/submit_picks/<int:league_id>', methods=['POST'])
def submit_picks(league_id):
    # must be signed in
    if 'user_id' not in session:
        return redirect(url_for('signin'))

    week = request.form.getlist('week')[0]
    special = request.form.get('special')
    pick_list = request.form.getlist('pick')
    picks = { i : pick_list[i] for i in range(0, len(pick_list) ) }
    db.session.execute("""
        update ud_picks
          set
            is_invalid = True
        where pick_id in (
            select
              p.pick_id
            from (
                select
                  pick_id,
                  game_id
                from ud_picks
                where
                  user_id = :user
                  and league_id = :league
                  and is_invalid = False
            ) p
            inner join ud_games g
              on p.game_id = g.game_id
            where
              g.week_id = :week
              and date_add(now(), interval -4 hour) < g.game_ts)
    """,{'league': league_id, 'user': session['user_id'], 'week': week,
        'p1': picks.get(0, 0),
        'p2': picks.get(1, 0),
        'p3': picks.get(2, 0),
        'p4': picks.get(3, 0),
        'p5': picks.get(4, 0)})
    db.session.commit()

    db.session.execute("""
        insert into ud_picks
            (league_id, user_id, game_id, is_special)
        values
            (:league, :user, :p1, False),
            (:league, :user, :p2, False),
            (:league, :user, :p3, False),
            (:league, :user, :p4, False),
            (:league, :user, :p5, False)
    """,{'league': league_id, 'user': session['user_id'],
        'p1': picks.get(0, 0),
        'p2': picks.get(1, 0),
        'p3': picks.get(2, 0),
        'p4': picks.get(3, 0),
        'p5': picks.get(4, 0)})
    if int(special) != 0:
        db.session.execute("""
            update ud_picks
                set is_special = True
            where
              game_id = :special
              and user_id = :user
              and league_id = :league
              and is_invalid = False
        """,{'league': league_id, 'user': session['user_id'], 'special': special})
    db.session.commit()

    # league query
    leagues = db.session.execute("""
        select
            l.league_id,
            l.league_name,
            u.email as owner,
            lu.entrant_id
        from leagues_users lu
        inner join leagues l
          on lu.league_id = l.league_id
        inner join users u
          on l.owner_id = u.user_id
        where lu.user_id = :user
    """
    , {'user': int(session['user_id'])})
    return render_template('league.html', leagues=leagues.fetchall())

# -------------- #
# Article Routes #
# -------------- #

@app.route('/article/<string:article>', methods=['GET'])
def show_article(article):
    # article query
    qry = db.session.execute("""
        select
          a.article_id,
          a.article_file,
          a.article_name,
          a.article_desc,
          concat(u.first_name, ' ', u.last_name) as author,
          a.create_ts
        from articles a
        inner join users u
          on a.author_id = u.user_id
        where
            article_file = :article
    """
    , {'article': article})
    if qry.rowcount == 0:
        return render_template("error404.html", message="We lost that article! I know... we dropped the ball! Please take a look at a different article while we work on our hands. Sorry!")
    else:
        with open(os.path.join(APP_STATIC, 'articles/'+article+'.html'), 'r') as f:
            text = f.read()
            article_text = text.format('<p class="sif-subtext">','</p>','<br>')
        return render_template("article.html", article=qry.fetchall(), txt=article_text)


# ------------ #
# Basic Routes #
# ------------ #

#@app.errorhandler(404)
@app.route('/error404')
def error404():
    return render_template("error404.html")

@app.route('/incomplete')
def incomplete():
    return render_template("incomplete.html")

@app.route('/about')
def about():
    return render_template("underdog/about.html")

@app.route('/help')
def help():
    return render_template("help.html")

@app.route('/privacy')
def privacy():
    return render_template("privacy.html")

@app.route('/terms')
def terms():
    return render_template("terms.html")

@app.route('/logout')
def logout():
    session.clear()
    session['logged_in'] = False
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)

def current_week():
    # Determine current week to get set of games to scrape
    now = dt.date.today()
    season_start = dt.date(2017, 8, 26)
    diff = pd.to_datetime(now) - pd.to_datetime(season_start)
    diff = float(diff / np.timedelta64(1, 'W'))
    week = math.ceil(diff)
