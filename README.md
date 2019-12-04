# Purpose of the Repository
This repository contains the results of the Data Engineering Nanodegree 'Data-Pipelines' Project. Its’s purpose is to give the reviewers access to the code. For more information click [here](https://www.udacity.com/course/data-engineer-nanodegree--nd027).
# Summary of the Project
A music streaming company, Sparkify, has decided that it is time to introduce more automation and monitoring to their data warehouse ETL pipelines and come to the conclusion that the best tool to achieve this is Apache Airflow.

They have decided to bring a data engineer into the project and expect the engineer to create high grade data pipelines that are dynamic and built from reusable tasks, can be monitored, and allow easy backfills. They have also noted that the data quality plays a big part when analyses are executed on top the data warehouse and want to run tests against their datasets after the ETL steps have been executed to catch any discrepancies in the datasets.

The source data resides in S3 and needs to be processed in Sparkify's data warehouse in Amazon Redshift. The source datasets consist of JSON logs that tell about user activity in the application and JSON metadata about the songs the users listen to.

# Raw Datasets
We will be working with two datasets that reside in S3. Here are the S3 links for each:

-   Song data:  `s3://udacity-dend/song_data`
-   Log data:  `s3://udacity-dend/log_data`

These datasets are visible to everyone. The song data contains data about all available songs at Sparkify while the log data contains data about user activity, i.e. "which user is listening to which song at which time".
# Overview of the Pipeline
The pipeline implements a ETL process where the raw data is located in S3, stages it into Redshift and transforms it into a set of fact and dimensional tables (cf. below). Furter, some data quality checks are performed. Below is a picture of the pipeline structure:
![Pipeline](https://github.com/chrisk2b/Data-Pipelines/blob/master/pics/pipeline.JPG)

# Files in the Repository
The following files/folders are contained in the repository:

 - [dags](https://github.com/chrisk2b/Data-Pipelines/tree/master/dags): a folder which contains the dags. The following files are in this folder:
  a) [etl_dag.py](https://github.com/chrisk2b/Data-Pipelines/blob/master/dags/etl_dag.py): this python file defines the main dag which describes the ETL process.

 - [plugins](https://github.com/chrisk2b/Data-Pipelines/tree/master/plugins): a folder which consists of two subfolders:
  a) [operators](https://github.com/chrisk2b/Data-Pipelines/tree/master/plugins/operators): this folder contains the definition of all customized operators, cf. below.
  b) [helpers](https://github.com/chrisk2b/Data-Pipelines/tree/master/plugins/helpers): contains the file [sql_queries.py](https://github.com/chrisk2b/Data-Pipelines/blob/master/plugins/helpers/sql_queries.py) which contains all SQL-queries used during the ETL process.

 - [create_tables.sql](https://github.com/chrisk2b/Data-Pipelines/blob/master/create_tables.sql): a file which contains all DDL statements to define the redshift tables (staging tables as well as fact and dimension tables) needed to store the data 
 - [README.md](https://github.com/chrisk2b/Data-Pipelines/blob/master/README.md): this README.

# How to run the ETL pipeline
As mentioned above, the pipeline is based on Apache Airflow. Hence, Airflow must be installed. This can be done e.g. by using Docker with the [puckel image](https://github.com/puckel/docker-airflow). Under [this link](https://github.com/puckel/docker-airflow) one can find further instructions to run Airflow with Docker. Also, an AWS account is needed and a Redshift cluster must be created. To interact with Redshift from Airflow, a corresponding connection (of type Postgres) must be created within Airflow. Further, to interact with S3 from Airflow, an AWS connection (of type Amazon Web Services) must be created in Airflow using a public-private key pair for a given AWS account.
To run the pipeline, the following steps must be executed:
 - Use a SQL-Client and connect to the Redshift cluster. Execute all DDL statement in the file [create_tables.sql](https://github.com/chrisk2b/Data-Pipelines/blob/master/create_tables.sql). This will create all necessary redshift tables.
 - Once Airflow is running and the dag defined in [etl_dag.py](https://github.com/chrisk2b/Data-Pipelines/blob/master/dags/etl_dag.py) is scheduled, the pipeline will run. Its progress can be tracked in the Airflow UI.

# Summary of the Target Datamodel
The file [create_tables.sql](https://github.com/chrisk2b/Data-Pipelines/blob/master/create_tables.sql) contains the definition of the staging tables staging_events and staging_songs which mimic the structure of the raw data in S3. Furter, the following fact and dimension tables define the target data model:

 - **Dimension Tables**:
	 1.  **users** - users of Sparkify
    -   _user_id, first_name, last_name, gender, level_
      2.  **songs** - songs in music database
    -   _song_id, title, artist_id, year, duration_
   3. **artists** - artists in music database
    -   _artist_id, name, location, latitude, longitude_
   5.  **time** - timestamps of records in **songplays** (cf. fact tables below) broken down into specific units
    -   _start_time, hour, day, week, month, year, weekday_
 - **Fact Tables**:
    1.  **songplays** - records in log data associated with song plays 

	-   _songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent_


# Customized Airflow Operators
The following customized operators are used and defined in the folder [operators](https://github.com/chrisk2b/Data-Pipelines/tree/master/plugins/operators):
 ### Stage Operator

The stage operator can load JSON formatted files from S3 to Amazon Redshift. The operator creates and runs a SQL COPY statement based on the parameters provided. The operator's parameters specify where in S3 the file is loaded and what is the target table.

The parameters are used to distinguish between JSON file. 

### Fact and Dimension Operators

With dimension and fact operators, one can utilize the SQL statements in the SQL helper class to run data transformations. Most of the logic is within the SQL transformations and the operator is expected to take as input a SQL statement and target database on which to run the query against. 

Dimension loads are often done with the truncate-insert pattern where the target table is emptied before the load. Thus, one could also have a parameter that allows switching between insert modes when loading dimensions. Fact tables are usually so massive that they should only allow append type functionality.

### Data Quality Operator

The final operator is the data quality operator, which is used to run checks on the data itself. The operator's main functionality is to receive one or more SQL based test cases along with the expected results and execute the tests. For each test, the test result and expected result needs to be checked and if there is no match, the operator raises an exception and the task should retry and fail eventually.



	 

 
 Summary of the Datamodel
The Datamodel is based on a Star Sche
