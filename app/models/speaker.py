from sqlalchemy import Column, BIGINT, String
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.talk import Talk


class Speaker(Base):
    __tablename__ = 'speakers'
    facebook_id = Column(BIGINT, primary_key=True)
    name = Column(String(128), nullable=False)

    talks = relationship('Talk', backref='speaker', lazy='dynamic')

    def __repr__(self):
        return '<Speaker %r>' % self.facebook_id
