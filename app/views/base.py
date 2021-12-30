from fastapi import Depends, Request, APIRouter, Response
from fastapi.exceptions import HTTPException
from fastapi_utils.cbv import cbv
from app.schemas.base import PostSchema, PatchSchema, GetSchema
from app.crud.base import BaseCrud
from app.models.base import BaseModel
from typing import List
from fastapi_utils.inferring_router import InferringRouter

class BaseBuildView:
    get_schema: GetSchema
    post_schema: PostSchema
    patch_schema: PatchSchema
    put_schema: PatchSchema
    available_routes: list = ['get','index','post','patch','put','delete','head','undelete']
    component: BaseCrud = None
    model: BaseModel = None

    def __init__(self):
        #uses a precomposed component if needed, otherwise generates one for you.
        if not self.component:
            class AutoCrud(BaseCrud):
                model = self.model
            self.component = AutoCrud
        component = self.component
        router = InferringRouter()
        get_schema = self.get_schema
        post_schema = self.post_schema
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
                    id: int) -> get_schema:
                if 'get' not in self.available_routes:
                    raise HTTPException(405)
                item = component.get(session=self.request.state.db,
                                         id=id)
                schema = get_schema.from_orm(item)
                self.request.state.schema = schema
                return schema

            @router.get("/")
            def index(self,
                      params: dict = Depends(component.query_params)
                      ) -> List[GetSchema]:
                if 'index' not in self.available_routes:
                    raise HTTPException(405)
                items = component.index(session=self.request.state.db,
                                        params=params
                                        )
                schema = [get_schema.from_orm(item) for item in items]
                self.request.state.schema = schema
                return schema

            @router.post("/",status_code=201)
            def post(self,
                     item: post_schema)->get_schema:
                if 'post' not in self.available_routes:
                    raise HTTPException(405)
                item = component.post(session=self.request.state.db,
                                      data=item)
                schema = get_schema.from_orm(item)
                self.request.state.schema = schema
                return schema


            @router.patch("/{id}",status_code=202)
            def patch(self,
                      id: int,
                      item: patch_schema)->get_schema:
                if 'patch' not in self.available_routes:
                    raise HTTPException(405)
                item = component.update(session=self.request.state.db,
                                        id = id,
                                        data=item)
                schema = get_schema.from_orm(item)
                self.request.state.schema = schema
                return schema

            @router.put("/",status_code=202)
            def put(self,
                    item: put_schema)->get_schema:
                if 'put' not in self.available_routes:
                    raise HTTPException(405)
                try:
                    id = item.id
                    del item.id
                    item = component.update(session=self.request.state.db,
                                            id = id,
                                            data=item
                                            )
                except:
                    item = component.post(session=self.request.state.db,
                                          data= item)
                schema = get_schema.from_orm(item)
                self.request.state.schema = schema
                return schema

            @router.delete("/{id}",status_code=202)
            def delete(self,
                       id: int)->get_schema:
                if 'delete' not in self.available_routes:
                    raise HTTPException(405)
                item = component.delete(session=self.request.state.db,
                                            id = id)
                schema = get_schema.from_orm(item)
                self.request.state.schema = schema
                return schema

            @router.delete("/undo/{id}",status_code=202)
            def undelete(self,
                         id: int)->get_schema:
                if 'undelete' not in self.available_routes:
                    raise HTTPException(405)
                item = component.undelete(session=self.request.state.db,
                                          id=id)
                schema = get_schema.from_orm(item)
                self.request.state.schema = schema
                return schema

            @router.head("/")
            def head(self,
                     response: Response,
                     params:dict = Depends(component.query_params),
                     ):
                if 'head' not in self.available_routes:
                    raise HTTPException(405)
                response.headers['Query-Length']=str(component.head(session=self.request.state.db,
                                                                    params=params
                                                                    )
                                                     )
                return {}

        self.router = router
        self.view = BaseView

