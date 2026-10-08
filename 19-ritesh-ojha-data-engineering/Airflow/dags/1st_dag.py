from  datetime import datetime
from airflow.operators.bash import BashOperator
from airflow import DAG


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1
}


with DAG(
    dag_id= "first_dag",
    default_args= default_args,
    description="This is my first day of airflow",
    start_date= datetime(2024,3,21),
    schedule_interval='@daily'
    
) as dag:
    task1 =  BashOperator(
        task_id = "task1",
        bash_command = "echo hello"
    )
    
    task2 = BashOperator(
        task_id = "task2",
        depends_on_past = True,
        bash_command= 'sleep 5; echo World! How are you?'
    )
    
    
    task1 >> task2

