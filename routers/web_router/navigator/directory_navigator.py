from routers.web_router.navigator.abstract import NavBase


class DirectoryClaimsTemplateNavigator(NavBase):
    def __init__(self):
        super().__init__("", None, "directory_claims")


class DirectoryClaimsFormNavigator(NavBase):
    def __init__(self):
        super().__init__("", None, "directory_claims_form")


class DirectoryClaimsNavigator(NavBase):
    def __init__(self):
        super().__init__("/directory_claims", None, "directories")
        self._template = DirectoryClaimsTemplateNavigator()
        self._form = DirectoryClaimsFormNavigator()

    @property
    def template(self) -> DirectoryClaimsTemplateNavigator:
        return self._template

    @property
    def form(self) -> DirectoryClaimsFormNavigator:
        return self._form


class DepartmentDirectoryTemplateNavigator(NavBase):
    def __init__(self):
        super().__init__("", None, "department_directory")


class DepartmentDirectoryNavigator(NavBase):
    def __init__(self):
        super().__init__("/department_directory", None, "directories")
        self._template = DepartmentDirectoryTemplateNavigator()

    @property
    def template(self) -> DepartmentDirectoryTemplateNavigator:
        return self._template


class DirectoryDirectionTemplateNavigator(NavBase):
    def __init__(self):
        super().__init__("", None, "directory_direction")


class DirectoryDirectionFormNavigator(NavBase):
    def __init__(self):
        super().__init__("", None, "directory_direction_form")


class DirectoryDirectionNavigator(NavBase):
    def __init__(self):
        super().__init__("/directory_direction", None, "directories")
        self._template = DirectoryDirectionTemplateNavigator()
        self._form = DirectoryDirectionFormNavigator()

    @property
    def template(self) -> DirectoryDirectionTemplateNavigator:
        return self._template

    @property
    def form(self) -> DirectoryDirectionFormNavigator:
        return self._form


class DirectoriesIndexNavigator(NavBase):
    def __init__(self):
        super().__init__("", None, "directories")


class DirectoriesNavigator(NavBase):

    def __init__(self):
        super().__init__("/directories", None, "directories")
        self._index = DirectoriesIndexNavigator()
        self._directory_claims = DirectoryClaimsNavigator()
        self._department_directory = DepartmentDirectoryNavigator()
        self._directory_direction = DirectoryDirectionNavigator()

    @property
    def index(self) -> DirectoriesIndexNavigator:
        return self._index

    @property
    def directory_claims(self) -> DirectoryClaimsNavigator:
        return self._directory_claims

    @property
    def department_directory(self) -> DepartmentDirectoryNavigator:
        return self._department_directory

    @property
    def directory_direction(self) -> DirectoryDirectionNavigator:
        return self._directory_direction
