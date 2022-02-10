from fastapi import Depends, Request, APIRouter, Response, Cookie
from fastapi.exceptions import HTTPException
from fastapi_utils.cbv import cbv
from app.oauth.callable import AuthRoleCheck
from app.schemas.base import PostSchema, PatchSchema, GetSchema
from app.schemas.user import UserWithRoles
from app.crud.base import BaseCrud
from app.models.base import BaseModel
from typing import List, Union, Optional
from fastapi_utils.inferring_router import InferringRouter

class BaseBuildView:
    get_schema: GetSchema
    post_schema: PostSchema
    patch_schema: PatchSchema
    put_schema: PatchSchema
    available_routes: List[str] = ['get','index','post','patch','put','delete','head','undelete']
    additional_routes: Union[InferringRouter,APIRouter]
    require_auth: bool = False
    required_role: List[str] = []
    role_get: List[str] = []
    role_index: List[str] = []
    role_post: List[str] = []
    role_patch:  List[str] = []
    role_put: List[str] = []
    role_delete: List[str] = []
    role_head: List[str] = []
    role_undelete: List[str] = []
    crud_class: BaseCrud = None
    model: BaseModel = None

    def __init__(self):
        #uses a precomposed crud_class if needed, otherwise generates one for you.
        if not self.crud_class:
            class AutoCrud(BaseCrud):
                model = self.model
            self.crud_class = AutoCrud
        crudclass = self.crud_class
        router = InferringRouter()
        get_schema = self.get_schema
        post_schema = self.post_schema
        get_callable = AuthRoleCheck(role=self.required_role+self.role_get, required=self.require_auth)
        index_callable = AuthRoleCheck(role=self.required_role+self.role_index, required=self.require_auth)
        post_callable = AuthRoleCheck(role=self.required_role+self.role_post, required=self.require_auth)
        patch_callable = AuthRoleCheck(role=self.required_role+self.role_patch, required=self.require_auth)
        put_callable = AuthRoleCheck(role=self.required_role+self.role_patch, required=self.require_auth)
        delete_callable = AuthRoleCheck(role=self.required_role+self.role_delete, required=self.require_auth)
        head_callable = AuthRoleCheck(role=self.required_role+self.role_head, required=self.require_auth)
        undelete_callable = AuthRoleCheck(role=self.required_role+self.role_undelete, required=self.require_auth)
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
                    user: UserWithRoles = Depends(get_callable)
                    ) -> get_schema:
                if 'get' not in self.available_routes:
                    raise HTTPException(405)
                item = crudclass.get(session=self.request.state.db,
                                         id=id)
                schema = get_schema.from_orm(item)
                self.request.state.schema = schema
                self.request.state.db.close()
                return schema

            @router.get("/")
            def index(self,
                      params: dict = Depends(crudclass.query_params),
                      user: UserWithRoles = Depends(index_callable)
                      ) -> List[get_schema]:
                if 'index' not in self.available_routes:
                    raise HTTPException(405)
                items = crudclass.index(session=self.request.state.db,
                                        params=params
                                        )
                try:
                    schema = [get_schema.from_orm(item) for item in items]
                except TypeError:
                    schema = []
                self.request.state.schema = schema
                self.request.state.db.close()
                return schema

            @router.post("/",status_code=201)
            def post(self,
                     item: post_schema,
                user: UserWithRoles = Depends(post_callable),
            )->get_schema:
                if 'post' not in self.available_routes:
                    raise HTTPException(405)
                item = crudclass.post(session=self.request.state.db,
                                      data=item)
                schema = get_schema.from_orm(item)
                self.request.state.schema = schema
                self.request.state.db.close()
                return schema


            @router.patch("/{id}",status_code=202)
            def patch(self,
                      id: int,
                      item: patch_schema,
                      user: UserWithRoles = Depends(patch_callable))->get_schema:
                if 'patch' not in self.available_routes:
                    raise HTTPException(405)
                item = crudclass.update(session=self.request.state.db,
                                        id = id,
                                        data=item)
                schema = get_schema.from_orm(item)
                self.request.state.schema = schema
                self.request.state.db.close()
                return schema

            @router.put("/",status_code=202)
            def put(self,
                    item: put_schema,
                    user: UserWithRoles = Depends(put_callable))->get_schema:
                if 'put' not in self.available_routes:
                    raise HTTPException(405)
                try:
                    id = item.id
                    if not id:
                        raise ValueError('No ID')
                    del item.id
                    item = crudclass.update(session=self.request.state.db,
                                            id = id,
                                            data=item
                                            )
                except:
                    item = crudclass.post(session=self.request.state.db,
                                          data=item)
                schema = get_schema.from_orm(item)
                self.request.state.schema = schema
                self.request.state.db.close()
                return schema

            @router.delete("/{id}",status_code=202)
            def delete(self,
                       id: int,
                       user: UserWithRoles = Depends(delete_callable)
                       )->get_schema:
                if 'delete' not in self.available_routes:
                    raise HTTPException(405)
                item = crudclass.delete(session=self.request.state.db,
                                            id = id)
                schema = get_schema.from_orm(item)
                self.request.state.schema = schema
                self.request.state.db.close()
                return schema

            @router.delete("/undo/{id}",status_code=202)
            def undelete(self,
                         id: int,
                         user: UserWithRoles = Depends(undelete_callable)
                         )->get_schema:
                if 'undelete' not in self.available_routes:
                    raise HTTPException(405)
                item = crudclass.undelete(session=self.request.state.db,
                                          id=id)
                schema = get_schema.from_orm(item)
                self.request.state.schema = schema
                self.request.state.db.close()
                return schema

            @router.head("/")
            def head(self,
                     response: Response,
                     params:dict = Depends(crudclass.query_params),
                     user: UserWithRoles = Depends(head_callable)
                     ):
                if 'head' not in self.available_routes:
                    raise HTTPException(405)
                response.headers['Query-Length']=str(crudclass.head(session=self.request.state.db,
                                                                    params=params
                                                                    )
                                                     )
                self.request.state.db.close()
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

