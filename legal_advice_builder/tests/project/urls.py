from django.urls import include
from django.urls import path

urlpatterns = [
    path('advicebuilder/admin/', include('legal_advice_builder.urls'))
]
