from routers.web_router.navigator.abstract import NavBase


class HomeNavigator(NavBase):
    def __init__(self):
        super().__init__("/home", None, "web_home")
