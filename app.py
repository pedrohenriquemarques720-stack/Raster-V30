import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
import time
import hashlib

# ============================================
# VERIFICAÇÃO DE BIBLIOTECAS OPCIONAIS
# ============================================
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import base64
    BASE64_AVAILABLE = True
except ImportError:
    BASE64_AVAILABLE = False
    # Implementação fallback do base64
    import binascii
    
    def base64_encode(data):
        if isinstance(data, str):
            data = data.encode()
        return binascii.b2a_base64(data).decode().strip()
    
    def base64_decode(data):
        return binascii.a2b_base64(data).decode()

# ============================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================
st.set_page_config(
    page_title="Rasther V29 - Gestão de Firmware",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# INICIALIZAÇÃO DO ESTADO DA SESSÃO
# ============================================
def init_session_state():
    """Inicializa todas as variáveis de estado da sessão"""
    
    if 'initialized' in st.session_state:
        return
    
    st.session_state.initialized = True
    st.session_state.page = "dashboard"
    
    # Dispositivos simulados
    st.session_state.devices = [
        {
            "id": "DEV-001",
            "nome": "Rasther V29 Pro",
            "serial": "RH-29-2024-1234",
            "versao": "v2.1.3",
            "hardware": "H7.2",
            "ultimo_acesso": datetime.now() - timedelta(hours=2),
            "status": "online",
            "bateria": 85,
            "sinal": 92,
            "cliente": "Oficina São João"
        },
        {
            "id": "DEV-002",
            "nome": "Rasther V29 Lite",
            "serial": "RH-29-2024-5678",
            "versao": "v2.0.9",
            "hardware": "H5.1",
            "ultimo_acesso": datetime.now() - timedelta(days=1),
            "status": "offline",
            "bateria": 0,
            "sinal": 0,
            "cliente": "Auto Mecânica Centro"
        },
        {
            "id": "DEV-003",
            "nome": "Rasther V29 Pro",
            "serial": "RH-29-2024-9012",
            "versao": "v2.1.5",
            "hardware": "H7.2",
            "ultimo_acesso": datetime.now() - timedelta(minutes=30),
            "status": "online",
            "bateria": 67,
            "sinal": 88,
            "cliente": "Concessionária Premium"
        }
    ]
    
    # Licenças simuladas
    st.session_state.licenses = [
        {
            "id": "LIC-2024-001",
            "cliente": "Oficina São João",
            "tipo": "Premium",
            "data_ativacao": "2024-01-15",
            "data_expiracao": "2025-12-31",
            "status": "ativa",
            "dispositivos": 1,
            "max_dispositivos": 3
        },
        {
            "id": "LIC-2024-002",
            "cliente": "Auto Mecânica Centro",
            "tipo": "Básico",
            "data_ativacao": "2024-02-01",
            "data_expiracao": "2024-12-31",
            "status": "ativa",
            "dispositivos": 1,
            "max_dispositivos": 1
        },
        {
            "id": "LIC-2024-003",
            "cliente": "Concessionária Premium",
            "tipo": "Enterprise",
            "data_ativacao": "2024-01-10",
            "data_expiracao": "2025-06-30",
            "status": "ativa",
            "dispositivos": 3,
            "max_dispositivos": 10
        }
    ]
    
    # Firmware disponíveis
    st.session_state.firmwares = {
        "v29": {
            "modelo": "V29 Pro",
            "versoes": [
                {
                    "versao": "v2.1.5",
                    "data": "2024-01-15",
                    "tamanho": 5242880,
                    "changelog": [
                        "Correção de bugs no protocolo CAN",
                        "Melhorias na estabilidade Bluetooth",
                        "Novos protocolos para veículos 2024",
                        "Otimização do consumo de bateria"
                    ],
                    "downloads": 1250,
                    "critica": False
                },
                {
                    "versao": "v2.1.3",
                    "data": "2023-12-10",
                    "tamanho": 4980736,
                    "changelog": [
                        "Suporte a novos veículos",
                        "Correções de segurança"
                    ],
                    "downloads": 3500,
                    "critica": True
                }
            ]
        },
        "v29lite": {
            "modelo": "V29 Lite",
            "versoes": [
                {
                    "versao": "v2.1.5",
                    "data": "2024-01-15",
                    "tamanho": 4194304,
                    "changelog": [
                        "Correção de bugs no protocolo CAN",
                        "Melhorias na estabilidade Bluetooth"
                    ],
                    "downloads": 850,
                    "critica": False
                }
            ]
        }
    }
    
    # Estatísticas
    st.session_state.stats = {
        "total_updates": 4850,
        "updates_hoje": 12,
        "dispositivos_online": 2,
        "dispositivos_total": 3,
        "licencas_ativas": 3,
        "usuarios_ativos": 42
    }
    
    # Logs do sistema
    st.session_state.logs = [
        {"timestamp": datetime.now() - timedelta(minutes=5), "mensagem": "Sistema iniciado", "tipo": "info"},
        {"timestamp": datetime.now() - timedelta(minutes=4), "mensagem": "Backup automático concluído", "tipo": "success"},
        {"timestamp": datetime.now() - timedelta(minutes=3), "mensagem": "Nova versão de firmware disponível", "tipo": "info"},
    ]

# Inicializar
init_session_state()

# ============================================
# FUNÇÕES AUXILIARES
# ============================================
def format_bytes(size):
    """Formata bytes para formato legível"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def get_status_color(status):
    """Retorna cor baseada no status"""
    colors = {
        "online": "green",
        "offline": "gray",
        "ativa": "green",
        "inativa": "red",
        "sucesso": "green",
        "falha": "red"
    }
    return colors.get(status, "blue")

def add_log(mensagem, tipo="info"):
    """Adiciona um log ao sistema"""
    st.session_state.logs.insert(0, {
        "timestamp": datetime.now(),
        "mensagem": mensagem,
        "tipo": tipo
    })
    if len(st.session_state.logs) > 50:
        st.session_state.logs.pop()

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px;">
        <h1 style="color: #3b82f6; font-size: 24px;">🔧 Rasther V29</h1>
        <p style="color: #94a3b8; font-size: 12px;">Gestão de Firmware</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Menu de navegação
    pages = {
        "📊 Dashboard": "dashboard",
        "📱 Dispositivos": "devices",
        "🔧 Firmware": "firmware",
        "🔑 Licenças": "licenses",
        "📈 Relatórios": "reports",
        "⚙️ Configurações": "settings"
    }
    
    for page_name, page_key in pages.items():
        if st.button(
            page_name,
            key=f"btn_{page_key}",
            use_container_width=True,
            type="primary" if st.session_state.page == page_key else "secondary"
        ):
            st.session_state.page = page_key
            st.rerun()
    
    st.markdown("---")
    
    # Status rápido
    st.markdown("### 📊 Status")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Dispositivos",
            f"{st.session_state.stats['dispositivos_online']}/{st.session_state.stats['dispositivos_total']}"
        )
    with col2:
        st.metric("Licenças", st.session_state.stats['licencas_ativas'])
    
    # Últimos logs
    with st.expander("📋 Logs Recentes"):
        for log in st.session_state.logs[:5]:
            st.caption(f"🕐 {log['timestamp'].strftime('%H:%M')}")
            st.caption(log['mensagem'])

# ============================================
# PÁGINA: DASHBOARD
# ============================================
def show_dashboard():
    st.title("📊 Dashboard")
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Total Atualizações",
            f"{st.session_state.stats['total_updates']:,}",
            f"+{st.session_state.stats['updates_hoje']} hoje"
        )
    with col2:
        st.metric(
            "Dispositivos Ativos",
            st.session_state.stats['dispositivos_online']
        )
    with col3:
        st.metric(
            "Licenças Ativas",
            st.session_state.stats['licencas_ativas']
        )
    with col4:
        st.metric(
            "Usuários Ativos",
            st.session_state.stats['usuarios_ativos']
        )
    
    # Gráficos simples
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Atualizações Recentes")
        dates = pd.date_range(end=datetime.now(), periods=7, freq='D')
        updates = np.random.randint(10, 50, size=7)
        chart_data = pd.DataFrame({
            'data': dates.strftime('%d/%m'),
            'atualizacoes': updates
        })
        st.bar_chart(chart_data.set_index('data'))
    
    with col2:
        st.subheader("Dispositivos por Versão")
        versions = ['v2.1.5', 'v2.1.3', 'v2.0.9']
        counts = [15, 42, 23]
        chart_data = pd.DataFrame({
            'versao': versions,
            'quantidade': counts
        })
        st.bar_chart(chart_data.set_index('versao'))
    
    # Tabela de dispositivos
    st.subheader("📱 Dispositivos Recentes")
    df = pd.DataFrame(st.session_state.devices)
    df['ultimo_acesso'] = pd.to_datetime(df['ultimo_acesso']).dt.strftime('%d/%m/%Y %H:%M')
    st.dataframe(
        df[['nome', 'serial', 'versao', 'ultimo_acesso', 'status']],
        use_container_width=True,
        hide_index=True
    )

# ============================================
# PÁGINA: DISPOSITIVOS
# ============================================
def show_devices():
    st.title("📱 Dispositivos")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Status", ["Todos", "Online", "Offline"])
    with col2:
        version_filter = st.selectbox("Versão", ["Todas", "v2.1.5", "v2.1.3", "v2.0.9"])
    with col3:
        search = st.text_input("Buscar", placeholder="Serial ou cliente...")
    
    # Aplicar filtros
    df = pd.DataFrame(st.session_state.devices)
    
    if status_filter != "Todos":
        df = df[df['status'] == status_filter.lower()]
    if version_filter != "Todas":
        df = df[df['versao'] == version_filter]
    if search:
        df = df[df['serial'].str.contains(search, case=False) | 
                df['cliente'].str.contains(search, case=False)]
    
    # Lista de dispositivos
    for _, device in df.iterrows():
        with st.container():
            cols = st.columns([2, 2, 1, 1, 1])
            with cols[0]:
                st.write(f"**{device['nome']}**")
                st.caption(device['serial'])
            with cols[1]:
                st.write(f"Cliente: {device['cliente']}")
                st.caption(f"Último: {pd.to_datetime(device['ultimo_acesso']).strftime('%d/%m/%Y')}")
            with cols[2]:
                st.write(f"Versão: {device['versao']}")
            with cols[3]:
                status_color = get_status_color(device['status'])
                st.markdown(f":{status_color}[{device['status'].upper()}]")
            with cols[4]:
                if st.button("📊", key=f"btn_{device['id']}"):
                    st.info(f"Detalhes de {device['serial']}")
            st.divider()

# ============================================
# PÁGINA: FIRMWARE
# ============================================
def show_firmware():
    st.title("🔧 Firmware")
    
    tab1, tab2 = st.tabs(["📦 Versões", "📤 Nova Versão"])
    
    with tab1:
        for modelo, data in st.session_state.firmwares.items():
            with st.expander(f"📱 {data['modelo']}", expanded=True):
                for versao in data['versoes']:
                    cols = st.columns([1, 3])
                    with cols[0]:
                        st.markdown(f"### {versao['versao']}")
                        if versao['critica']:
                            st.markdown("🔴 **CRÍTICA**")
                    with cols[1]:
                        st.write(f"📅 {versao['data']}")
                        st.write(f"📦 {format_bytes(versao['tamanho'])}")
                        st.write(f"📥 {versao['downloads']} downloads")
                        with st.expander("📋 Changelog"):
                            for item in versao['changelog']:
                                st.write(f"• {item}")
                    st.divider()
    
    with tab2:
        st.subheader("Publicar Nova Versão")
        
        col1, col2 = st.columns(2)
        with col1:
            versao = st.text_input("Versão", value="v2.1.6")
            data = st.date_input("Data de Lançamento")
        with col2:
            critica = st.checkbox("Atualização Crítica")
            arquivo = st.file_uploader("Arquivo do Firmware", type=['bin'])
        
        changelog = st.text_area(
            "Changelog",
            height=150,
            value="• Correções de segurança\n• Melhorias de performance"
        )
        
        if st.button("📤 Publicar", type="primary"):
            st.success("Nova versão publicada!")
            add_log(f"Nova versão {versao} publicada", "success")

# ============================================
# PÁGINA: LICENÇAS
# ============================================
def show_licenses():
    st.title("🔑 Licenças")
    
    # Estatísticas
    total = len(st.session_state.licenses)
    ativas = len([l for l in st.session_state.licenses if l['status'] == 'ativa'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total", total)
    with col2:
        st.metric("Ativas", ativas)
    with col3:
        st.metric("Taxa", f"{ativas/total*100:.0f}%")
    
    # Lista de licenças
    st.subheader("Licenças Ativas")
    
    for lic in st.session_state.licenses:
        cols = st.columns([2, 1, 1, 1])
        with cols[0]:
            st.write(f"**{lic['cliente']}**")
            st.caption(lic['id'])
        with cols[1]:
            st.write(f"Tipo: {lic['tipo']}")
        with cols[2]:
            exp_date = datetime.strptime(lic['data_expiracao'], '%Y-%m-%d')
            days = (exp_date - datetime.now()).days
            st.write(f"Expira: {days} dias")
        with cols[3]:
            status_color = get_status_color(lic['status'])
            st.markdown(f":{status_color}[{lic['status'].upper()}]")
        st.divider()
    
    # Nova licença
    with st.expander("➕ Nova Licença"):
        col1, col2 = st.columns(2)
        with col1:
            cliente = st.text_input("Cliente")
            codigo = st.text_input("Código")
        with col2:
            tipo = st.selectbox("Tipo", ["Básico", "Profissional", "Premium"])
            expiracao = st.date_input("Expiração")
        
        if st.button("✅ Ativar"):
            st.success(f"Licença ativada para {cliente}")

# ============================================
# PÁGINA: RELATÓRIOS
# ============================================
def show_reports():
    st.title("📈 Relatórios")
    
    # Período
    col1, col2 = st.columns(2)
    with col1:
        inicio = st.date_input("Início", datetime.now() - timedelta(days=30))
    with col2:
        fim = st.date_input("Fim", datetime.now())
    
    # Gráficos
    tab1, tab2 = st.tabs(["📊 Uso", "📥 Downloads"])
    
    with tab1:
        st.subheader("Atividades")
        dates = pd.date_range(start=inicio, end=fim, freq='D')
        data = pd.DataFrame({
            'data': dates,
            'atualizacoes': np.random.randint(5, 30, len(dates)),
            'dispositivos': np.random.randint(10, 50, len(dates))
        })
        st.line_chart(data.set_index('data'))
    
    with tab2:
        st.subheader("Downloads por Versão")
        downloads = pd.DataFrame({
            'versao': ['v2.1.5', 'v2.1.3', 'v2.0.9'],
            'downloads': [1250, 3500, 850]
        })
        st.bar_chart(downloads.set_index('versao'))
    
    if st.button("📥 Exportar PDF"):
        st.success("Relatório gerado!")

# ============================================
# PÁGINA: CONFIGURAÇÕES
# ============================================
def show_settings():
    st.title("⚙️ Configurações")
    
    tab1, tab2 = st.tabs(["🔧 Geral", "👥 Usuários"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Empresa", "Rasther Diagnostics")
            st.text_input("Email", "suporte@rasther.com")
        with col2:
            st.text_input("Servidor", "https://api.rasther.com")
            st.text_input("API Key", "••••••••", type="password")
        
        st.checkbox("Backup Automático", True)
        st.selectbox("Frequência", ["Diário", "Semanal", "Mensal"])
        
        if st.button("💾 Salvar"):
            st.success("Configurações salvas!")
            add_log("Configurações atualizadas", "success")
    
    with tab2:
        users = pd.DataFrame([
            {"nome": "Admin", "email": "admin@rasther.com", "tipo": "admin"},
            {"nome": "Suporte", "email": "suporte@rasther.com", "tipo": "suporte"},
        ])
        st.dataframe(users, use_container_width=True)

# ============================================
# ROTEAMENTO
# ============================================
pages = {
    "dashboard": show_dashboard,
    "devices": show_devices,
    "firmware": show_firmware,
    "licenses": show_licenses,
    "reports": show_reports,
    "settings": show_settings
}

# Executar página atual
pages[st.session_state.page]()

# ============================================
# RODAPÉ
# ============================================
st.markdown("---")
cols = st.columns(3)
with cols[0]:
    st.caption("Rasther V29 v1.0.0")
with cols[1]:
    st.caption(f"Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
with cols[2]:
    st.caption("© 2024 Rasther Diagnostics")
