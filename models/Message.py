from sqlalchemy import (
    Column,
    Integer,
    select,
    insert,
    and_,
)
from models.DB import (
    Base,
    connect_and_close,
    lock_and_release,
)
from sqlalchemy.orm import Session


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    from_message_id = Column(Integer)
    to_message_id = Column(Integer)
    from_channel_id = Column(Integer)
    to_channel_id = Column(Integer)

    @staticmethod
    @lock_and_release
    async def add(
        from_message_id: int,
        to_message_id: int,
        from_channel_id: int,
        to_channel_id: int,
        s: Session = None,
    ):
        s.execute(
            insert(Message).values(
                from_message_id=from_message_id,
                to_message_id=to_message_id,
                from_channel_id=from_channel_id,
                to_channel_id=to_channel_id,
            )
        )

    @staticmethod
    @connect_and_close
    def get_one(
        from_message_id: int,
        from_channel_id: int,
        to_channel_id: int,
        s: Session = None,
    ):
        res = s.execute(
            select(Message).where(
                and_(
                    Message.from_message_id == from_message_id,
                    Message.from_channel_id == from_channel_id,
                    Message.to_channel_id == to_channel_id,
                )
            )
        )
        try:
            return res.fetchone().t[0]
        except:
            pass