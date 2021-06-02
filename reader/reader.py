import pandas as pd

from sqlalchemy import create_engine

class Connection:

    def __call__(self,uri):
        engine = create_engine(uri,echo=True)
        return engine


class File_Reader:

    @staticmethod
    def read_csv(path:str) -> pd.DataFrame:
        df = pd.read_csv(path)
        return df

    @staticmethod
    def read_excel(path:str) -> pd.DataFrame:
        df = pd.read_excel(path)
        return df
    
    @staticmethod
    def read_table(con:Connection,tbl_name:str,uri:str) -> pd.DataFrame:
        table_df = pd.read_sql_table(tbl_name,con=con(str))

    @staticmethod
    def read_table(con:Connection,tbl_name:str,uri:str) -> pd.DataFrame:
        table_df = pd.read_sql_table(tbl_name,con=con(str))



