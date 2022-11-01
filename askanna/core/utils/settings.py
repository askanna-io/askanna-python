import collections

StorageUnit = collections.namedtuple("StorageUnit", ["B", "KiB", "MiB", "GiB", "TiB", "PiB"])

diskunit = StorageUnit(B=1, KiB=1024**1, MiB=1024**2, GiB=1024**3, TiB=1024**4, PiB=1024**5)
