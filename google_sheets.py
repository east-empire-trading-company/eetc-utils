from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import pandas as pd


class GoogleSheetsClient:
    def __init__(self, creds: dict, scope: list):
        self.creds = ServiceAccountCredentials.from_json_keyfile_dict(creds, scope)
        self.service = build("sheets", "v4", credentials=self.creds)
        self.sheet = self.service.spreadsheets()

    def get_single_sheet(self, sheets_url: str, sheet_name: str) -> list:
        """
        Reads and returns wanted sheet as List
        :param sheets_url: Google sheets url
        :param sheet_name: Name of the sheet we want to read
        """
        full_sheet = f"{sheet_name}" + "!A1:G4"  # change range as needed

        response = (
            self.sheet.values()
            .get(spreadsheetId=sheets_url, majorDimension="ROWS", range=full_sheet)
            .execute()
        )

        return response.get("values", [])

    def get_single_sheet_as_df(self, sheets_url: str, sheet_name: str) -> pd.DataFrame:
        """
        Returns wanted sheet as Pandas DataFrame
        :param sheets_url: Google sheets url
        :param sheet_name: Name of the sheet we want to convert to PandasDataFrame
        """
        sheet_data = self.get_single_sheet(sheets_url, sheet_name)

        df = pd.DataFrame(data=sheet_data[1:], columns=sheet_data[0])
        return df

    def get_single_sheet_as_dict(self, sheets_url: str, sheet_name: str) -> dict:
        """
        Returns wanted sheet as dict
        :param sheets_url: Google sheets url
        :param sheet_name: Name of the sheet we want to convert to dict
        """
        data = self.get_single_sheet(sheets_url, sheet_name)

        sheet_dict = {}
        key = f"{sheet_name}"
        for a in data[1:]:
            sheet_dict.setdefault(key, [])
            sheet_dict[key].append(a)

        return sheet_dict

    def get_entire_sheet(self, sheets_url: str, *args: str) -> dict:
        """
        Returns all wanted sheets as dict
        :param sheets_url: Google sheets url
        :param args: Name of sheets we want to convert to dict
        """
        sheet_names = list(args)
        sheet_range = "!A1:G4"  # change range as needed
        full_sheet_names = [x + sheet_range for x in sheet_names]

        response = (
            self.service.spreadsheets()
            .values()
            .batchGet(spreadsheetId=sheets_url, ranges=full_sheet_names)
            .execute()
        )

        sheets_dict = {}
        for item in response.get("valueRanges", []):
            sheets_dict[item["range"]] = item["values"]

        return sheets_dict
