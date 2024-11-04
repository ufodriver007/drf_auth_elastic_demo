from drf_downloader.celery_app import app


@app.task()
def process_file(path: str) -> str:
    try:
        counter = 0
        with open(path, 'r') as f:
            for line in f:
                counter += 1
    except Exception as e:
        return str('Not an utf-8 file')

    return str(counter)
