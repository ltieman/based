from fastapi import Depends, Request, APIRouter, Response
from fastapi_utils.cbv import cbv
from app.oauth.roles import RoleEnum
from app.oauth.callable import AuthRoleCheck
from sqlalchemy.orm import Session
from app.schemas.base import PostSchema, PatchSchema, GetSchema
from app.schemas.auth.user import UserWithRoles
from app.crud.base import BaseCrud
from app.models.base import BaseModel
from typing import List, Union
from fastapi_utils.inferring_router import InferringRouter
from app.db import get_db
from .enums import Routes


class BaseBuildView:
    get_schema: GetSchema
    post_schema: PostSchema
    patch_schema: PatchSchema
    put_schema: PatchSchema
    index_schema: GetSchema
    available_routes: List[Routes] = [

        Routes.get,
        Routes.index,
        Routes.post,
        Routes.patch,
        Routes.put,
        Routes.delete,
        Routes.head,
        Routes.undelete,

    ]
    additional_routes: Union[InferringRouter, APIRouter] = []
    auth_callable: AuthRoleCheck = AuthRoleCheck
    require_auth: bool = False
    required_role: RoleEnum = RoleEnum.OPEN
    role_get: RoleEnum = None
    role_index: RoleEnum = None
    role_post: RoleEnum = None
    role_patch: RoleEnum = None
    role_put: RoleEnum = None
    role_delete: RoleEnum = None
    role_head: RoleEnum = None
    role_undelete: RoleEnum = None
    crud_class: BaseCrud = None
    model: BaseModel = None

    def __init__(self):
        # uses a precomposed crud_class if needed, otherwise generates one for you.
        if not self.crud_class:

            class AutoCrud(BaseCrud):
                model = self.model

            self.crud_class = AutoCrud
        else:
            self.model = self.crud_class.model
        crudclass = self.crud_class
        router = InferringRouter()
        get_schema = self.get_schema
        post_schema = self.post_schema
        get_callable = self.auth_callable(
            role=self.role_get if self.role_get else self.required_role,
            required=self.require_auth,
            model=self.model,
        )
        index_callable = self.auth_callable(
            role=self.role_index if self.role_index else self.required_role,
            required=self.require_auth,
            model=self.model,
        )
        post_callable = self.auth_callable(
            role=self.role_post if self.role_post else self.required_role,
            required=self.require_auth,
            model=self.model,
        )
        patch_callable = self.auth_callable(
            role=self.role_patch if self.role_patch else self.required_role,
            required=self.require_auth,
            model=self.model,
        )
        put_callable = self.auth_callable(
            role=self.role_patch if self.role_patch else self.required_role,
            required=self.require_auth,
            model=self.model,
        )
        delete_callable = self.auth_callable(
            role=self.role_delete if self.role_delete else self.required_role,
            required=self.require_auth,
            model=self.model,
        )
        head_callable = self.auth_callable(
            role=self.role_head if self.role_head else self.required_role,
            required=self.require_auth,
            model=self.model,
        )
        undelete_callable = self.auth_callable(
            role=self.role_undelete if self.role_undelete else self.required_role,
            required=self.require_auth,
            model=self.model,
        )
        try:
            patch_schema = self.patch_schema
        except:
            self.patch_schema = self.post_schema
            patch_schema = self.patch_schema
        try:
            put_schema = self.put_schema
        except:
            self.put_schema = self.patch_schema
            put_schema = self.put_schema
        try:
            index_schema = self.index_schema
        except:
            self.index_schema = self.get_schema
            index_schema = self.index_schema

        @cbv(router)
        class BaseView(object):
            request: Request
            available_routes = self.available_routes

            if Routes.get in self.available_routes:

                @router.get("/{id}")
                def get(
                    self,
                    id: int,
                    user: UserWithRoles = Depends(get_callable),
                    session: Session = Depends(get_db),
                ) -> get_schema:

                    item = crudclass.get(session=session, id=id, user=user)
                    schema = get_schema.from_orm(item)
                    self.request.state.schema = schema
                    session.close()
                    return schema

            if Routes.index in self.available_routes:

                @router.get("/")
                def index(
                    self,
                    params: dict = Depends(crudclass.query_params),
                    user: UserWithRoles = Depends(index_callable),
                    session: Session = Depends(get_db),
                ) -> List[index_schema]:
                    items = crudclass.index(session=session, params=params, user=user)
                    try:
                        schema = [index_schema.from_orm(item) for item in items]
                    except TypeError:
                        schema = []
                    self.request.state.schema = schema
                    session.close()
                    return schema

            if Routes.post in self.available_routes:

                @router.post("/", status_code=201)
                def post(
                    self,
                    item: post_schema,
                    user: UserWithRoles = Depends(post_callable),
                    session: Session = Depends(get_db),
                ) -> get_schema:
                    item = crudclass.post(session=session, data=item, user=user)
                    schema = get_schema.from_orm(item)
                    self.request.state.schema = schema
                    session.close()
                    return schema

            if Routes.patch in self.available_routes:

                @router.patch("/{id}", status_code=202)
                def patch(
                    self,
                    id: int,
                    item: patch_schema,
                    user: UserWithRoles = Depends(patch_callable),
                    session: Session = Depends(get_db),
                ) -> get_schema:
                    item = crudclass.update(
                        session=session, id=id, data=item, user=user
                    )
                    schema = get_schema.from_orm(item)
                    self.request.state.schema = schema
                    session.close()
                    return schema

            if Routes.put in self.available_routes:

                @router.put("/", status_code=202)
                def put(
                    self,
                    item: put_schema,
                    user: UserWithRoles = Depends(put_callable),
                    session: Session = Depends(get_db),
                ) -> get_schema:
                    try:
                        id = item.id
                        if not id:
                            raise ValueError("No ID")
                        del item.id
                        item = crudclass.update(
                            session=session, id=id, data=item, user=user
                        )
                    except:
                        item = crudclass.post(session=session, data=item, user=user)
                    schema = get_schema.from_orm(item)
                    self.request.state.schema = schema
                    session.close()
                    return schema

            if Routes.delete in self.available_routes:

                @router.delete("/{id}", status_code=202)
                def delete(
                    self,
                    id: int,
                    user: UserWithRoles = Depends(delete_callable),
                    session: Session = Depends(get_db),
                ) -> get_schema:
                    item = crudclass.delete(session=session, id=id, user=user)
                    schema = get_schema.from_orm(item)
                    self.request.state.schema = schema
                    session.close()
                    return schema

            if Routes.undelete in self.available_routes:

                @router.delete("/undo/{id}", status_code=202)
                def undelete(
                    self,
                    id: int,
                    user: UserWithRoles = Depends(undelete_callable),
                    session: Session = Depends(get_db),
                ) -> get_schema:
                    item = crudclass.undelete(session=session, id=id, user=user)
                    schema = get_schema.from_orm(item)
                    self.request.state.schema = schema
                    session.close()
                    return schema

            if Routes.head in self.available_routes:

                @router.head("/")
                def head(
                    self,
                    response: Response,
                    params: dict = Depends(crudclass.query_params),
                    user: UserWithRoles = Depends(head_callable),
                    session: Session = Depends(get_db),
                ):
                    response.headers["Query-Length"] = str(
                        crudclass.head(session=session, params=params, user=user)
                    )
                    session.close()
                    return {}

        # if we need to add additional routes beyond the core crud api
        # then we need to add the router for the core crud api to those endpoints router
        # as APIRouters have problems running inside of Infering Routers
        if self.additional_routes:
            self.additional_routes.include_router(router)
            self.router = self.additional_routes
        else:
            self.router = router
        self.view = BaseView

def view_base(obj:BaseBuildView)->BaseBuildView:

    return obj()
