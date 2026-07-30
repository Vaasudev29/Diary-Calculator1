
import json
import os
# import requests # Uncomment if live API fetching is implemented later

class CurrencyConverter:
    def __init__(self, settings_file_path='currency_settings.json'):
        self.base_currency = 'INR' # Base currency for internal calculations
        self.default_display_currency = 'USD'
        self.settings_file_path = os.path.join(os.path.dirname(__file__), settings_file_path)
        self.exchange_rates = { # Default exchange rates relative to INR
            'INR': 1.0, # Base currency
            'USD': 0.012, # 1 INR = 0.012 USD (approx)
            'EUR': 0.011, # 1 INR = 0.011 EUR (approx)
            'GBP': 0.0094, # 1 INR = 0.0094 GBP (approx)
            'AUD': 0.018, # 1 INR = 0.018 AUD (approx)
            'CAD': 0.017, # 1 INR = 0.017 CAD (approx)
        }
        self.currency_symbols = {
            'INR': '₹',
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'AUD': '$',
            'CAD': '$',
        }
        self._load_settings()

    def _load_settings(self):
        """Loads currency settings from a JSON file."""
        if os.path.exists(self.settings_file_path):
            with open(self.settings_file_path, 'r') as f:
                settings = json.load(f)
                self.exchange_rates.update(settings.get('exchange_rates', {}))
                self.default_display_currency = settings.get('default_display_currency', self.default_display_currency)
                self.base_currency = settings.get('base_currency', self.base_currency)
        else:
            self._save_settings() # Save default settings if file doesn't exist

    def _save_settings(self):
        """Saves current currency settings to a JSON file."""
        settings = {
            'base_currency': self.base_currency,
            'default_display_currency': self.default_display_currency,
            'exchange_rates': self.exchange_rates,
        }
        with open(self.settings_file_path, 'w') as f:
            json.dump(settings, f, indent=4)

    def get_available_currencies(self):
        """Returns a list of all available currency codes."""
        return sorted(list(self.exchange_rates.keys()))

    def get_exchange_rate(self, target_currency):
        """Returns the exchange rate from the base currency to the target currency."""
        return self.exchange_rates.get(target_currency, 0.0) # Default to 0 if not found

    def get_currency_symbol(self, currency_code):
        """Returns the symbol for a given currency code."""
        return self.currency_symbols.get(currency_code, '')

    def set_exchange_rate(self, currency_code, rate):
        """Sets a custom exchange rate for a given currency code."""
        if currency_code in self.exchange_rates:
            self.exchange_rates[currency_code] = rate
            self._save_settings()
            return True
        return False

    def set_default_display_currency(self, currency_code):
        """Sets the default display currency."""
        if currency_code in self.exchange_rates:
            self.default_display_currency = currency_code
            self._save_settings()
            return True
        return False

    def convert_from_base(self, amount_in_base, target_currency):
        """Converts an amount from the base currency to the target currency."""
        rate = self.get_exchange_rate(target_currency)
        return amount_in_base * rate

    def fetch_live_exchange_rates(self, api_key=None): # Placeholder for future API integration
        """Fetches live exchange rates from an external API (placeholder)."""
        # This method would typically make an API call to a service like Open Exchange Rates,
        # ExchangeRate-API, etc., and update self.exchange_rates.
        # For now, it will use the default rates or manually set rates.
        print("Live exchange rate fetching is a premium feature and requires API integration.")
        print("Using predefined or manually set exchange rates.")
        # Example of how you might update rates (simplified):
        # if api_key:
        #     try:
        #         response = requests.get(f"https://api.exchangeratesapi.io/latest?base={self.base_currency}&symbols=USD,EUR", params={'access_key': api_key})
        #         data = response.json()
        #         if 'rates' in data:
        #             for currency, rate in data['rates'].items():
        #                 self.exchange_rates[currency] = rate
        #             self._save_settings()
        #             return True
        #     except Exception as e:
        #         print(f"Error fetching live rates: {e}")
        return False
