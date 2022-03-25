import sqlalchemy
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


member_role = sqlalchemy.Table('roleAssociation', SqlAlchemyBase.metadata,
    sqlalchemy.Column('Member_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('Member.id')),
    sqlalchemy.Column('Role_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('Role.id'))
)

member_duel = sqlalchemy.Table('duelAssociation', SqlAlchemyBase.metadata,
    sqlalchemy.Column('Member_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('Member.id')),
    sqlalchemy.Column('Duel_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('Duel.id'))
)


class Member(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'Member'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    nickname = sqlalchemy.Column(sqlalchemy.String)
    coins = sqlalchemy.Column(sqlalchemy.Integer)
    reputation = sqlalchemy.Column(sqlalchemy.Integer)
    duels = relationship('Duel', secondary=member_duel, backref='duels')
    roles = relationship('Role', secondary=member_role, backref='roles')

    def __repr__(self):
        return f'Member<{self.nickname}>'


class Duel(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'Duel'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    duelist_one = sqlalchemy.Column(sqlalchemy.String)
    duelist_two = sqlalchemy.Column(sqlalchemy.String)
    pay = sqlalchemy.Column(sqlalchemy.Integer)
    winner = sqlalchemy.Column(sqlalchemy.String)
    timestamp = sqlalchemy.Column(sqlalchemy.DateTime)

    def __repr__(self):
        return f'Duel<{self.winner}><{self.pay}>'


class Role(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'Role'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String)
    colour = sqlalchemy.Column(sqlalchemy.String)
    owner = sqlalchemy.Column(sqlalchemy.Integer)
    expired_at = sqlalchemy.Column(sqlalchemy.DateTime(timezone=True))

    def __repr__(self):
        return f'Role<{self.name}>'
