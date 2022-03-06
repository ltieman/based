from app.models.base import BaseModel as SQLBaseModel
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session, Query
from fastapi.exceptions import HTTPException
from typing import List, Union
from app.oauth.roles import RoleEnum
from sqlalchemy import update
from app.schemas.base import ArchiveUpdate, HeadSchema
from app.schemas.auth.user import UserWithRoles
from dateutil.parser import parse


class BaseCrud:
    model: SQLBaseModel

    @classmethod
    def apply_query_security(cls, query: Query,
                             user: UserWithRoles = None)->Query:
        if not user:
            return query
        elif RoleEnum.ADMIN.name in user.roles:
            return query
        elif user and hasattr(cls.model, "group_id"):
            query = query.filter(cls.model.group_id.in_(user.authorized_groups))
        elif user and cls.model.__name__.lower() == "group":
            query = query.filter(cls.model.id.in_(user.authorized_groups))
        return query

    @classmethod
    def apply_patch_security(cls,
                             data: BaseModel,
                             id: int,
                             user: UserWithRoles = None):
        if not user:
            ...
        elif RoleEnum.ADMIN.name in user.roles:
            ...
        elif user and hasattr(data, "group_id"):
            try:
                assert data.group_id in user.authorized_groups
            except:
                raise HTTPException("401", "Not Authorized")
        elif hasattr(data.config, "is_group_schema"):
            try:
                assert id in user.authorized_groups
            except:
                raise HTTPException("401", "Not Authorized")

    @classmethod
    def apply_post_security(cls,
                            data: BaseModel,
                            user: UserWithRoles = None):
        if not user:
            ...
        elif user and (hasattr(data, "group_id") or hasattr(cls.model, "group_id")):
            try:
                assert data.group_id in user.authorized_groups
            except:
                raise HTTPException("401", "Not Authorized")

    @classmethod
    def index_params(cls,
                     params: dict,
                     query: Query) -> Query:
        try:
            # if show archived is set to false, return only rows where archived is none
            if not params["show_archived"]:
                query = query.filter(cls.model.archived == None)
        except:
            ...
        try:
            if params["updated_since"]:
                # set query to return only rows created or updated since the date in the params
                query = query.filter(
                    cls.model.created
                    >= params["updated_since"] | cls.model.updated
                    >= params["updated_since"]
                )
        except:
            ...
        # for every query param that matches up with a field name, return rows with the value
        for k, v in params.items():
            if hasattr(cls.model, k) and k not in [
                "offset",
                "limit",
                "show_archived",
                "updated_since",
            ]:
                query = query.filter(getattr(cls.model, k) == v)
        return query

    @classmethod
    def get(cls,
            session: Session,
            id: int,
            query: Query = None,
            user: UserWithRoles = None,
            query_pass_back: bool = False
    ) -> Union[SQLBaseModel,Query]:
        # simple get by id
        if query:
            query = query.filter(cls.model.id == id)
        else:
            query = session.query(cls.model).filter(cls.model.id == id)
        query = cls.apply_query_security(query, user)
        if query_pass_back:
            return query
        item = query.first()
        return item

    @classmethod
    def index(
        cls,
        session: Session,
        params: dict = None,
        query_pass_back: bool = False,
        from_head: bool = False,
        query: Query = None,
        user: UserWithRoles = None,
    ) -> Union[List[SQLBaseModel], Query]:
        if not params:
            params = {}
        # allow for passing in query through super()
        if not query:
            query = session.query(cls.model)
        # this modifies the query based on the query params
        # if we dont want to do this here, don't pass it in from super()
        query = cls.index_params(params=params, query=query)
        query = cls.apply_query_security(query, user)
        # returns the query without executing it for the head method
        if from_head:
            return query
        query = query.offset(params.get("offset", 0)).limit(params.get("limit", 20))
        if query_pass_back:
            return query
        # sets the offset and limit from the params and fetches the query
        return (
            query.all()
        )

    @classmethod
    def post(
        cls,
        session: Session,
        data: BaseModel,
        user: UserWithRoles = None,
        query_pass_back: bool = False
    ) -> SQLBaseModel:
        # very straight forward sql alchemy create row
        cls.apply_post_security(data)
        item = cls.model(**data.dict())
        if query_pass_back:
            return item
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

    @classmethod
    def update(
        cls,
        session,
        id: int,
        data: BaseModel,
        query: Query = None,
        user: UserWithRoles = None,
        query_pass_back: bool = False
    ) -> Union[Query,SQLBaseModel]:
        cls.apply_patch_security(data=data, user=user, id=id)
        up_query = (
            update(cls.model)
            .where(cls.model.id == id)
            .values(**data.dict(exclude_unset=True))
        )
        up_query = cls.apply_query_security(up_query, user)
        if query_pass_back:
            return up_query
        session.execute(up_query)
        session.commit()
        return cls.get(session, id, query=query, user=user)

    @classmethod
    def delete(cls,
               session: Session,
               id: int,
               user: UserWithRoles = None,
               query_pass_back: bool = False
    ) -> Union[Query,SQLBaseModel]:
        # uses the update method to modify the archived field
        return cls.update(
            session=session,
            id=id,
            data=ArchiveUpdate(archived=datetime.utcnow()),
            user=user,
            query_pass_back=query_pass_back
        )

    @classmethod
    def undelete(cls,
                 session: Session,
                 id: int,
                 user: UserWithRoles = None,
                 query: Query = None,
                 query_pass_back: bool = False
    ) -> Union[SQLBaseModel, Query]:
        # uses the update field to nullify the archived field
        return cls.update(
            session=session, id=id, data=ArchiveUpdate(archived=None), user=user,query=query, query_pass_back=query_pass_back
        )

    @classmethod
    def head(
        cls,
        session: Session,
        params: BaseModel,
        query: Query = None,
        user: UserWithRoles = None,
        query_pass_back: bool = False
    ) -> Union[Query,HeadSchema]:
        # get back the exact query that we would get from the index method

        query = cls.index(
            session=session, params=params, from_head = True, query=query, user=user
        )
        if query_pass_back:
            return query
        # get the count of the rows on the dataset
        return query.count()
        # give it back along with the params we were given

    @staticmethod
    def query_params(
        limit: int = 20,
        offset: int = 0,
        show_archived: bool = False,
        updated_since: datetime = None,
    ):
        # this code takes the parameters specified above for use as query parameters and returns them as a dictionary
        # as well as doing a little bit of parsing
        return BaseCrud.__query_params__(**locals())

    @staticmethod
    def __query_params__(**kwargs):
        if kwargs["updated_since"]:
            kwargs["updated_since"] = parse(kwargs["updated_since"])
        return {k: v for k, v in kwargs.items() if v is not None}
