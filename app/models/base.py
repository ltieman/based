from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import Column, Integer, DateTime, inspect
from datetime import datetime

class TableBase(object):
    """
    base class for sql alchemy tables
    """
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    # From https://riptutorial.com/sqlalchemy/example/6614/converting-a-query-result-to-dict
    def _asdict(self):
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
    id = Column(Integer, primary_key=True, index=True)
    created = Column(DateTime, default=datetime.now())
    updated = Column(DateTime)
    archived = Column(DateTime)

Base = declarative_base(cls=TableBase)