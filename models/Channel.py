from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    select,
    insert,
    delete,
    and_,
)
from models.DB import (
    Base,
    connect_and_close,
    lock_and_release,
)
from sqlalchemy.orm import Session


class Channel(Base):
    __tablename__ = "channels"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    username = Column(String)
    net = Column(String)
    for_rep = Column(Boolean)
    for_on = Column(Boolean, default=1)

    @staticmethod
    @connect_and_close
    def get_all(for_on: bool = None, for_rep: bool = None, s: Session = None):
        if for_on or for_rep:
            if for_on and for_rep:
                where_clause = and_(Channel.for_rep == for_rep, Channel.for_on == for_on)
            elif for_rep:
                where_clause = Channel.for_rep == for_rep
            else:
                where_clause = Channel.for_on == for_on
            res = s.execute(select(Channel).where(where_clause))
        else:
            res = s.execute(select(Channel))
        try:
            return list(map(lambda x: x[0], res.tuples().all()))
        except:
            pass

    @staticmethod
    @connect_and_close
    def get_one(ch_id: int, s: Session = None):
        res = s.execute(select(Channel).where(Channel.id == ch_id))
        try:
            return res.fetchone().t[0]
        except:
            pass

    @staticmethod
    @lock_and_release
    async def add(
        channel_id: int,
        name: str,
        username: str,
        net: str,
        for_rep: bool,
        s: Session = None,
    ):
        s.execute(
            insert(Channel)
            .values(
                id=channel_id,
                name=name,
                username=username,
                net=net,
                for_rep=for_rep,
            )
            .prefix_with("OR IGNORE")
        )

    @staticmethod
    @lock_and_release
    async def remove(channel_id: int, s: Session = None):
        s.execute(delete(Channel).where(Channel.id == channel_id))

    @staticmethod
    @lock_and_release
    async def update(
        ch_id: int,
        net: str = None,
        for_rep: bool = None,
        for_on: bool = None,
        s: Session = None,
    ):
        values = {}
        if net:
            values[Channel.net] = net
        if for_rep is not None:
            values[Channel.for_rep] = for_rep
        if for_on is not None:
            values[Channel.for_on] = for_on
        s.query(Channel).filter_by(id=ch_id).update(values)
