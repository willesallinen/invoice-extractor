import streamlit as st
import pdfplumber
import re

st.title('Laskurivien poiminta ja yhteissummat (VAT 0%)')

uploaded_file = st.file_uploader("Valitse PDF-lasku", type="pdf")

keywords_input = st.text_input("Syötä haettavat sanat pilkulla eroteltuna (esim. Vakuutusmaksu, Vuokra):")
keywords = [kw.strip().lower() for kw in keywords_input.split(",") if kw.strip()]

if uploaded_file and keywords:
    with pdfplumber.open(uploaded_file) as pdf:
        lines = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines.extend(text.splitlines())

    st.subheader("Tulokset:")

    for keyword in keywords:
        st.markdown(f"### 🔍 {keyword.upper()}")
        total = 0.0
        found_lines = []

        for i, line in enumerate(lines):
            if keyword in line.lower():
                # Katsotaan seuraavat rivit mukaan (hinta löytyy usein seuraavalta riviltä)
                context = " ".join(lines[i:i+3])

                # Etsitään VAT 0% merkintä riviltä
                if re.search(r"0\.00|0,00", context) and re.search(r'VAT\s*0|ALV\s*0|0%', context, re.IGNORECASE):
                    # Poimitaan numerot summamuodossa
                    sums = re.findall(r'\d{1,3}(?:[\s\u202f]?\d{3})*[.,]\d{2}', context)
                    if sums:
                        last_sum = sums[-1].replace(" ", "").replace(u'\u202f', '').replace(",", ".")
                        try:
                            value = float(last_sum)
                            total += value
                            found_lines.append((context.strip(), value))
                        except:
                            pass

        if found_lines:
            for ctx, val in found_lines:
                st.write(f"🔹 {ctx} → **{val:.2f} €**")
            st.success(f"**Yhteensä (VAT 0%) hakusanalla '{keyword}': {total:.2f} €**")
        else:
            st.warning(f"Ei löytynyt hakusanalla '{keyword}' ja VAT 0%.")
