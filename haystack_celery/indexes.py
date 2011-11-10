from django.db.models import signals
from django.db.models.loading import get_model
from haystack import indexes

from tasks import SearchIndexUpdateTask

def remove_instance_from_index(instance):
    model = get_model(instance._meta.app_label, instance._meta.module_name)
    unified_index = haystack_connections['default'].get_unified_index()
    index = unified_index.get_index(model)
    index.remove_object(instance)

class QueuedSearchIndex(indexes.SearchIndex):
    """
    A ``SearchIndex`` subclass that enqueues updates for later processing.

    Deletes are handled instantly since a reference, not the instance, is put on the queue. It would not be hard
    to update this to handle deletes as well (with a delete task).
    """
    # We override the built-in _setup_* methods to connect the enqueuing operation.
    def _setup_save(self):
        signals.post_save.connect(self.enqueue_save, sender=self.get_model())

    def _setup_delete(self):
        signals.post_delete.connect(self.enqueue_delete, sender=self.get_model())

    def _teardown_save(self):
        signals.post_save.disconnect(self.enqueue_save, sender=self.get_model())

    def _teardown_delete(self):
        signals.post_delete.disconnect(self.enqueue_delete, sender=self.get_model())

    def enqueue_save(self, instance, **kwargs):
        SearchIndexUpdateTask.delay(instance._meta.app_label, instance._meta.module_name, instance._get_pk_val())

    def enqueue_delete(self, instance, **kwargs):
        remove_instance_from_index(instance)
    
