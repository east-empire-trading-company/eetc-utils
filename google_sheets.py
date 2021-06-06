from typing import Dict

from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import pandas as pd


class GoogleSheetsClient:
    def __init__(self, creds: dict, scope: list):
        """
        Google Sheets API access constructor

        :param creds credentials obtained from Google Cloud Platform
        :param scope API service endpoint, "https://www.googleapis.com/auth/spreadsheets"
        """

        self.creds = ServiceAccountCredentials.from_json_keyfile_dict(creds, scope)
        self.service = build("sheets", "v4", credentials=self.creds)
        self.sheet = self.service.spreadsheets()

    def get_single_sheet_as_dict(self, spreadsheet_id: str, sheet_name: str) -> Dict:
        """
        Returns wanted sheet as dict
        :param spreadsheet_id: Google sheets url
        :param sheet_name: Name of the sheet we want to convert to dict
        """

        full_sheet = f"{sheet_name}" + "!A1:G100"  # change range as needed

        response = (
            self.sheet.values()
            .get(spreadsheetId=spreadsheet_id, majorDimension="ROWS", range=full_sheet)
            .execute()
        )

        sheet_as_dict = []

        all_rows = response.get("values", [])
        column_row = all_rows[0]  # the first row is the column row

        for row in all_rows[1:]:
            row_dict = {}
            # populate row_dict with col: val pairs
            for i, val in enumerate(row):
                # a value at position i corresponds to the column of position i
                col = column_row[i]
                row_dict[col] = val

            if len(row_dict) > 1:  # eliminates rows without values
                sheet_as_dict.append(row_dict)

        return sheet_as_dict

    def get_single_sheet_as_df(
        self, spreadsheet_id: str, sheet_name: str
    ) -> pd.DataFrame:
        """
        Returns wanted sheet as Pandas DataFrame
        :param spreadsheet_id: Google sheets url
        :param sheet_name: Name of the sheet we want to convert to PandasDataFrame
        """
        sheet_data = self.get_single_sheet_as_dict(spreadsheet_id, sheet_name)

        df = pd.DataFrame(data=sheet_data, columns=sheet_data[0])

        return df

    def get_all_sheets_as_dicts(
        self, spreadsheet_id: str, *args: str
    ) -> Dict[str, Dict]:
        """
        Returns all wanted sheets as dict containing dicts
        :param spreadsheet_id: Google sheets url
        :param args: Name of sheets we want to convert to dict
        """
        sheet_names = list(args)

        sheets_dict = {}
        for sheet_name in sheet_names:
            sheets_dict[sheet_name] = self.get_single_sheet_as_dict(
                spreadsheet_id, sheet_name
            )

        return sheets_dict

    def get_all_sheets_as_dfs(
        self, spreadsheet_id: str, *args: str
    ) -> Dict[str, pd.DataFrame]:
        """
        Returns all wanted sheets as dict containing dataframes
        :param spreadsheet_id: Google sheets url
        :param args: Name of sheets we want to convert to dict
        """
        sheet_names = list(args)
        sheets_as_dfs = {}
        for sheet_name in sheet_names:
            sheets_as_dfs[sheet_name] = self.get_single_sheet_as_df(
                spreadsheet_id, sheet_name,
            )
        return sheets_as_dfs
