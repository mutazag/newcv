from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta


def listFiles(account_name, account_key, container_name, prefix=None, delimiter=None):
    blob_service = BlobServiceClient(
        account_url=f"https://{account_name}.blob.core.windows.net/",
        credential=account_key)
    container_client = blob_service.get_container_client(container_name)
    blob_list = container_client.list_blobs()

    list1 = [
        {
        'blob_name': blob.name,
        'blob_url': blob_service.get_blob_client(container=container_name, blob=blob.name).url,
        'blob_sas': generate_blob_sas(
            account_name=account_name,
            account_key=account_key,
            container_name=container_name,
            blob_name=blob.name,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1))} for blob in blob_list]
    # return blob_list as a list
    blob_list = list(blob_list)

    return list1


def uploadFile(account_name, account_key, container_name, file):
    #https://www.c-sharpcorner.com/article/uploading-file-to-azure-blob-using-python/#:~:text=Uploading%20File%20To%20Azure%20Blob%20Using%20Python%201,Blob%20...%204%20File%20In%20Azure%20Blob%20
    blob_service = BlobServiceClient(
        account_url=f"https://{account_name}.blob.core.windows.net/",
        credential=account_key)
    blob_client = blob_service.get_blob_client(container_name, file.filename)
    # container_client = blob_service.get_container_client(container_name)
    # blob_client = container_client.get_blob_client(file.filename)
    blob_client.upload_blob(data=file.stream)

    return None