# Linkpy - Access your Linky data via Python
## What is this?
This Python 3 library allows you to retrieve your Linky power consumption data
without any hardware, just a connection to your Enedis account.

This module was previously part of Linkindle and was extracted for better 
modularity and easier usage.

## How to install
```bash
pip3 install linkpy
```

## Help, it's not working!
1. First, check that the Enedis website itself is working.
2. You might need to accept updated terms and conditions on the website. Linkpy won't work until you do.
3. Check that you have the latest version of this package. As Enedis changes its website, stuff can and occasionally does break.
4. If everything else fails, you can [report an issue](https://github.com/outadoc/linkindle/issues). I'll try to get to it on my free time, but contributions are welcome!

## How to use
```python
from linkpy import Linky, LinkyLoginException, LinkyServiceException

try:
    linky = Linky()
    linky.login(USERNAME, PASSWORD)

    today = datetime.date.today()
    res_year = linky.get_data_per_year()

    # 6 months ago - today
    res_month = linky.get_data_per_month(dtostr(
        today - relativedelta(months=6)), dtostr(today))

    # One month ago - yesterday
    res_day = linky.get_data_per_day(
                dtostr(today - relativedelta(days=1, months=1)),
                dtostr(today - relativedelta(days=1)))

    # Yesterday - today
    res_hour = linky.get_data_per_hour(
                dtostr(today - relativedelta(days=1)), 
                dtostr(today))
except LinkyLoginException as exc:
    logging.error(exc)

except LinkyServiceException as exc:
    logging.error(exc)
```

## Example
See my [Linkindle project](https://github.com/outadoc/linkindle) for a real-life
example. 
