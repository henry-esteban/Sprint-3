from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, send_file
)

from app.auth import login_required
from app.db import get_db

bp = Blueprint('inbox', __name__, url_prefix='/inbox')

@bp.route("/getDB")
@login_required
def getDB():
    return send_file(current_app.config['DATABASE'], as_attachment=True)


@bp.route('/show')
@login_required
def show():
    db = get_db()
    messages = db.execute(
        'SELECT * FROM message WHERE to_id = ?', (g.user['id'],)
    ).fetchall()

    return render_template('inbox/show.html', messages=messages)


@bp.route('/send', methods=('GET', 'POST'))
@login_required
def send():
    if request.method == 'POST':        
        from_id = g.user['id']
        print(from_id)
        to_username = request.form['to']
        subject = request.form['subject']
        body = request.form['body']

        db = get_db()
       
        if not to_username:
            flash('To field is required')
            return render_template('inbox/send.html')
        
        if not subject:
            flash('Subject field is required')
            return render_template('inbox/send.html')
        
        if not body:
            flash('Body field is required')
            return render_template('inbox/send.html')    
        
        error = None    
        userto = None 
        
        userto = db.execute(
            'SELECT id FROM user WHERE username = ?', (to_username,)
        ).fetchone()

        from_user = db.execute(
            'SELECT username FROM user WHERE id = ?', (from_id,)
        ).fetchone()
        
        if userto is None:
            error = 'Recipient does not exist'
        print(userto)
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO message (from_id, to_id, from_user, subject, body) VALUES (?, ?, ?, ?, ?)',
                (g.user['id'], userto['id'], from_user['username'], subject, body)
            )
            db.commit()

            return redirect(url_for('inbox.show'))

    return render_template('inbox/send.html')