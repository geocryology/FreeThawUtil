* Invalid table structure+

  
your table needs to have the following header (line order is important). This seems to differ slightly from the OMS / Geoframe documentation which seems to be more flexible in metadata order:
```
@T,tablename
@H,headers,
ID,,0
```
and needs to have `CRLF` line terminators


* ArrayIndexOutOfBoundsException

if this happens during `refineCloseToZeroIsotherm`, you may need to adjust your grid parameters or adjust KMAX in your sim file
