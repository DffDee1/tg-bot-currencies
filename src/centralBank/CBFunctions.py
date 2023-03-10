import json
from fuzzywuzzy.fuzz import WRatio
import requests
import xmltodict


class NotFound(Exception):
    pass


async def get_all_currencies(url="https://cbr.ru/scripts/XML_daily.asp?date_req=") -> json:
    """
    Возвращает все валюты и значения
    """
    response = requests.get(url)
    values = xmltodict.parse(response.content)
    json.dumps(values, ensure_ascii=False)
    return values["ValCurs"]["Valute"]


async def get_currencies_by_name(currency) -> list:
    """
    На вход подается валюта(в виде "название валюты" или "код валюты")
    Ищем её среди всех валют
    На выходе может быть несколько валют
    Например, если это "доллар", на выходе будет канадский, американский и тд.
    """
    values = await get_all_currencies()
    final_values = []
    for val in values:
        if currency in ["ен", "ена", "йен", "йена", "иена"]:
            currency = "иен"
        if (WRatio(currency, val["Name"]) >= 80 or WRatio(currency[:len(currency)-1], val["Name"]) >= 80) or (currency.upper() == val["CharCode"]):
            val["Value"] = val["Value"].replace(',', '.')
            final_values.append(val)
    if len(final_values) > 0:
        return final_values
    else:
        raise NotFound


async def get_course(currency_to_swap, amount, user_currency_code: str) -> (float, int):
    """
    На вход подается валюта, курс которой надо узнать по отношению к пользовательской валюте
    Пользовательская валюта передается вторым параметром в виде "код валюты" (Например, "RUB")
    """
    swap_currency_val, swap_currency_nom = round(float(currency_to_swap["Value"]) * amount, 2), int(currency_to_swap["Nominal"])
    if user_currency_code == "RUB":
        return swap_currency_val, swap_currency_nom
    else:
        to_curr_val = await get_currencies_by_name(user_currency_code)
        to_curr_val = to_curr_val[0]
        return swap_currency_val * amount / round(float(to_curr_val["Value"]) / float(to_curr_val["Nominal"]), 2), swap_currency_nom


async def get_base_currencies() -> list:
    return [await get_currencies_by_name(curr) for curr in ['usd', 'eur', 'gbp', 'jpy', 'cny', 'kzt']]
