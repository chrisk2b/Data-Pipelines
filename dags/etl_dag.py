from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import (StageToRedshiftOperator, LoadFactOperator,
                                LoadDimensionOperator, DataQualityOperator)
from helpers import SqlQueries

# AWS_KEY = os.environ.get('AWS_KEY')
# AWS_SECRET = os.environ.get('AWS_SECRET')

default_args = {
    'owner': 'udacity',
    'start_date': datetime(2019, 1, 12),
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'email_on_retry': False,
    'catchup': False
}

#########################################
# Definition of the DAG
#########################################

dag = DAG('udac_example_dag',
          default_args=default_args,
          description='Load and transform data in Redshift with Airflow',
          schedule_interval='0 * * * *'
        )

#########################################
# Definition of the tasks
#########################################

start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)

stage_events_to_redshift = StageToRedshiftOperator(
    task_id='Stage_events',
    dag=dag,
    target_table='staging_events',
    s3_bucket='udacity-dend',
    s3_key='log_data',
    redshift_conn_id='redshift',
    aws_conn_id='aws_credentials',
    jsonpath='s3://udacity-dend/log_json_path.json'
    
)

stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Stage_songs',
    dag=dag,
    target_table='staging_songs',
    s3_bucket='udacity-dend',
    s3_key='song_data',
    redshift_conn_id='redshift',
    aws_conn_id='aws_credentials'
)

load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    dag=dag,
    target_table='songplays',
    redshift_conn_id='redshift',
    str_sql_select=SqlQueries.songplay_table_insert
)

load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    dag=dag,
    target_table='users',
    redshift_conn_id='redshift',
    str_sql_select=SqlQueries.user_table_insert
)

load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    dag=dag,
    target_table='songs',
    redshift_conn_id='redshift',
    str_sql_select=SqlQueries.song_table_insert
)

load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    dag=dag,
    target_table='artists',
    redshift_conn_id='redshift',
    str_sql_select=SqlQueries.artist_table_insert
)

load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    dag=dag,
    target_table='time',
    redshift_conn_id='redshift',
    str_sql_select=SqlQueries.time_table_insert
)

run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    dag=dag,
    redshift_conn_id='redshift',
    tables=['songplays',
            'songs',
            'users',
            'artists',
            'time']
)

end_operator = DummyOperator(task_id='Stop_execution',  dag=dag)

##################################################################
# Definition of task dependencies
##################################################################

start_operator >> stage_events_to_redshift
start_operator >> stage_songs_to_redshift

stage_events_to_redshift >> load_songplays_table
stage_songs_to_redshift >> load_songplays_table

load_songplays_table >> load_user_dimension_table
load_songplays_table >> load_song_dimension_table
load_songplays_table >> load_time_dimension_table
load_songplays_table >> load_artist_dimension_table

load_user_dimension_table >> run_quality_checks
load_song_dimension_table >> run_quality_checks
load_time_dimension_table >> run_quality_checks
load_artist_dimension_table >> run_quality_checks

run_quality_checks >> end_operator
