from app.crud.auth.base import AuthCrud
from app.schemas.auth.user import UserLoginPostSchema
from fastapi.responses import Response
import pytest
import secrets

@pytest.fixture
def login_token(user_login):
    user_password = UserLoginPostSchema(username = 'lucas', password = user_login.COGNITO_PASSWORD)
    return AuthCrud.user_login(user_password=user_password)

@pytest.fixture
def login_code():
    return secrets.token_urlsafe(32)

@pytest.fixture
def login_blank_response():
    return Response()

@pytest.fixture
def login_with_code_and_token(session, login_token, login_code, login_blank_response):
    AuthCrud.auth_callback(code=login_code, token=login_token, response=login_blank_response, session=session)
    return login_blank_response

def test_login(login_with_code_and_token, login_code, user_login):
    assert f"AUTH-TOKEN={login_code}" in login_with_code_and_token.headers['set-cookie']

@pytest.fixture
def login_response(test_client, user_login):
    response = test_client.post(url="/users/login",json={"username":'lucas',"password":user_login.COGNITO_PASSWORD})
    assert response.status_code == 200
    return response

def test_login_response(login_response):
    assert login_response.json()['id']
    assert login_response.json()['created']
    assert login_response.json()['first_name']
    assert login_response.json()['last_name']
    assert login_response.json()['username']
    assert login_response.json()['sub']
    assert login_response.json()['email']
    assert login_response.cookies['AUTH-TOKEN']


def test_add_group():
    ...

def test_add_user_to_group():
    ...

def test_remove_user_from_group():
    ...

def test_change_user_permission_in_group():
    ...

def test_group_post():
    ...

def test_code_token_post():
    ...

def test_code_token_get():
    ...

def test_code_token_index():
    ...

def mock_get_token_from_code():
    ...

def mock_get_user_from_token():
    ...

def test_user_formater():
    ...

def test_auth_callback():
    ...

def test_auth_callback_token_fail():
    ...

def test_auth_callback_no_roles():
    ...

def test_validate_code():
    ...

def test_validate_code_fail():
    ...

def test_validate_code_group_roles():
    ...

def test_validate_code_group_no_roles():
    ...

def test_auth_callable():
    ...

def test_auth_callable_fail():
    ...

def test_auth_role_check_callable_open_no_user_roles():
    ...

def test_auth_role_check_callable_open_with_user_roles():
    ...

def test_auth_role_check_callable_read_with_valid_user_roles():
    ...

def test_auth_role_check_callable_read_without_valid_user_roles():
    ...

def test_auth_role_check_callable_read_with_group_role_but_no_general_access():
    ...

def test_auth_role_check_callable_read_but_with_login_access():
    ...

def test_auth_role_check_callable_read_but_with_post_access():
    ...

def test_auth_role_check_callable_read_but_with_admin_access():
    ...

def test_auth_role_group_check_callable_read_with_group_read_access():
    ...

def test_auth_role_group_check_callable_read_with_read_but_not_group_access():
    ...

def test_auth_role_Group_check_callable_read_with_non_group_admin_access():
    ...

def test_auth_role_group_check_callable_read_with_access_to_other_group():
    ...

def test_crud_apply_query_security_open_user():
    ...

def test_crud_apply_query_security_user_is_admin():
    ...

def test_crud_apply_query_security_user_is_in_group():
    ...

def test_crud_apply_query_security_user_is_not_in_group():
    ...

def test_crud_apply_query_security_groups_user_is_in():
    ...

def test_crud_apply_query_security_groups_user_isnt_in():
    ...

def test_apply_patch_query_security_open():
    ...

def test_apply_patch_query_security_user_is_admin():
    ...

def test_apply_patch_query_security_user_groups_user_is_in():
    ...

def test_apply_patch_query_security_user_groups_user_isnt_in():
    ...

def test_patch_user_group_user_in_group_but_not_right_permission():
    ...

def test_patch_user_group_user_has_permission_in_another_group():
    ...

def test_apply_post_security_open():
    ...

def test_post_query_security_user_is_admin():
    ...

def test_post_query_security_user_is_in_group_with_permissions():
    ...

def test_post_query_security_user_is_in_group_without_proper_permissions():
    ...

def test_post_query_security_user_has_permissions_in_other_group():
    ...

def test_post_item_in_group():
    ...

def test_post_item_in_group_without_access_to_group():
    ...

def test_post_item_in_group_without_proper_permissions():
    ...

def test_post_item_in_group_with_greater_than_needed_permissions():
    ...

def test_post_item_in_group_with_group_only_requiring_open():
    ...

def test_post_item_in_wrong_group():
    ...

def test_get_index_filtered_by_group():
    ...

def test_get_index_query_param_not_in_group():
    ...

def test_patch_in_group():
    ...

def test_patch_not_in_group_admin():
    ...



