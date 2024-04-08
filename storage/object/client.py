import io
import pandas as pd
from typing import Union

from minio import Minio


class MinioObject(object):
    def __init__(
            self,
            endpoint,
            port,
            access_key,
            secret_key,
            bucket_name
    ):
        self.client = Minio(
            endpoint=f'{endpoint}:{port}',
            access_key=access_key,
            secret_key=secret_key,
            secure=False
        )
        self.bucket = bucket_name

    def __get__(self, name: str) -> io.BytesIO:
        """ Get an object from S3 storage. name is the key of the object. """
        obj = self.client.get_object(
            bucket_name=self.bucket,
            object_name=name
        )
        data = io.BytesIO()
        data.write(obj.read())
        data.seek(0)
        return data

    def __put__(self, name: str, length: int, data: io.BytesIO) -> str:
        """ Put an object into S3 storage. data is the content to upload."""
        return self.client.put_object(
            bucket_name=self.bucket,
            object_name=name,
            length=length,
            data=data
        )

    def put_json(
            self,
            df: Union[pd.Series, pd.DataFrame],
            name: str,
            **kwargs
    ) -> str:
        """ Store a pandas.Series or pandas.Dataframe in json format into s3 storage """
        data = io.BytesIO()
        json_bytes = df.to_json(path_or_buf=None, **kwargs).encode("utf-8")
        data.write(json_bytes)
        nb_bytes = data.tell()
        data.seek(0)
        return self.__put__(name, length=nb_bytes, data=data)

    def put_csv(
            self,
            df: Union[pd.Series, pd.DataFrame],
            name: str,
            index: bool = False,
            **kwargs
    ) -> str:
        """ Store a pandas.Series or pandas.Dataframe in csv format into s3 storage """
        data = io.BytesIO()
        csv_bytes = df.to_csv(path_or_buf=None, index=index, **kwargs).encode("utf-8")
        data.write(csv_bytes)
        nb_bytes = data.tell()
        data.seek(0)
        return self.__put__(name, length=nb_bytes, data=data)

    def read_csv(self, name: str, **kwargs) -> Union[pd.Series, pd.DataFrame]:
        """ Read a pandas DataFrame stored as csv file from s3 storage. """
        data = self.__get__(name)
        return pd.read_csv(data, **kwargs)

    def list_objects_(
            self,
            bucket_name,
            prefix,
            with_path=False,
            recursive=False
    ):
        result_obj = self.client.list_objects(
            bucket_name=bucket_name,
            prefix=prefix,
            recursive=recursive
        )
        if with_path:
            obj_names = [obj._object_name for obj in result_obj]
        else:
            obj_names = [obj._object_name.replace(
                f"{prefix}", ""
            )
                for obj in result_obj]
        return obj_names


