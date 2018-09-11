from sqlalchemy import Column, String, Integer, Float, Date, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError


from .config import DBsession

Base = DBsession.base()

class Script(Base):
    __tablename__ = 'scripts'

    id = Column(String, primary_key=True)
    unbabel_id = Column(String, default='')
    status = Column(String, CheckConstraint('char_length(status)>0'), nullable=False)
    content = Column(String, CheckConstraint('char_length(content)>0'), nullable=False)
    translated = Column(String)

    @staticmethod
    def create(sid, status, content, unbabel_id=''):
        try:
            script = Script(
                    id=str(sid),
                    status=status,
                    unbabel_id=unbabel_id,
                    content=content)
            DBsession.session().add(script)
            DBsession.session().commit()
            return script
        except:
            DBsession.session().rollback()
            raise

    @staticmethod
    def set_translated(translated_content):
        try:
            for uid, translated in translated_content:
                script = Script.get_by_uid(uid)
                script.status = 'translated'
                script.translated = translated
            DBsession.session().commit()
        except:
            DBsession.session().rollback()
            raise

    @staticmethod
    def get(sid):
        return DBsession.session().query(Script).get(sid)

    @staticmethod
    def get_by_uid(uid):
        return DBsession.session().query(Script).filter(Script.unbabel_id == uid).one()

    @staticmethod
    def get_many(ids):
        scripts = [DBsession.session().query(Script).get(sid) for sid in ids]
        return filter(lambda s: s is not None, scripts)

    @staticmethod
    def get_by_status(status):
        return DBsession.session().query(Script).filter(Script.status == status).all()

    @staticmethod
    def get_all():
        return DBsession.session().query(Script).all()

    def set_ext_id(self, ext_id):
        try:
            self.unbabel_id = ext_id
            DBsession.session().commit()
        except:
            DBsession.session().rollback()
            raise

    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'content': self.content,
            'translated': self.translated
        }
