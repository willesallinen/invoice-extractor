import streamlit as st
import pdfplumber
import re

st.title('Laskurivien poiminta')

uploaded_file = st.file_uploader("Valitse PDF-lasku", type="pdf")

keywords_input = st.text_input("Syötä haettavat sanat pilkulla eroteltuna (esim. Vakuutusmaksu, Vuokra):")
keywords = [kw.strip() for kw in keywords_input.split(",") if kw.strip()]

if uploaded_file and keywords:
    with pdfplumber.open(uploaded_file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    st.subheader("Tulokset:")
    results = []
    for keyword in keywords:
        pattern = rf"({re.escape(keyword)}.*?)(\d+[\.,]?\d*)"
        matches = re.findall(pattern, text)
        for match in matches:
            results.append((match[0].strip(), match[1]))

    if results:
        for rivi, summa in results:
            st.write(f"🔎 **{rivi}** – **{summa}**")
    else:
        st.write("Ei löytynyt osumia hakusanoilla.")
