import json
import logging
import os

from dotenv import load_dotenv
import awswrangler as wr

load_dotenv()

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class BuildCsv:
    def __init__(self, date_time: str):
        self.date_time = date_time

    @staticmethod
    def get_dataframe():
        conn = wr.postgresql.connect(
            secret_id=str(os.getenv("SECRET_ARN"))
        )
        df = wr.postgresql.read_sql_query(
            sql="SELECT email FROM user_company LIMIT 100;",
            con=conn
        )
        return df

    @staticmethod
    def update_data(dataframe):
        dataframe['FECHA_ENVIO'] = ''
        dataframe['FECHA_ACTIVIDAD'] = ''
        dataframe['CAMPANIA'] = ''
        dataframe['ACCION'] = ''
        dataframe['TIPO_ACCION'] = ''
        dataframe['ACTIVIDAD'] = ''
        dataframe['DESCRIPCION'] = ''
        dataframe['TAG'] = ''
        return dataframe

    def send_file(self, data_frame):
        wr.s3.to_csv(data_frame, f"s3://{os.getenv('BUCKET')}/IN_{self.date_time}.csv", index=False)

    def handler(self):
        self.send_file(data_frame=self.update_data(dataframe=self.get_dataframe()))


if __name__ == '__main__':
    build_csv = BuildCsv(date_time='202210181619')
    print(build_csv.handler())
