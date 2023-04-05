import openpyxl
import os


class Loader:
    _input_path = None
    def __init__(self, input_path: str):
        self.data = []
        self.input_path = input_path
        self.load_data()

    @property
    def input_path(self) -> str:
        return self._input_path
    
    @input_path.setter
    def input_path(self, value: str):
        if not os.path.exists(value):
            raise FileNotFoundError(f"Cannot locate inpurt data file -> {value}")
        self._input_path = value
    
    def load_data(self):
        wb = openpyxl.load_workbook(self.input_path)
        ws = wb[wb.sheetnames[0]]

        for row in range(1, ws.max_row + 1):
            name_address = f"A{row}"
            price_address = f"C{row}"
            name = ws[name_address].value
            price = ws[price_address].value

            if name is None or price is None or (isinstance(price, str) and "=" in price):
                continue

            self.data.append({"addresses": [name_address, price_address], "name": name, "price": price})
