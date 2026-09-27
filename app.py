import streamlit as st
import pandas as pd

# Konfiguration für mobile Ansicht
st.set_page_config(page_title="Bingo Live-Prüfer", page_icon="🎰", layout="centered")

st.markdown("<h2 style='text-align: center; font-size: 22px; margin-bottom: 20px;'>🎰 BINGO! Live-Prüfer</h2>", unsafe_allow_html=True)

# Speicher im Hintergrund anlegen
if "lose" not in st.session_state:
    st.session_state.lose = []
if "gezogene_zahlen" not in st.session_state:
    st.session_state.gezogene_zahlen = set()

tab1, tab2 = st.tabs(["📋 Meine Lose", "📺 Live-Ziehung & Abgleich"])

# ==========================================
# REITER 1: MANUELLE LOSEINGABE (PROFI-LOOK)
# ==========================================
with tab1:
    if len(st.session_state.lose) > 0:
        st.write("### 🗂️ Deine gespeicherten Lose")
        for idx, los in enumerate(st.session_state.lose):
            with st.expander(f"🎫 Los-Nr: {los['los_nr']} (Serie: {los['serien_nr']})"):
                df_visual = pd.DataFrame(los['matrix'], columns=["B", "I", "N", "G", "O"])
                st.table(df_visual)
        st.write("---")

    st.subheader("➕ Neues Los hinzufügen")
    
    col_ser, col_los = st.columns(2)
    with col_ser:
        serien_nr = st.text_input("Seriennummer", placeholder="z.B. 1109", key="sn_in")
    with col_los:
        los_nr = st.text_input("Losnummer", placeholder="z.B. 21416", key="ln_in")
        
    # Geniale Texteingabe: Schont die Nerven und spart Platz auf dem Handy!
    zahlen_text = st.text_area(
        "Trage die 25 Zahlen deines Loses ein (mit Komma getrennt):",
        placeholder="6, 20, 39, 47, 72, 7, 28, 40, 59, 64, ...",
        help="Einfach alle 25 Zahlen von links nach rechts, Reihe für Reihe eingeben."
    )
    
    if st.button("➕ Los jetzt speichern", use_container_width=True):
        if serien_nr and los_nr and zahlen_text:
            try:
                # Text in eine saubere Zahlenliste umwandeln
                rohe_zahlen = [int(z.strip()) for z in zahlen_text.split(",") if z.strip().isdigit()]
                
                if len(rohe_zahlen) != 25:
                    st.error(f"Ein Bingo-Los braucht genau 25 Zahlen! (Du hast {len(rohe_zahlen)} eingegeben)")
                else:
                    # Die 25 Zahlen in ein perfektes 5x5 Raster aufteilen
                    neue_matrix = [rohe_zahlen[i*5:(i+1)*5] for i in range(5)]
                    
                    st.session_state.lose.append({
                        "serien_nr": serien_nr,
                        "los_nr": los_nr,
                        "matrix": neue_matrix
                    })
                    st.success(f"🎉 Los {los_nr} erfolgreich gespeichert!")
                    st.rerun()
            except Exception as e:
                st.error("Fehler: Bitte trenne die Zahlen nur mit echten Kommas!")
        else:
            st.error("Bitte fülle die Seriennummer, Losnummer und alle Zahlen aus.")

# ==========================================
# REITER 2: LIVE-ZIEHUNG (PERFEKTE BUTTONS)
# ==========================================
with tab2:
    st.subheader("📺 Ziehungs-Spielfeld")
    
    # Grid-Hack für das Ziehungsfeld (Zwingt Buttons auf Handys nebeneinander)
    st.markdown("""
    <style>
        .board-container { display: grid; grid-template-columns: repeat(5, 1fr); gap: 2px; width: 100%; box-sizing: border-box; }
        .board-hdr { background: #1E88E5; color: white; text-align: center; font-weight: bold; padding: 4px 0; font-size: 13px; border-radius: 3px; }
        .mobile-btn { width: 100%; background: #f0f2f6; border: 1px solid #ccc; padding: 6px 0; font-size: 11px; font-weight: bold; text-align: center; border-radius: 4px; cursor: pointer; }
        .mobile-btn.active { background: #E53935 !important; color: white !important; border: none !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # Verarbeitet Klicks aus dem mobilen HTML-Feld unblockierbar via URL-Wechsel
    query = st.query_params
    if "z" in query:
        geklickte_zahl = int(query["z"])
        if geklickte_zahl in st.session_state.gezogene_zahlen:
            st.session_state.gezogene_zahlen.remove(geklickte_zahl)
        else:
            st.session_state.gezogene_zahlen.add(geklickte_zahl)
        st.query_params.clear()
        st.rerun()

    # Wir bauen das Spielfeld als reines HTML-Grid. Das passt sich IMMER zu 100% ohne Scrollen an!
    von_bis = [1, 16, 31, 46, 61]
    html_board = '<div class="board-container">'
    for b in ["B", "I", "N", "G", "O"]:
        html_board += f'<div class="board-hdr">{b}</div>'
        
    for r in range(15):
        for s in range(5):
            zahl = von_bis[s] + r
            ist_aktiv = zahl in st.session_state.gezogene_zahlen
            cls = "mobile-btn active" if ist_aktiv else "mobile-btn"
            label = f"🎯{zahl}" if ist_aktiv else str(zahl)
            html_board += f'<button class="{cls}" onclick="parent.location.href=\'?z={zahl}\'">{label}</button>'
    html_board += '</div>'
    
    components.html(html_board, height=530, scrolling=False)
    st.write("---")
    
    # LIVE-ABGLEICH DARUNTER
    if len(st.session_state.lose) == 0:
        st.warning("Füge im ersten Reiter Lose hinzu, um den Live-Abgleich zu sehen.")
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

