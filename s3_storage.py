"""
AWS S3 Storage Integration for File Drive
Provides cloud storage capabilities with fast upload/download
"""
import boto3
import uuid
import mimetypes
from botocore.exceptions import ClientError
import os
from werkzeug.utils import secure_filename

class S3Storage:
    def __init__(self, bucket_name=None, region_name='us-east-1'):
        self.bucket_name = bucket_name or os.environ.get('AWS_S3_BUCKET_NAME')
        self.region_name = region_name
        
        # Initialize S3 client
        try:
            # Only initialize if AWS credentials are provided
            aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
            aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
            
            if aws_access_key and aws_secret_key:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=self.region_name
                )
            else:
                self.s3_client = None
        except Exception:
            self.s3_client = None
    
    def is_configured(self):
        """Check if S3 is properly configured"""
        return (
            self.s3_client is not None and 
            self.bucket_name and
            os.environ.get('AWS_ACCESS_KEY_ID') and
            os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
    
    def generate_file_key(self, team_id, original_filename):
        """Generate a unique S3 key for the file"""
        secure_name = secure_filename(original_filename)
        unique_id = str(uuid.uuid4())
        return f"teams/{team_id}/files/{unique_id}_{secure_name}"
    
    def upload_file(self, file_obj, team_id, original_filename):
        """Upload file to S3 and return the key and URL"""
        if not self.is_configured():
            return None, None
        
        try:
            file_key = self.generate_file_key(team_id, original_filename)
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(original_filename)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Upload file to S3
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                file_key,
                ExtraArgs={
                    'ContentType': content_type,
                    'ServerSideEncryption': 'AES256'
                }
            )
            
            # Generate public URL
            file_url = f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{file_key}"
            
            return file_key, file_url
            
        except ClientError as e:
            print(f"Error uploading file to S3: {e}")
            return None, None
    
    def delete_file(self, file_key):
        """Delete file from S3"""
        if not self.is_configured():
            return False
        
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True
        except ClientError as e:
            print(f"Error deleting file from S3: {e}")
            return False
    
    def generate_presigned_url(self, file_key, expiration=3600):
        """Generate a presigned URL for secure file access"""
        if not self.is_configured():
            return None
        
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None
    
    def get_file_info(self, file_key):
        """Get metadata about a file in S3"""
        if not self.is_configured():
            return None
        
        try:
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return {
                'size': response['ContentLength'],
                'last_modified': response['LastModified'],
                'content_type': response.get('ContentType', 'application/octet-stream')
            }
        except ClientError as e:
            print(f"Error getting file info: {e}")
            return None

# Global S3Storage instance
s3_storage = S3Storage()

# Helper functions for easy integration
def upload_to_s3(file_obj, team_id, original_filename):
    """Upload file to S3 or local storage as fallback"""
    if s3_storage.is_configured():
        return s3_storage.upload_file(file_obj, team_id, original_filename)
    else:
        # Fallback to local storage
        return None, None

def delete_from_s3(file_key):
    """Delete file from S3"""
    if s3_storage.is_configured():
        return s3_storage.delete_file(file_key)
    return False

def get_download_url(file_key):
    """Get secure download URL for file"""
    if s3_storage.is_configured():
        return s3_storage.generate_presigned_url(file_key)
    return None