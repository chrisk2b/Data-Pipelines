from airflow.hooks.postgres_hook import PostgresHook
from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'
    template_fields = ("s3_key",)
    str_sql_copy= """
                   COPY {}
                   FROM '{}'
                   ACCESS_KEY_ID '{}'
                   SECRET_ACCESS_KEY '{}'
                   JSON AS '{}'
                   REGION '{}'
                  """

    @apply_defaults
    def __init__(self,
                 target_table="",
                 s3_bucket="",
                 s3_key="",
                 redshift_conn_id="",
                 aws_conn_id="",
                 jsonpath="auto",
                 region="us-west-2",
                 *args,
                 **kwargs):

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        self.target_table=target_table
        self.s3_bucket=s3_bucket
        self.s3_key=s3_key
        self.redshift_conn_id=redshift_conn_id
        self.aws_conn_id=aws_conn_id
        self.jsonpath=jsonpath
        self.region=region
        #self.execution_date = kwargs['execution_date']


    def execute(self, context):
        aws_hook = AwsHook(self.aws_conn_id)
        credentials = aws_hook.get_credentials()
        redshift = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        
        self.log.info("Truncate insert: delete data in the target staging table")
        redshift.run("TRUNCATE TABLE {}".format(self.target_table))
        
        self.log.info("Start copy data from S3 to staging table in redshift")
        aws_access_key = credentials.access_key
        aws_secret_key = credentials.secret_key
        
        s3_path = "s3://{}/{}".format(self.s3_bucket, self.s3_key)
        
        str_execute = self.str_sql_copy.format(self.target_table,
                                               s3_path,
                                               aws_access_key,
                                               aws_secret_key,
                                               self.jsonpath,
                                               self.region)
        
        redshift.run(str_execute)
        self.log.info(f"Loaded data from S3 under {s3_path} to the redshift table {self.target_table}")




