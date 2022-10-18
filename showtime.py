

import time
from datetime import datetime, timezone, timedelta

def main():
    s = time.time()
    GMT = timezone(timedelta(0),"GMT")
    print(f"time = {s}")
    print(f"time = {time.localtime()}")
    dt = datetime.now()
    print(f"time = {dt.now()}")
    print(f"time = {dt.tzinfo}")
    print(f"time = {datetime.now(tz=None)}")
    print(f"time = {datetime.now(tz=GMT)}")
    print(f"time = {datetime.now(tz=timezone.utc)}")
    
if __name__ == "__main__":
    main()
