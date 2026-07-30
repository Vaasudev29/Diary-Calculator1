
import streamlit as st
import pandas as pd
from calculator import Calculator
from utils import export_to_excel, export_to_pdf
import os

# Initialize the calculator
# Adjust path if running locally from a different directory than the main script
calculator = Calculator(conversion_data_path='conversion_data.json', cost_data_path='cost_data.json')

def main():
    st.set_page_config(layout="centered", page_title="Dairy Product Yield Calculator")

    st.title("🥛 Dairy Product Yield Calculator")

    st.markdown("--- Say Cheese! ---", unsafe_allow_html=True)

    # Get supported products from the calculator
    products = calculator.get_supported_products()

    # UI for input
    col1, col2, col3 = st.columns([3, 2, 1])

    with col1:
        input_product = st.selectbox("Select Input Product", products, index=products.index("Milk"))

    default_unit = calculator.get_product_unit(input_product)

    with col2:
        input_quantity = st.number_input("Quantity", min_value=0.0, value=100.0, step=0.1)

    with col3:
        st.markdown(f"<div style='padding-top: 27px; font-weight: bold;'>{default_unit}</div>", unsafe_allow_html=True)

    st.markdown("&nbsp;") # Spacer

    if st.button("Calculate Yield", type="primary"):
        if input_quantity <= 0:
            st.warning("Please enter a quantity greater than zero.")
            return

        st.subheader(f"Results for {input_quantity:.2f} {default_unit} of {input_product}")

        # Perform calculation
        yield_results = calculator.calculate_yield(input_product, input_quantity)
        cost_results = calculator.calculate_costs(input_product, input_quantity, yield_results)

        if not yield_results:
            st.info(f"No direct or multi-level conversions found for {input_product}.")
            return

        # Prepare data for display and export
        results_data = []
        for product, data in yield_results.items():
            results_data.append({
                "Product": product,
                "Quantity": f"{data['quantity']:.2f}",
                "Unit": data['unit']
            })

        # Sort results alphabetically by product name
        results_data_sorted = sorted(results_data, key=lambda x: x['Product'])

        # Display results in a DataFrame (table)
        st.dataframe(pd.DataFrame(results_data_sorted), hide_index=True, use_container_width=True)

        st.subheader("Cost Analysis")
        col_cost1, col_cost2, col_cost3 = st.columns(3)
        with col_cost1:
            st.metric(label="Total Input Cost", value=f"${cost_results['total_input_cost']:.2f}")
        with col_cost2:
            st.metric(label="Total Output Value", value=f"${cost_results['total_output_value']:.2f}")
        with col_cost3:
            st.metric(label="Profit/Loss", value=f"${cost_results['profit_loss']:.2f}")

        # Export buttons
        col_export1, col_export2 = st.columns(2)
        with col_export1:
            excel_data = export_to_excel(results_data_sorted, cost_results) # Pass cost_results here
            if excel_data:
                st.download_button(
                    label="Export to Excel",
                    data=excel_data,
                    file_name="dairy_yield_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        with col_export2:
            pdf_data = export_to_pdf(input_product, input_quantity, default_unit, results_data_sorted, cost_results) # Pass cost_results here
            if pdf_data:
                st.download_button(
                    label="Export to PDF",
                    data=pdf_data,
                    file_name="dairy_yield_report.pdf",
                    mime="application/pdf"
                )

    st.markdown("---", unsafe_allow_html=True)
    st.caption("Developed with Streamlit by your AI assistant")

if __name__ == "__main__":
    main()
