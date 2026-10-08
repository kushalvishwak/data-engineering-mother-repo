from airflow import DAG
from datetime import datetime, timedelta
from airflow.providers.http.sensors.http import HttpSensor

import json
from airflow.providers.http.operators.http import SimpleHttpOperator
import pandas as pd
from airflow.operators.python import PythonOperator




def kelvin_to_fahrenheit(temp_in_kelvin):
    temp_in_fahrenheit = (temp_in_kelvin - 273.15) * (9/5) + 32
    return temp_in_fahrenheit


def transform_load_data(task_instance):
    data = task_instance.xcom_pull(task_ids="extract_weather_data")
    city = data["name"]
    weather_description = data["weather"][0]['description']
    temp_farenheit = kelvin_to_fahrenheit(data["main"]["temp"])
    feels_like_farenheit= kelvin_to_fahrenheit(data["main"]["feels_like"])
    min_temp_farenheit = kelvin_to_fahrenheit(data["main"]["temp_min"])
    max_temp_farenheit = kelvin_to_fahrenheit(data["main"]["temp_max"])
    pressure = data["main"]["pressure"]
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]
    time_of_record = datetime.utcfromtimestamp(data['dt'] + data['timezone'])
    sunrise_time = datetime.utcfromtimestamp(data['sys']['sunrise'] + data['timezone'])
    sunset_time = datetime.utcfromtimestamp(data['sys']['sunset'] + data['timezone'])

    transformed_data = {"City": city,
                        "Description": weather_description,
                        "Temperature (F)": temp_farenheit,
                        "Feels Like (F)": feels_like_farenheit,
                        "Minimun Temp (F)":min_temp_farenheit,
                        "Maximum Temp (F)": max_temp_farenheit,
                        "Pressure": pressure,
                        "Humidty": humidity,
                        "Wind Speed": wind_speed,
                        "Time of Record": time_of_record,
                        "Sunrise (Local Time)":sunrise_time,
                        "Sunset (Local Time)": sunset_time                        
                        }
    transformed_data_list = [transformed_data]
    df_data = pd.DataFrame(transformed_data_list)
    # aws_credentials = {"key": "xxxxxxxxx", "secret": "xxxxxxxxxx", "token": "xxxxxxxxxxxxxx"}

    now = datetime.now()
    dt_string = now.strftime("%d%m%Y%H%M%S")
    dt_string = 'current_weather_data_portland_' + dt_string
    # df_data.to_csv(f"s3://weatherapiairflowyoutubebucket-yml/{dt_string}.csv", index=False, storage_options=aws_credentials)
    df_data.to_csv(f"{dt_string}.csv",index=False)


default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024,3,17),
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry' : False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
    

}

    
with DAG('weather_dag',
    default_args=default_args,
    schedule_interval = '@daily',
    catchup=False) as dag:


    is_weather_api_ready = HttpSensor(
    task_id ='is_weather_api_ready',
    http_conn_id='weathermap_api',
    endpoint='/data/2.5/weather?q=Portland&APPID=e1cb4f63b4382fbf753f111ef016216c'
    )


    extract_weather_data = SimpleHttpOperator(
    task_id = 'extract_weather_data',
    http_conn_id = 'weathermap_api',
    endpoint='/data/2.5/weather?q=Portland&APPID=e1cb4f63b4382fbf753f111ef016216c',
    method = 'GET',
    response_filter= lambda r: json.loads(r.text),
    log_response=True
    )

    transform_load_weather_data = PythonOperator(
    task_id= 'transform_load_weather_data',
    python_callable=transform_load_data
    )




    is_weather_api_ready >> extract_weather_data >> transform_load_weather_data