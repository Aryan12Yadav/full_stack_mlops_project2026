import sys
import pandas as pd
import numpy as np
from typing import Optional

from src.configuration.mongo_db_connection import MongoDBClient
from src.constants import DATABASE_NAME
from src.exception import MyException

class Proj1Data:
    """
    A class to export MongoDB records as a pandas DataFrame.
    """

    def __init__(self) -> None:
        """
        Initializes the MongoDB client connection.
        """
        try:
            self.mongo_client = MongoDBClient(database_name=DATABASE_NAME)
        except Exception as e:
            raise MyException(e, sys)

    def export_collection_as_dataframe(self, collection_name: str, database_name: Optional[str] = None) -> pd.DataFrame:
        """
        Exports an entire MongoDB collection as a pandas DataFrame.

        Parameters:
        ----------
        collection_name : str
            The name of the MongoDB collection to export.
        database_name : Optional[str]
            Name of the database (optional). Defaults to DATABASE_NAME.

        Returns:
        -------
        pd.DataFrame
            DataFrame containing the collection data, with '_id' column removed and 'na' values replaced with NaN.
        """
        try:
            # Access specified collection from the default or specified database
            if database_name is None:
                collection = self.mongo_client.database[collection_name]
            else:
                collection = self.mongo_client[database_name][collection_name]

            # Convert collection data to DataFrame and preprocess
            print("Fetching data from mongoDB in batches to avoid timeout...")
            records = []
            last_id = None
            batch_size = 10000

            while True:
                query = {}
                if last_id is not None:
                    query['_id'] = {'$gt': last_id}
                
                # Fetch a batch of records with retry logic
                batch = None
                retries = 3
                for attempt in range(retries):
                    try:
                        batch = list(collection.find(query).sort('_id', 1).limit(batch_size))
                        break
                    except Exception as e:
                        import time
                        print(f"Network error on batch fetch (attempt {attempt+1}/{retries}): {e}")
                        time.sleep(3)
                        if attempt == retries - 1:
                            raise e
                
                if not batch:
                    break
                    
                records.extend(batch)
                last_id = batch[-1]['_id']
                print(f"Fetched {len(records)} records so far...")

            df = pd.DataFrame(records)
            print(f"Data fecthed with total len: {len(df)}")
            if "_id" in df.columns.to_list():
                df = df.drop("_id", axis=1)
            df.replace({"na":np.nan},inplace=True)
            return df

        except Exception as e:
            raise MyException(e, sys)