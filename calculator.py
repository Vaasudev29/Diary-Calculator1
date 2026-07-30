
import json
import os

class Calculator:
    def __init__(self, conversion_data_path='conversion_data.json', cost_data_path='cost_data.json'):
        # Construct full paths relative to the calculator.py file's directory
        self.conversion_data_path = os.path.join(os.path.dirname(__file__), conversion_data_path)
        self.cost_data_path = os.path.join(os.path.dirname(__file__), cost_data_path)
        self.conversions = {}
        self.units = {}
        self.costs = {}
        self._load_conversion_data()

    def _load_conversion_data(self):
        """Loads conversion factors, units, and costs from JSON files."""
        if not os.path.exists(self.conversion_data_path):
            raise FileNotFoundError(f"Conversion data file not found at: {self.conversion_data_path}")
        with open(self.conversion_data_path, 'r') as f:
            data = json.load(f)
            self.conversions = data.get('conversions', {})
            self.units = data.get('units', {})

        if not os.path.exists(self.cost_data_path):
            raise FileNotFoundError(f"Cost data file not found at: {self.cost_data_path}")
        with open(self.cost_data_path, 'r') as f:
            self.costs = json.load(f)

    def get_supported_products(self):
        """Returns a list of all products that can be used as input or output."""
        products = set(self.conversions.keys())
        for product_conversions in self.conversions.values():
            products.update(product_conversions.keys())
        return sorted(list(products))

    def get_product_unit(self, product_name):
        """Returns the default unit for a given product."""
        return self.units.get(product_name, 'unit') # Default to 'unit' if not specified

    def get_product_cost(self, product_name):
        """Returns the cost per unit for a given product."""
        return self.costs.get(product_name, 0.0) # Default to 0.0 if cost not specified

    def calculate_yield(self, input_product, input_quantity, level=0, max_level=3, current_path=None):
        """
        Calculates the yield of all possible downstream products, including multi-level conversions.
        max_level prevents infinite recursion for circular conversions (though not expected here).
        """
        if input_quantity <= 0:
            raise ValueError("Input quantity must be greater than zero.")

        if current_path is None:
            current_path = []

        if level > max_level:
            return {}

        results = {}
        direct_conversions = self.conversions.get(input_product, {})

        for output_product, factor in direct_conversions.items():
            yield_quantity = input_quantity * factor
            output_unit = self.get_product_unit(output_product)

            # Store direct conversion result
            # If product already exists, update with max quantity (useful if multiple paths lead to it)
            if output_product in results:
                if yield_quantity > results[output_product]['quantity']:
                    results[output_product] = {'quantity': yield_quantity, 'unit': output_unit}
            else:
                results[output_product] = {'quantity': yield_quantity, 'unit': output_unit}

            # Recursive call for multi-level conversions, avoiding cycles in the immediate path
            if output_product not in current_path:
                nested_results = self.calculate_yield(
                    output_product,
                    yield_quantity,
                    level=level + 1,
                    max_level=max_level,
                    current_path=current_path + [input_product]
                )
                # Merge nested results, prioritizing larger quantities
                for nested_product, nested_data in nested_results.items():
                    if nested_product in results:
                        if nested_data['quantity'] > results[nested_product]['quantity']:
                             results[nested_product] = nested_data
                    else:
                        results[nested_product] = nested_data

        return results

    def calculate_costs(self, input_product, input_quantity, yield_results):
        """
        Calculates the total cost of the input product and the total value of all yielded output products.
        """
        input_cost_per_unit = self.get_product_cost(input_product)
        total_input_cost = input_quantity * input_cost_per_unit

        total_output_value = 0.0
        for product, data in yield_results.items():
            output_cost_per_unit = self.get_product_cost(product)
            total_output_value += data['quantity'] * output_cost_per_unit

        return {
            'total_input_cost': total_input_cost,
            'total_output_value': total_output_value,
            'profit_loss': total_output_value - total_input_cost
        }
