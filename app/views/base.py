from fastapi import Depends, Request, APIRouter
from fastapi.exceptions import HTTPException
from fastapi_utils.cbv import cbv
from app.schemas.base import Webargs, PostSchema, PatchSchema, GetSchema, HeadSchema
from app.components.base import CrudComponent
from typing import List
from fastapi_utils.inferring_router import InferringRouter

class BuildView:
    component: CrudComponent
    #webargs: Webargs

    #get_schema: GetSchema
    available_routes: list = ['get','index','post','patch','put','delete','head','undelete']
    def __init__(self):
    #    Webargs = self.webargs
        component = self.component
        router = InferringRouter()  # Step 1: Create a router

        @cbv(router)
        class BaseView(object):
            request: Request
            available_routes = self.available_routes
            @router.get("/{id}")
            def get(self,
                    id: int) -> GetSchema:
                if 'get' not in self.available_routes:
                    raise HTTPException(405)
                item = component.get(session=self.request.state.db,
                                         id=id)
                return self.get_schema.from_orm(item)

            @router.get("/")
            def index(self,
                      #params:Webargs = Webargs
                      ) -> List[GetSchema]:
                if 'index' not in self.available_routes:
                    raise HTTPException(405)
                items = component.index(session=self.request.state.db,
                                        #    params=params
                                        )
                return [self.get_schema.from_orm(item) for item in items]

            @router.post("/")
            def post(self,
                     item: PostSchema)->GetSchema:
                if 'post' not in self.available_routes:
                    raise HTTPException(405)
                item = component.post(session=self.request.state.db,
                                          data=item)
                return self.get_schema.from_orm(item)

            @router.patch("/{id}")
            def patch(self,
                      id: int,
                      item: PatchSchema)->GetSchema:
                if 'patch' not in self.available_routes:
                    raise HTTPException(405)
                item = component.update(session=self.request.state.db,
                                            id = id,
                                            data=item)
                return self.get_schema.from_orm(item)

            @router.put("/{id}")
            def put(self, id: int,
                    item: PostSchema)->GetSchema:
                if 'put' not in self.available_routes:
                    raise HTTPException(405)
                pass

            @router.delete("/{id}")
            def delete(self,
                       id: int)->GetSchema:
                if 'delete' not in self.available_routes:
                    raise HTTPException(405)
                item = component.delete(session=self.request.state.db,
                                            id = id)
                return self.get_schema.from_orm(item)

            @router.delete("/undo/{id}")
            def undelete(self,
                         id: int)->GetSchema:
                if 'undelete' not in self.available_routes:
                    raise HTTPException(405)
                pass

            @router.head("/")
            def head(self,
                     #params:Webargs = Webargs
                     )->HeadSchema:
                if 'head' not in self.available_routes:
                    raise HTTPException(405)
                pass
        self.router = router
        self.view = BaseView
