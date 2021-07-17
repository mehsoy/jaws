from application.system.user import User, Administrator
from application.system.user_role import UserRole
from exceptions.user_not_found_exception import UserNotFoundException


def test_user():
    try:
        user = User.get_user_by_username("testuser")
    except UserNotFoundException:
        user = User("testuser", "token")

    assert user.get_token() == "token"
    assert user.get_username() == "testuser"
    assert user.get_user_type() == UserRole.User


def test_inheritance():
    try:
        user = User.get_user_by_username("testuser5")
    except UserNotFoundException:
        user = User("testuser5", "token")

    user.set_user_type(UserRole.Administrator)
    assert user.get_user_type() == UserRole.Administrator

    administrator = User.get_user_by_username("testuser5")
    assert administrator.get_user_type() == UserRole.Administrator

    assert isinstance(administrator, Administrator)

    administrator.set_user_type(UserRole.User)
    user = User.get_user_by_username("testuser5")
    assert user.get_user_type() == UserRole.User
    assert not isinstance(user, Administrator)
    assert isinstance(user, User)


