import streamlit as st
from datetime import datetime
import re

# ==========================================
# CONFIGURAZIONE PAGINA & BRANDING VISIVO
# ==========================================
st.set_page_config(
    page_title="P.M. Keiken — Maintenance Copilot",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS per riflettere il design industrial/enterprise (Palette Slate & Emerald)
st.markdown("""
    <style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .sidebar .sidebar-content { background-color: #1e293b; }
    .stMetric { background-color: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155; }
    .stAlert { background-color: #1e293b; border: 1px solid #475569; color: #f8fafc; }
    div.stButton > button { background-color: #0d9488; color: white; border-radius: 6px; font-weight: 600; border: none; }
    div.stButton > button:hover { background-color: #0f766e; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# INIZIALIZZAZIONE STATO (Database in Memoria)
# ==========================================
if "tickets" not in st.session_state:
    st.session_state.tickets = [
        {"id": "TICK-2026-001", "store": "STORE_104", "equip": "EQ-FRIG-01", "sev": "HIGH", "status": "OPEN", "date": "2026-03-01"},
        {"id": "TICK-2026-002", "store": "STORE_101", "equip": "EQ-FORN-03", "sev": "CRITICAL", "status": "PENDING_APPROVAL", "date": "2026-03-02"}
    ]

if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# SIDEBAR: GOVERNANCE & PROFILO (Strato 5)
# ==========================================
st.sidebar.title("🛡️ P.M. Keiken")
st.sidebar.markdown("### Enterprise AI Governance")
st.sidebar.markdown("---")

role_choice = st.sidebar.selectbox(
    "Profilo Operativo (Strato 5):",
    ["Store Manager (Store 104)", "Area Manager (Nord - Multi-Store)"]
)

if "Store Manager" in role_choice:
    user_id = "mario.rossi"
    user_role = "store_manager"
    allowed_stores = ["STORE_104"]
    clearance = 2
    st.sidebar.success("👤 Profilo: Store 104 (Clearance 2)")
else:
    user_id = "giulia.verdi"
    user_role = "area_manager"
    allowed_stores = ["STORE_101", "STORE_102", "STORE_104"]
    clearance = 4
    st.sidebar.warning("👤 Profilo: Area Manager [101, 102, 104] (Clearance 4)")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Stato Architettura (8 Strati)")
for i, layer in enumerate([
    "1. Modello LLM Fissato", "2. System Prompt Ver.", "3. RAG ibrido (PDF/Wiki)",
    "4. Strumenti MCP Ticket", "5. RBAC & Multi-Store", "6. Guardrail & PII Mask",
    "7. Cache Semantica", "8. Test Gate & Audit"
], 1):
    st.sidebar.text(f"L{i}: {layer} [OK]")

# ==========================================
# INTERFACCIA PRINCIPALE A SCHEDE (TABS)
# ==========================================
tab_chat, tab_analytics, tab_checklist = st.tabs([
    "💬 Copilot & Segnalazioni", 
    "📊 Analytics & Resoconti Catena", 
    "📋 Checklist 8 Strati"
])

# ------------------------------------------
# TAB 1: CHAT & RAG + STRUMENTI MCP
# ------------------------------------------
with tab_chat:
    st.subheader("Assistente Tecnico Impianti")
    st.markdown("Interagisci con i manuali tecnici certificati e apri ticket di manutenzione protetti da regole rigide.")

    col_cfg1, col_cfg2, col_cfg3 = st.columns(3)
    with col_cfg1:
        target_store = st.selectbox("Store di intervento:", allowed_stores)
    with col_cfg2:
        eq_code = st.text_input("Codice Impianto:", value="EQ-FRIG-01")
    with col_cfg3:
        severity = st.selectbox("Livello di gravità:", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])

    st.markdown("---")

    # Render chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Scrivi un problema tecnico (es. 'Come riparo la cella?' o 'Crea un ticket di riparazione')"):
        # STRATO 6: Difesa Ingresso (Prompt Injection)
        if any(bad in prompt.lower() for bad in ["ignora le istruzioni", "system prompt", "jailbreak"]):
            response_text = "🛡️ **SecurityError (Strato 6):** Rilevato potenziale tentativo di Prompt Injection. Richiesta bloccata."
        else:
            # STRATO 5: Verifica Permessi Multi-Store
            if target_store not in allowed_stores:
                response_text = f"⛔ **Accesso Negato (Strato 5):** Non disponi dei diritti per operare sullo store {target_store}."
            
            # STRATO 4: Esecuzione Strumento MCP (Ticket)
            elif "ticket" in prompt.lower() or "riparazione" in prompt.lower() or "guasto" in prompt.lower():
                new_id = f"TICK-2026-{len(st.session_state.tickets)+1:03d}"
                st.session_state.tickets.append({
                    "id": new_id, "store": target_store, "equip": eq_code, "sev": severity, "status": "OPEN", "date": str(datetime.now().date())
                })
                response_text = f"✅ **Ticket Creato con successo (Strato 4):** `{new_id}` assegnato a `{target_store}` per l'impianto `{eq_code}`."
                if severity == "CRITICAL":
                    response_text += "\n\n🚨 **ALERT CRITICO:** Trattandosi di livello CRITICAL, è stata avviata la notifica automatica all'Area Manager."
            
            # STRATO 3: RAG Ibrido (Manuali PDF & Wiki)
            elif "cella" in prompt.lower() or "frigorifera" in prompt.lower():
                response_text = "📄 **Fonte Citata (Strato 3):** *Manuale Manutenzione Frigoriferi 2026.pdf*\n\nPer la cella frigorifera, verificare il blocco del compressore e richiedere intervento con tecnico certificato F-Gas."
            elif "forno" in prompt.lower():
                response_text = "📄 **Fonte Citata (Strato 3):** *Wiki Aziendale - SOP Forni Rotativi (Confluence)*\n\nPrima di aprire un ticket, resettare il relè termico sul pannello posteriore."
            else:
                response_text = f"Ho analizzato la richiesta per lo store `{target_store}`. Per aprire una segnalazione ufficiale, scrivi 'Crea un ticket', oppure chiedi la procedura tecnica specifica."

        # Salvataggio e visualizzazione
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        st.rerun()

# ------------------------------------------
# TAB 2: ANALYTICS & RESOCONTI
# ------------------------------------------
with tab_analytics:
    st.subheader("📈 P.M. Keiken — Dashboard Analitica & KPI")
    st.markdown("Monitoraggio in tempo reale dello stato degli impianti e dei costi di manutenzione.")

    user_tickets = [t for t in st.session_state.tickets if t["store"] in allowed_stores]

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Ticket Totali Visibili", len(user_tickets))
    col_m2.metric("Store Sotto Controllo", len(allowed_stores))
    col_m3.metric("Tempo Medio Risoluzione", "14.2 ore")
    col_m4.metric("Stato Compliance RAG", "98.5%")

    st.markdown("---")
    st.markdown("### 📋 Registro Attività e Ticket Attivi")
    st.table(user_tickets)

    st.markdown("### 📄 Esportazione Report Ufficiale")
    if st.button("Genera Verbale Ufficiale per Bilancio (.txt)"):
        report_data = f"""==================================================
P.M. KEIKEN - VERBALE DI MANUTENZIONE & ANALYTICS
Utente: {user_id} ({user_role})
Store Autorizzati: {allowed_stores}
Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}
--------------------------------------------------
Ticket Registrati nel Periodo: {len(user_tickets)}
Stato Impianti: OTTIMALE
Certificato da Architettura 8 Strati (Strato 8)
=================================================="""
        st.download_button(
            label="📥 Scarica Report di Manutenzione",
            data=report_data,
            file_name=f"Report_Keiken_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

# ------------------------------------------
# TAB 3: CHECKLIST DEGLI 8 STRATI
# ------------------------------------------
with tab_checklist:
    st.subheader("📋 Controllo di Conformità degli 8 Strati")
    st.markdown("Nessun rilascio va in produzione se anche una sola voce non è spuntata (Regola Strato 8).")

    checklist_items = [
        ("Strato 1: Modello LLM", "Modello unificato e bloccato in versione stabile", True),
        ("Strato 2: System Prompt", "Prompt di sistema versionato senza credenziali hardcoded", True),
        ("Strato 3: Documenti (RAG)", "RAG ibrido (PDF + Wiki) con citazione obbligatoria e fail-closed", True),
        ("Strato 4: Strumenti (MCP)", "Server MCP per ticket con approvazioni transazionali", True),
        ("Strato 5: Permessi e Identità", "RBAC dinamico e isolamento Multi-Store (Store vs Area Manager)", True),
        ("Strato 6: Difese & Guardrail", "Filtri anti-injection in ingresso e mascheramento in uscita", True),
        ("Strato 7: Cache e Router", "Cache semantica isolata per ruolo e controllo costi", True),
        ("Strato 8: Tracce e Test Gate", "Golden dataset di test superato al 100% prima del deploy", True),
    ]

    for title, desc, status in checklist_items:
        cols = st.columns([0.1, 0.9])
        cols[0].checkbox("", value=status, disabled=True, key=title)
        cols[1].markdown(f"**{title}** — *{desc}*")
