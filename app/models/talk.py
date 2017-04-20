from sqlalchemy import Column, Integer, String, BIGINT, ForeignKey
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.like import Like


class Talk(Base):
    __tablename__ = 'talks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(128), unique=True, nullable=False)
    description = Column(String(512))
    speaker_facebook_id = Column(
        BIGINT,
        ForeignKey('speakers.facebook_id'),
        nullable=False
    )

    likes = relationship('Like', backref='talk', lazy='dynamic')

    def is_liked_by(self, user_id, db_session):
        like = db_session.query(Like).filter_by(
            user_facebook_id=user_id,
            talk_id=self.id
        )
        return db_session.query(like.exists()).one()

    def count_likes(self, db_session):
        return db_session.query(Like).filter_by(talk_id=self.id).count()

    def set_like(self, user_id, db_session):
        if self.is_liked_by(user_id):
            raise ValueError('The like has already been set.')
        like = Like(user_facebook_id=user_id, talk=self)
        db_session.add(like)
        db_session.commit()

    def unset_like(self, user_id, db_session):
        if not self.is_liked_by(user_id):
            raise ValueError('The like has not been set.')
        like = db_session.query(Like).filter_by(
            user_facebook_id=user_id,
            talk_id=self.id
        ).one()
        db_session.delete(like)
        db_session.commit()

    def revert_like(self, user_id, db_session):
        if self.is_liked_by(user_id):
            self.unset_like(user_id)
        else:
            self.set_like(user_id)

    def __repr__(self):
        return '<Talk %r>' % self.id
