
from django.contrib.auth.mixins import UserPassesTestMixin


class AlwaysAllowToAccessToAdminMixin(UserPassesTestMixin):

    def test_func(self):
        return True
