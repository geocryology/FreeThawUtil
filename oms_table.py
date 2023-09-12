import datetime
import pandas as pd
import re
from typing import Optional, Any, Union
import numpy as np
## Create a freethaw time series


class OmsTable:

    def __init__(self,
                 data:pd.DataFrame,
                 tblheader:str="OMS Data Table", 
                 dtypes:list=[],
                 formats:list=[],
                 metadata:Optional[dict] = None):
        
        """Create a new OmsTable object.
        
        Parameters
        ----------
        data : pd.DataFrame
            Data to be stored in the table.
        tblheader : str, optional
            Header of the table, by default "OMS Data Table"
        dtypes : list
            List of data types
        formats : list
            List of formats
        metadata : Optional[dict], optional
            Metadata to be stored in the table, by default None

        Notes
        -----
        The are the follwing types available:

        Date
        Real
        Boolean
        Integer
        String 
    
        """
        self._tblheader = tblheader
        self._metadata = metadata
        self._columns = data.columns
        self._formats = formats
        self._dtypes = dtypes
        self._df = data

    @property
    def data(self):
        return self._df

    @property
    def header(self):
        return self._tblheader
    
    @property
    def metadata(self):
        return self._metadata
    
    def write(self, filename:str):
        with open(filename, 'w') as f:
            # Header
            f.write(f"@Table, {self.header}\n")
            
            # Metadata
            if self.metadata:
                for k, v in self.metadata.items():
                    if isinstance(v, list):
                        f.write(f"{k},{','.join(v)}\n")
                    else:
                        f.write(f"{k},{v}\n")

            # format & type (special metadata?)
            f.write(f"Type,{','.join(dtype for dtype in self._dtypes)}\n")
            f.write(f"Format,{','.join(format for format in self._formats)}\n")

            # Columns
            if len(self._columns) > 0:
                f.write(f"@Header,{','.join(self._columns)}\n")
            else:
                raise ValueError("No columns defined")

            # Data
            tbl = pd.DataFrame(data=self.data.values)
            tbl.insert(0, "blank", "")
            f.write(tbl.to_csv(index=False, header=False, lineterminator="\n"))


    @classmethod
    def from_pandas(cls, df):
        data = df.to_dict(orient='list')


DTYPE = {"int64": "Integer",
         "object": "String",
         "float64": "Real",
         "bool": "Boolean",
         "datetime64": "Date",
         "timedelta[ns]":None}


def pd_to_oms(type:str):
    raise NotImplementedError


def read_oms_table(filename:str) -> OmsTable:
    """ Read an OMS table from a file."""
    with open(filename) as f:
        tablematch = re.match(r"^\s*@[tT](able)?,\s*(.*)$", f.readline())
        tblheader = str(tablematch.groups(1)[1]) if tablematch is not None else "OMS Data Table"
        skip = 1

        # metadata
        metadata = {}
        colnames = None
        headers = None

        for line in f:
            if line.startswith(","):  # start of data
                break
            
            elif re.match("@[Hh](eader)?", line):
                _, *colnames = line.split(",")
                headers = [h.strip() for h in colnames]
                skip += 1
            
            else:
                try:
                    key, value = line.split(",")
                    metadata[key.strip()] = value.strip()
                except ValueError:
                    key, *values = line.split(",")
                    metadata[key.strip()] = [v.strip() for v in values]
                skip += 1
        
        data = pd.read_csv(filename, skiprows=skip, names=headers)
        data.reset_index(drop=True, inplace=True)
        headers = headers if headers is not None else [f"Column {i}" for i in range(len(data.columns))]

    t = OmsTable(data=data,
                 tblheader=tblheader,
                 metadata=metadata,
                 formats=metadata.pop("Format", []),
                 dtypes=metadata.pop("Type", []))

    return t


def write_oms(filename:str, 
              dates:"Union[pd.DatetimeIndex,list[datetime.datetime]]", 
              data:"np.ndarray",
              infer_dtypes:bool=True,
              ) -> None:
    """ Write data to an OMS table-formatted file.
    
    Parameters
    ----------
    filename : str
        Filename to write to.
    dates : Union[pd.DatetimeIndex,list[datetime]] 
        Datetime index or list of datetimes.
    data : np.ndarray
        Data to write, first dimension must match length of dates.
    """
    if not isinstance(dates, pd.DatetimeIndex):
        dates = pd.DatetimeIndex(dates)
    dates = dates.strftime("%Y-%m-%d %H:%M")

    names = [f"value_{i}" for i in range(data.shape[1])]
    df = pd.DataFrame(data=data, index=dates, columns=names)
    
    if infer_dtypes:
        dtypes = [DTYPE[str(t)] for t in df.dtypes]
    else:
        raise NotImplementedError
    
    formats = ["yyyy-MM-dd HH:mm"] + ["" for _ in range(data.shape[1])]
    ID = [""] + [str(i) for i in range(data.shape[1])]

    df.insert(0, "timestamp", dates)
    dtypes.insert(0, "Date")

    t = OmsTable(data=df,
                 tblheader="OMS Data Table",
                 formats=formats,
                 dtypes=dtypes,
                 metadata={"ID": ID})
    
    t.write(filename)
