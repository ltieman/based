from fastapi import Depends, Request
from fastapi_utils.cbv import cbv
from ..schemas.base import Webargs, PostSchema, PatchSchema, GetSchema, HeadSchema
from ..components.base import CrudComponent
from typing import List
from fastapi_utils.inferring_router import InferringRouter
router = InferringRouter()  # Step 1: Create a router


class BaseView(object):
    request: Request
    component: CrudComponent


class GetView(BaseView):
    @router.get("/{id}")
    def get(self,
            id: int) -> GetSchema:
        item = self.component.get(session=self.request.state.db,
                                 id=id)
        return self.component.get_schema.from_orm(item)


class IndexView(BaseView):
    @router.get("/")
    def index(self,
              params:Webargs = Webargs) -> List[GetSchema]:
        items = self.component.index(session=self.request.state.db,
                                    params=params)
        return [self.component.get_schema.from_orm(item) for item in items]


class PostView(BaseView):
    @router.post("/")
    def post(self,
             item: PostSchema = PostSchema)->GetSchema:
        item = self.component.post(session=self.request.state.db,
                                  data=item)
        return self.component.get_schema.from_orm(item)


class PatchView(BaseView):
    @router.patch("/{id}")
    def patch(self,
              id: int,
              item: PatchSchema = PatchSchema)->GetSchema:
        item = self.component.update(session=self.request.state.db,
                                    id = id,
                                    data=item)
        return self.component.get_schema.from_orm(item)


class PutView(BaseView):
    @router.put("/{id}")
    def put(self, id: int,
            item: PostSchema = PostSchema)->GetSchema:
        pass


class DeleteView(BaseView):
    @router.delete("/{id}")
    def delete(self,
               id: int)->GetSchema:
        item = self.component.delete(session=self.request.state.db,
                                    id = id)
        return self.component.get_schema.from_orm(item)


class UnDeleteView(BaseView):
    @router.delete("/undo/{id}")
    def undelete(self,
                 id: int)->GetSchema:
        pass


class HeadView(BaseView):
    @router.head("/")
    def head(self,
             params:Webargs = Webargs)->HeadSchema:
        pass

