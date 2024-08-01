from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    select,
    insert,
    delete,
)
from models.DB import (
    Base,
    connect_and_close,
    lock_and_release,
)
from sqlalchemy.orm import Session


class Bot(Base):
    __tablename__ = "bots"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    on = Column(Boolean, default=0)

    @staticmethod
    @connect_and_close
    def check_active(s: Session = None):
        res = s.execute(select(Bot).where(Bot.on == True))
        try:
            return res.fetchone().t[0]
        except:
            pass

    @staticmethod
    @connect_and_close
    def get_all(s: Session = None):
        res = s.execute(select(Bot))
        try:
            return list(map(lambda x: x[0], res.tuples().all()))
        except:
            pass

    @staticmethod
    @connect_and_close
    def get_one(bot_id: int, s: Session = None):
        res = s.execute(select(Bot).where(Bot.id == bot_id))
        try:
            return res.fetchone().t[0]
        except:
            pass

    @staticmethod
    @lock_and_release
    async def add(
        bot_id: int,
        name: str,
        s: Session = None,
    ):
        s.execute(
            insert(Bot)
            .values(
                id=bot_id,
                name=name,
            )
            .prefix_with("OR IGNORE")
        )

    @staticmethod
    @lock_and_release
    async def remove(bot_id: int, s: Session = None):
        s.execute(delete(Bot).where(Bot.id == bot_id))

    @staticmethod
    @lock_and_release
    async def update(bot_id: int, on: bool = None, name: str = None, s: Session = None):
        values = {}
        if name:
            values[Bot.name] = name
        if on is not None:
            values[Bot.on] = on
        s.query(Bot).filter_by(id=bot_id).update(values)
