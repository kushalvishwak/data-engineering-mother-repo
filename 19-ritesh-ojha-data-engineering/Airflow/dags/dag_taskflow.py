from airflow.decorators import dag, task
from datetime import datetime, timedelta


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

@dag(
    dag_id='dag_taskflow',
    default_args=default_args,
    start_date=datetime(2024, 3, 21),
    schedule= '@daily'
)

def hello_world():
    @task
    def hello():
        print('Hello World!')

    @task
    def goodbye():
        print('Goodbye World!')
        
    hello() >> goodbye()
        
greet_dag = hello_world()  

