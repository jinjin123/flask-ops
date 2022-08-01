from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class User(Base):
	__tablename__ = 'Users'
	id = Column(Integer, primary_key=True)
	nickname = Column(String(256), unique=True)
	password = Column(String(256), unique=True)
	role = Column(Integer)
	email = Column(String(256), unique=True)
	lastlogin = Column(String(256), unique=True)

	def is_authenticated(self):
		return True

	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return unicode(self.id)

	def __repr__(self):
		return '<User %r>' % (self.nickname)