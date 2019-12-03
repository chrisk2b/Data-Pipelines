from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadFactOperator(BaseOperator):

    ui_color = '#F98866'
   
    @apply_defaults
    def __init__(self,
                 target_table='',
                 redshift_conn_id='',
                 str_sql_select='',
                 *args, **kwargs):

        super(LoadFactOperator, self).__init__(*args, **kwargs)
        self.target_table=target_table
        self.conn_id=redshift_conn_id
        self.str_sql_select=str_sql_select

    def execute(self, context):
        self.log.info(f"start loading fact table {self.target_table}")
        redshift = PostgresHook(postgres_conn_id=self.conn_id)
        str_sql_insert = f"INSERT INTO {self.target_table} {self.str_sql_select}"
        redshift.run(str_sql_insert)
        self.log.info(f"finished loading fact table {self.target_table}")
