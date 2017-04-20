from sqlalchemy import Column, BIGINT, Integer, ForeignKey

from app.models.base import Base


class Like(Base):
    __tablename__ = 'likes'
    user_facebook_id = Column(BIGINT, primary_key=True)
    talk_id = Column(Integer, ForeignKey('talks.id'), primary_key=True)

    def __repr__(self):
        return '<Like %r, %r>' % (self.user_facebook_id, self.talk_id)
