import streamlit as st
import pdfplumber

def find_keyword_totals(pdf, keywords):
    matches = []
    total_sum = 0.0

    for page in pdf.pages:
        words = page.extract_words()
        lines = {}

        # Ryhmitellään sanat riveittäin y-koordinaatin mukaan (pyöristettynä)
        for w in words:
            y = round(w['top'])  # pyöristetään rivitasolle
            lines.setdefault(y, []).append(w)

        for y in sorted(lines.keys()):
            line_words = lines[y]
            line_text = " ".join(w['text'] for w in line_words).lower()

            for keyword in keywords:
                if keyword.lower() in line_text:
                    # Etsitään riviltä VAT 0 ja viimeinen hinta
                    for w in reversed(line_words):
                        text = w['text'].replace(",", ".").replace(" ", "")
                        if "0.00" in text or text.endswith("0%"):
                            continue  # ohitetaan VAT-arvo
                        try:
                            val = float(text)
                            matches.append((line_text.strip(), val))
                            total_sum += val
                            break
                        except:
                            continue

    return matches, total_sum

st.title("SR-O - Laskurivien poiminta v.1.0 ")

uploaded_file = st.file_uploader("Lataa PDF-lasku", type="pdf")
keywords_input = st.text_input("Syötä hakusanat (pilkulla eroteltuna, esim. Vuokra, Vakuutusmaksu):")
keywords = [k.strip().lower() for k in keywords_input.split(",") if k.strip()]

if uploaded_file and keywords:
    with pdfplumber.open(uploaded_file) as pdf:
        results, total = find_keyword_totals(pdf, keywords)

    if results:
        st.subheader("Löydetyt rivit:")
        for line, val in results:
            st.write(f"🔹 {line} → **{val:.2f} €**")
        st.success(f"**Yhteensä: {total:.2f} €**")
    else:
        st.warning("Ei löytynyt osumia.")

