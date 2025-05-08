import streamlit as st
import pdfplumber

st.title("PDF-laskun analysointi: VAT 0 -rivit ja summat")

uploaded_file = st.file_uploader("Lataa PDF-lasku", type="pdf")

keywords_input = st.text_input("Syötä hakusanat pilkulla eroteltuna (esim. Vakuutusmaksu, Vuokra):")
keywords = [k.strip().lower() for k in keywords_input.split(",") if k.strip()]

if uploaded_file and keywords:
    with pdfplumber.open(uploaded_file) as pdf:
        matches = []
        total_sum = 0.0

        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if not row or len(row) < 6:
                        continue
                    product = (row[1] or "").lower()
                    vat_pct = (row[4] or "").replace(" ", "")
                    price_str = (row[5] or "").replace(" ", "").replace(",", ".")
                    try:
                        price = float(price_str)
                    except:
                        continue

                    if any(kw in product for kw in keywords) and ("0.00" in vat_pct or "0%" in vat_pct.lower()):
                        matches.append((product, price))
                        total_sum += price

    if matches:
        st.markdown("### ✅ Löydetyt rivit:")
        for product, price in matches:
            st.write(f"- {product} → **{price:.2f} €**")
        st.success(f"**Yhteensä: {total_sum:.2f} €**")
    else:
        st.warning("Ei löytynyt osumia.")
