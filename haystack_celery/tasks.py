import logging

from celery.schedules import crontab
from celery.task import Task, PeriodicTask
from django.db.models.loading import get_model
from haystack import connections as haystack_connections
from haystack.management.commands import update_index

class SearchIndexUpdateTask(Task):
    name = "search.index.update"
    default_retry_delay = 5 * 60
    max_retries = 1

    def run(self, app_name, model_name, pk, **kwargs):
        try:
            model = get_model(app_name, model_name)
            instance = model.objects.get(pk=pk)
            unified_index = haystack_connections['default'].get_unified_index()
            index = unified_index.get_index(model)
            index.update_object(instance)
        except Exception, exc:
            logging.exception("Index not updated for expert")
            self.retry([app_name, model_name, pk], kwargs, exc=exc)


class SearchIndexUpdatePeriodicTask(PeriodicTask):
    name = "search.index.periodic_update"
    run_every = crontab(hour=0, minute=0)
    abstract = True
    
    def run(self, **kwargs):
        logging.info("Starting update index")
        update_index.Command().handle()
        logging.info("Finishing update index")

