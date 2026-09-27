import streamlit as st
import pandas as pd

# Konfiguration für mobile Ansicht
st.set_page_config(page_title="Bingo Live-Prüfer", page_icon="🎰", layout="centered")

# DER DEFINITIVE MOBIL-HACK: Zwingt echte Streamlit-Elemente ohne Scrollen aufs Handy
st.markdown("""
<style>
    /* Spalten-Blöcke bilden eine feste horizontale Reihe ohne Umbruch */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 2px !important;
        width: 100% !important;
    }
    /* Teilt die Spalten mathematisch exakt auf 5 gleich große Stücke (je 20%) auf */
    [data-testid="column"] {
        flex: 1 1 0% !important;
        min-width: 0px !important;
        width: 20% !important;
    }
    /* Macht die echten Streamlit-Eingabefelder super schmal fürs Handy */
    [data-testid="column"] input {
        padding: 4px 1px !important;
        font-size: 13px !important;
        text-align: center !important;
        height: 34px !important;
        box-sizing: border-box !important;
    }
    /* Macht die echten Streamlit-Ziehungsbuttons flach und fingerfreundlich */
    [data-testid="column"] button {
        padding: 4px 1px !important;
        font-size: 11px !important;
        height: 28px !important;
        margin: 1px 0px !important;
        width: 100% !important;
    }
    /* Entfernt die Pfeile in den Zahlenfeldern für maximalen Platz */
    input[type=number]::-webkit-inner-spin-button, 
    input[type=number]::-webkit-outer-spin-button { 
        -webkit-appearance: none; 
        margin: 0; 
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='font-size: 24px; text-align: center; margin-bottom: 25px;'>🎰 BINGO! Live-Prüfer</h2>", unsafe_allow_html=True)

# Speicher für die Lose und gezogenen Zahlen im Hintergrund
if "lose" not in st.session_state:
    st.session_state.lose = []
if "gezogene_zahlen" not in st.session_state:
    st.session_state.gezogene_zahlen = set()

tab1, tab2 = st.tabs(["📋 Meine Lose", "📺 Live-Ziehung & Abgleich"])

# ==========================================
# REITER 1: MEINE LOSE (Eintragen & Speichern)
# ==========================================
with tab1:
    if len(st.session_state.lose) > 0:
        st.write("### 🗂️ Deine gespeicherten Lose")
        for idx, los in enumerate(st.session_state.lose):
            with st.expander(f"🎫 Los-Nr: {los['los_nr']} (Serie: {los['serien_nr']})"):
                df_visual = pd.DataFrame(los['matrix'], columns=["B", "I", "N", "G", "O"])
                st.table(df_visual)
        st.write("---")
    else:
        st.info("Noch keine Lose gespeichert. Trage unten dein erstes Los ein!")

    st.subheader("➕ Neues Los hinzufügen")
    
    col_ser, col_los = st.columns(2)
    with col_ser:
        serien_nr = st.text_input("Seriennummer", placeholder="z.B. 1109", key="ser_input")
    with col_los:
        los_nr = st.text_input("Losnummer", placeholder="z.B. 21416", key="los_input")
        
    st.write("**Die 25 Zahlen des Spielfelds (5x5 Raster):**")
    
    cols_header = st.columns(5)
    for idx, b in enumerate(["B", "I", "N", "G", "O"]):
        cols_header[idx].markdown(f"<p style='text-align: center; font-weight: bold; background: #f0f2f6; margin: 0; padding: 2px 0; border-radius: 4px;'>{b}</p>", unsafe_allow_html=True)
    
    matrix = []
    for i in range(5):
        cols = st.columns(5)
        row_values = []
        for j in range(5):
            val = cols[j].number_input(
                f"R{i}S{j}", min_value=1, max_value=75, value=1, 
                key=f"cell_{i}_{j}", label_visibility="collapsed"
            )
            row_values.append(val)
        matrix.append(row_values)
        
    if st.button("➕ Los jetzt speichern", use_container_width=True, key="save_los_btn"):
        if serien_nr and los_nr:
            st.session_state.lose.append({
                "serien_nr": serien_nr,
                "los_nr": los_nr,
                "matrix": matrix
            })
            st.success(f"🎉 Los {los_nr} erfolgreich gespeichert!")
            st.rerun()
        else:
            st.error("Bitte Serien- und Losnummer eingeben.")

# ==========================================
# REITER 2: LIVE-ZIEHUNG & BINGO-PRÜFUNG
# ==========================================
with tab2:
    st.subheader("📺 Ziehungs-Spielfeld")
    st.write("Klicke auf die Zahlen, um sie zu markieren:")
    
    buchstaben = ["B", "I", "N", "G", "O"]
    # Startwerte für die 5 Bingo-Spalten (1, 16, 31, 46, 61)
    von_bis = [1, 16, 31, 46, 61]
    
    cols_board = st.columns(5)
    for spalte_idx in range(5):
        with cols_board[spalte_idx]:
            st.markdown(f"<p style='text-align: center; font-weight: bold; color: white; background-color: #1E88E5; margin: 0; padding: 4px 0; border-radius: 4px; font-size: 14px;'>{buchstaben[spalte_idx]}</p>", unsafe_allow_html=True)
            
            start_wert = von_bis[spalte_idx]
            for zeile in range(15):
                zahl = start_wert + zeile
                ist_aktiv = zahl in st.session_state.gezogene_zahlen
                
                btn_label = f"🎯 {zahl}" if ist_aktiv else f"{zahl}"
                btn_type = "primary" if ist_aktiv else "secondary"
                
                if st.button(btn_label, key=f"native_btn_{zahl}", type=btn_type, use_container_width=True):
                    if ist_aktiv:
                        st.session_state.gezogene_zahlen.remove(zahl)
                    else:
                        st.session_state.gezogene_zahlen.add(zahl)
                    st.rerun()

    st.write("---")
    
    if len(st.session_state.lose) == 0:
        st.warning("Hinzugefügte Lose werden hier live abgeglichen.")
    else:
        st.write("### 🔍 Live-Abgleich deiner Lose:")
        for los in st.session_state.lose:
            mat = los['matrix']
            
            z_treffer = [0, 0, 0, 0, 0]
            s_treffer = [0, 0, 0, 0, 0]
            d1_treffer, d2_treffer = 0, 0
            
            display_matrix = []
            for i in range(5):
                row_display = []
                for j in range(5):
                    zahl = mat[i][j]
                    ist_gezogen = zahl in st.session_state.gezogene_zahlen
                    
                    if ist_gezogen:
                        row_display.append(f"✅ {zahl}")
                        z_treffer[i] += 1
                        s_treffer[j] += 1
                        if i == j: d1_treffer += 1
                        if i + j == 4: d2_treffer += 1
                    else:
                        row_display.append(f"❌ {zahl}")
                display_matrix.append(row_display)
            
            hat_bingo = (5 in z_treffer) or (5 in s_treffer) or (d1_treffer == 5) or (d2_treffer == 5)
            
            st.markdown(f"**🎫 Los {los['los_nr']} (Serie: {los['serien_nr']})**")
            df = pd.DataFrame(display_matrix, columns=["B", "I", "N", "G", "O"])
            st.table(df)
            
            if hat_bingo:
                st.balloons()
                st.success(f"🚨🚨 BINGO!!! Herzlichen Glückwunsch bei Los {los['los_nr']}! 🚨🚨")
