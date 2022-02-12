from fastapi import Depends, Request, APIRouter, Response, Cookie
from fastapi.exceptions import HTTPException
from fastapi_utils.cbv import cbv
from enum import Enum
from app.oauth.callable import AuthRoleCheck
from sqlalchemy.orm import Session
from app.schemas.base import PostSchema, PatchSchema, GetSchema
from app.schemas.user import UserWithRoles
from app.crud.base import BaseCrud
from app.models.base import BaseModel
from typing import List, Union, Optional
from fastapi_utils.inferring_router import InferringRouter
from app.db import get_db

class BaseBuildView:
    get_schema: GetSchema
    post_schema: PostSchema
    patch_schema: PatchSchema
    put_schema: PatchSchema
    available_routes: List[str] = ['get','index','post','patch','put','delete','head','undelete']
    additional_routes: Union[InferringRouter,APIRouter] = []
    auth_callable: AuthRoleCheck = AuthRoleCheck
    require_auth: bool = False
    required_role: List[Enum] = []
    role_get: List[Enum] = []
    role_index: List[Enum] = []
    role_post: List[Enum] = []
    role_patch:  List[Enum] = []
    role_put: List[Enum] = []
    role_delete: List[Enum] = []
    role_head: List[Enum] = []
    role_undelete: List[Enum] = []
    crud_class: BaseCrud = None
    model: BaseModel = None

    def __init__(self):
        #uses a precomposed crud_class if needed, otherwise generates one for you.
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
        get_callable = self.auth_callable(role=self.required_role+self.role_get, required=self.require_auth, model=self.model)
        index_callable = self.auth_callable(role=self.required_role+self.role_index, required=self.require_auth, model=self.model)
        post_callable = self.auth_callable(role=self.required_role+self.role_post, required=self.require_auth, model=self.model)
        patch_callable = self.auth_callable(role=self.required_role+self.role_patch, required=self.require_auth, model=self.model)
        put_callable = self.auth_callable(role=self.required_role+self.role_patch, required=self.require_auth, model=self.model)
        delete_callable = self.auth_callable(role=self.required_role+self.role_delete, required=self.require_auth, model=self.model)
        head_callable = self.auth_callable(role=self.required_role+self.role_head, required=self.require_auth, model=self.model)
        undelete_callable = self.auth_callable(role=self.required_role+self.role_undelete, required=self.require_auth, model=self.model)
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

        @cbv(router)
        class BaseView(object):
            request: Request
            available_routes = self.available_routes

            @router.get("/{id}")
            def get(self,
                    id: int,
                    user: UserWithRoles = Depends(get_callable),
                    session: Session = Depends(get_db)
                    ) -> get_schema:
                if 'get' not in self.available_routes:
                    raise HTTPException(405)
                item = crudclass.get(session=session,
                                         id=id)
                schema = get_schema.from_orm(item)
                self.request.state.schema = schema
                session.close()
                return schema

            @router.get("/")
            def index(self,
                      params: dict = Depends(crudclass.query_params),
                      user: UserWithRoles = Depends(index_callable),
                      session: Session = Depends(get_db)
                      ) -> List[get_schema]:
                if 'index' not in self.available_routes:
                    raise HTTPException(405)
                items = crudclass.index(session=session,
                                        params=params
                                        )
                try:
                    schema = [get_schema.from_orm(item) for item in items]
                except TypeError:
                    schema = []
                self.request.state.schema = schema
                session.close()
                return schema

            @router.post("/",status_code=201)
            def post(self,
                     item: post_schema,
                     user: UserWithRoles = Depends(post_callable),
                     session: Session = Depends(get_db)
            )->get_schema:
                if 'post' not in self.available_routes:
                    raise HTTPException(405)
                item = crudclass.post(session=session,
                                      data=item)
                schema = get_schema.from_orm(item)
                self.request.state.schema = schema
                session.close()
                return schema


            @router.patch("/{id}",status_code=202)
            def patch(self,
                      id: int,
                      item: patch_schema,
                      user: UserWithRoles = Depends(patch_callable),
                      session: Session = Depends(get_db)
                      )->get_schema:
                if 'patch' not in self.available_routes:
                    raise HTTPException(405)
                item = crudclass.update(session=session,
                                        id = id,
                                        data=item)
                schema = get_schema.from_orm(item)
                self.request.state.schema = schema
                session.close()
                return schema

            @router.put("/",status_code=202)
            def put(self,
                    item: put_schema,
                    user: UserWithRoles = Depends(put_callable),
                    session: Session = Depends(get_db)
                    )->get_schema:
                if 'put' not in self.available_routes:
                    raise HTTPException(405)
                try:
                    id = item.id
                    if not id:
                        raise ValueError('No ID')
                    del item.id
                    item = crudclass.update(session=session,
                                            id = id,
                                            data=item
                                            )
                except:
                    item = crudclass.post(session=session,
                                          data=item)
                schema = get_schema.from_orm(item)
                self.request.state.schema = schema
                session.close()
                return schema

            @router.delete("/{id}",status_code=202)
            def delete(self,
                       id: int,
                       user: UserWithRoles = Depends(delete_callable),
                       session: Session = Depends(get_db)
                       )->get_schema:
                if 'delete' not in self.available_routes:
                    raise HTTPException(405)
                item = crudclass.delete(session=session,
                                            id = id)
                schema = get_schema.from_orm(item)
                self.request.state.schema = schema
                session.close()
                return schema

            @router.delete("/undo/{id}",status_code=202)
            def undelete(self,
                         id: int,
                         user: UserWithRoles = Depends(undelete_callable),
                         session: Session = Depends(get_db)
                         )->get_schema:
                if 'undelete' not in self.available_routes:
                    raise HTTPException(405)
                item = crudclass.undelete(session=session,
                                          id=id)
                schema = get_schema.from_orm(item)
                self.request.state.schema = schema
                session.close()
                return schema

            @router.head("/")
            def head(self,
                     response: Response,
                     params:dict = Depends(crudclass.query_params),
                     user: UserWithRoles = Depends(head_callable),
                     session: Session = Depends(get_db)
                     ):
                if 'head' not in self.available_routes:
                    raise HTTPException(405)
                response.headers['Query-Length']=str(crudclass.head(session=session,
                                                                    params=params
                                                                    )
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

