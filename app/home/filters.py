from app.home import blueprint
from datetime import datetime
from currency_symbols import CurrencySymbols

@blueprint.app_template_filter('currency_symbol')
def currency_symbol(currency_code):
    return CurrencySymbols.get_symbol(currency_code)

@blueprint.context_processor
def utility_processor():
    def currency_symbol(currency_code):
        return CurrencySymbols.get_symbol(currency_code)
    return dict(currency_symbol=currency_symbol)

@blueprint.app_template_filter('timestamp')
def convert_ts(ts):
    date = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d')
    return date