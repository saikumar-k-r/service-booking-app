from django.urls import path

from .views import ReliableOperationView, IncrementalSyncView


urlpatterns = [
    path(
        "reliable-operation/",
        ReliableOperationView.as_view(),
        name="reliable-operation",
    ),
    path(
        "sync/",
        IncrementalSyncView.as_view(),
        name="incremental-sync",
    ),
]