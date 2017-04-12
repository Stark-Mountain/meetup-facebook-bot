from app import database


class Talk(database.Model):
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    title = database.Column(database.String(128), unique=True, nullable=False)
    description = database.Column(database.String(512))
    speaker_facebook_id = database.Column(database.BIGINT, database.ForeignKey('speaker.facebook_id'),
                                          nullable=False)

    likes = database.relationship('Liker_Talk', backref='talk', lazy='dynamic')

    def __repr__(self):
        return '<Talk %r>' % self.id


class Speaker(database.Model):
    facebook_id = database.Column(database.BIGINT, primary_key=True)
    name = database.Column(database.String(128), nullable=False)

    talks = database.relationship('Talk', backref='speaker', lazy='dynamic')

    def __repr__(self):
        return '<Speaker %r>' % self.facebook_id


class Liker_Talk(database.Model):
    liker_facebook_id = database.Column(database.BIGINT, primary_key=True)
    talk_id = database.Column(database.Integer, database.ForeignKey('talk.id'), primary_key=True)

    def __repr__(self):
        liker = repr(self.liker_facebook_id)
        talk = repr(self.talk_id)
        return '<Liker_Talk %r>' % ', '.join((liker, talk))
