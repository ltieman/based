from .base import BaseBuildView
from app.config import Config
from fastapi_utils.cbv import cbv
from fastapi.responses import RedirectResponse
from app.crud import UserCrud
from app.schemas.user import UserGetSchema, UserLoginPostSchema, UserPatchSchema, UserCreatePostSchema

router = None



login = """@router.post("/login/")
            def login(self,
                data: UserLoginPostSchema)->UserGetSchema:
                item = crud_class.login(data)
                item = UserGetSchema.from_orm(item)
                return item
        """

login_redirect = f"""@router.get("/login")
                    def login_redirect(self):
                        return RedirectResponse(
                        https://{Config.COGNITO_DOMAIN}/login?response_type=token&client_id={Config.COGNITO_CLIENTID}&redirect_uri={Config.CLEAN_URL}/oauth2/idpresponse      
                """

login_idpresponse = f"""@router.get("/oauth2/idpresponse")
                        def login_idpresponse(self):
                            pass
"""



class UserView(BaseBuildView):
    crud_class = UserCrud
    get_schema = UserGetSchema
    post_schema = UserCreatePostSchema
    patch_schema = UserPatchSchema
    added_methods = [login, login_redirect]