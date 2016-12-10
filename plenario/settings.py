import botocore.exceptions
import boto3
import requests
from os import environ

get = environ.get

SECRET_KEY = get('SECRET_KEY', 'abcdefghijklmnop')
PLENARIO_SENTRY_URL = get('PLENARIO_SENTRY_URL', None)
CELERY_SENTRY_URL = get('CELERY_SENTRY_URL', None)
DATA_DIR = '/tmp'

# Travis CI relies on the default values to build correctly,
# just keep in mind that if you push changes to the default
# values, you need to make sure to adjust for these changes 
# in the travis.yml
DB_USER = get('DB_USER', 'postgres')
DB_PASSWORD = get('DB_PASSWORD', 'password')
DB_HOST = get('DB_HOST', 'localhost')
DB_PORT = get('DB_PORT', 5432)
DB_NAME = get('DB_NAME', 'plenario_test')

RS_USER = get('RS_USER', 'postgres')
RS_PASSWORD = get('RS_PASSWORD', 'password')
RS_HOST = get('RS_HOST', 'localhost')
RS_PORT = get('RS_PORT', 5432)
RS_NAME = get('RS_NAME', 'sensor_obs_test')

DATABASE_CONN = 'postgresql://{}:{}@{}:{}/{}'.\
    format(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)
REDSHIFT_CONN = 'postgresql://{}:{}@{}:{}/{}'.\
    format(RS_USER, RS_PASSWORD, RS_HOST, RS_PORT, RS_NAME)

# Use this cache for data that can be refreshed
REDIS_HOST = get('REDIS_HOST', "localhost")
# Use this cache for data that needs protection from the API flush
REDIS_HOST_SAFE = get("REDIS_HOST_SAFE", "")

# See: https://pythonhosted.org/Flask-Cache/#configuring-flask-cache
# for config options
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': REDIS_HOST,
    'CACHE_KEY_PREFIX': get('CACHE_KEY_PREFIX', 'plenario_app')
}

# Load a default admin
DEFAULT_USER = {
    'name': get('DEFAULT_USER_NAME', 'Plenario Admin'),
    'email': get('DEFAULT_USER_EMAIL', 'plenario@email.com'),
    'password': get('DEFAULT_USER_PASSWORD', 'changemeplz')
}

AWS_ACCESS_KEY = get('AWS_ACCESS_KEY_ID', '')
AWS_SECRET_KEY = get('AWS_SECRET_KEY', '')
S3_BUCKET = get('S3_BUCKET', '')
AWS_REGION_NAME = get('AWS_REGION_NAME', 'us-east-1')

# Email address for notifying site administrators
# Expect comma-delimited list of emails.
email_list = get('ADMIN_EMAILS')
if email_list:
    ADMIN_EMAILS = email_list.split(',')
else:
    ADMIN_EMAILS = []

# For emailing users. ('MAIL_USERNAME' is an email address.)
MAIL_SERVER = get('MAIL_SERVER', 'smtp.gmail.com')
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_DISPLAY_NAME = 'Plenar.io Team'
MAIL_USERNAME = get('MAIL_USERNAME', '')
MAIL_PASSWORD = get('MAIL_PASSWORD', '')

# Toggle maintenence mode
MAINTENANCE = False

# SQS Jobs Queue
JOBS_QUEUE = get('JOBS_QUEUE', 'plenario-queue-test')


def get_ec2_instance_id():
    """Retrieve the instance id for the currently running EC2 instance. If
    the host machine is not an EC2 instance or is for some reason unable
    to make requests, return None.

    :returns: (str) id of the current EC2 instance
              (None) if the id could not be found"""

    instance_id_url = "http://169.254.169.254/latest/meta-data/instance-id"
    try:
        return requests.get(instance_id_url, timeout=1).text
    except requests.ConnectionError as err:
        print err.message

INSTANCE_ID = get_ec2_instance_id()


def get_autoscaling_group():
    """Retrieve the autoscaling group name of the current instance. If
    the host machine is not an EC2 instance, not subject to autoscaling,
    or unable to make requests, return None.

    :returns: (str) id of the current autoscaling group
              (None) if the autoscaling group could not be found"""

    try:
        autoscaling_client = boto3.client("autoscaling", region_name=AWS_REGION_NAME)
        return autoscaling_client.describe_auto_scaling_instances(
            InstanceIds=[INSTANCE_ID]
        )["AutoScalingInstances"][0]["AutoScalingGroupName"]
    except botocore.exceptions.BotoCoreError as err:
        print err.message
    except botocore.exceptions.ClientError as err:
        print err.message

AUTOSCALING_GROUP = get_autoscaling_group()
