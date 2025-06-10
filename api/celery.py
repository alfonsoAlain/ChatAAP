# myproject/celery.py  
from __future__ import absolute_import, unicode_literals  
import os  
from celery import Celery  

# establecer el módulo de configuración predeterminado de Django para el programa 'celery'  
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')  

app = Celery('api')  
app.conf.broker_url = 'amqp://inversor:Inversor2024@127.0.0.1:5672//'

# carga la configuración de Django  
app.config_from_object('django.conf:settings', namespace='CELERY')  

# carga las tareas de todos los módulos de tareas de Django  
app.autodiscover_tasks()
