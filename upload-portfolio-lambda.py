import boto3
from botocore.client import Config
from io import StringIO, BytesIO
import zipfile
import mimetypes


def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic ('arn:aws:sns:us-east-1:257688244751:deployPortfolioTopic')

    try:
        s3 = boto3.resource('s3', config=Config(signature_version = 's3v4'))

        portfolio_bucket = s3.Bucket('portfolio.cedricdana.com')
        build_bucket = s3.Bucket('portfoliobuild.cedricdana.com')

        portfolio_zip = BytesIO()
        build_bucket.download_fileobj ('portfoliobuild.zip', portfolio_zip)


        with zipfile.ZipFile(portfolio_zip) as myzip:
          for nm in myzip.namelist():
            obj = myzip.open(nm)
            portfolio_bucket.upload_fileobj(obj, nm,
                ExtraArgs = {'ContentType': mimetypes.guess_type(nm)[0]})
            portfolio_bucket.Object(nm).Acl().put(ACL = 'public-read')

        print ("Job Done!")
        topic.publish(Subject="Portfolio Deployed", Message= "Portfolio Deployed succesfully")
    except:
        topic.publish("Subject Deploy Failed", Message = "The portfolio was not deployed succesfully!")
        raise
    return 'Hello from Lambda'
