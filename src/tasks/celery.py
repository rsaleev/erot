from celery import Celery

app = Celery('erot',
             broker='amqp://',
             backend='rpc://',
             include=['src.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    task_routes = {
        'proj.tasks.add': {'queue': 'erot_etl'},
    },
)


if __name__ == '__main__':
    app.start()


