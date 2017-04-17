from app import database


class Talk(database.Model):

    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    title = database.Column(database.String(128), unique=True, nullable=False)
    description = database.Column(database.String(512))
    speaker_facebook_id = database.Column(database.BIGINT,
                                          database.ForeignKey('speaker.facebook_id'),
                                          nullable=False)

    likes = database.relationship('Liker_Talk', backref='talk', lazy='dynamic')

    def __repr__(self):
        talk_id = repr(self.id)
        title = repr(self.title)
        description = repr(self.description)
        speaker_facebook_id = repr(self.speaker_facebook_id)
        raw_repr = '<Talk id={talk_id}, title={title}, description={description}, '\
                   'speaker_facebook_id={speaker_facebook_id}>'
        formatted_repr = raw_repr.format(talk_id=talk_id, title=title, description=description,
                                         speaker_facebook_id=speaker_facebook_id)
        return formatted_repr


class Speaker(database.Model):

    facebook_id = database.Column(database.BIGINT, primary_key=True)
    name = database.Column(database.String(128), nullable=False)

    talks = database.relationship('Talk', backref='speaker', lazy='dynamic')

    def __repr__(self):
        facebook_id = repr(self.facebook_id)
        name = repr(self.name)
        raw_repr = '<Speaker facebook_id={facebook_id}, name={name}>'
        formatted_repr = raw_repr.format(facebook_id=facebook_id, name=name)
        return formatted_repr


class Liker_Talk(database.Model):
    liker_facebook_id = database.Column(database.BIGINT, primary_key=True)
    talk_id = database.Column(database.Integer, database.ForeignKey('talk.id'),
                              primary_key=True)

    def __repr__(self):
        liker = repr(self.liker_facebook_id)
        talk = repr(self.talk_id)
        raw_repr = '<Liker_Talk liker_facebook_id={liker}, talk_id={talk}>' 
        formatted_repr = raw_repr.format(liker=liker, talk=talk)
        return formatted_repr
