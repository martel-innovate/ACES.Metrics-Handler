from prefect import flow, get_run_logger, task

@task
def init_a():
    a =1
    return a

@task
def init_b():
    b =1
    return b



@flow
def load_data() -> None:
    a = init_a()
    b = init_b()
    c = a+b