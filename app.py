import streamlit as st
import pandas as pd
import numpy as np
import json
import hashlib
import time
import random
from datetime import datetime, timedelta
import base64

# ============================================
# VERIFICAÇÃO DE BIBLIOTECAS
# ============================================
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("⚠️ Plotly não disponível. Usando gráficos alternativos.")

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
# ESTADO DA SESSÃO (Simula banco de dados)
# ============================================
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    
    # Dispositivos
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
    
    # Licenças
    st.session_state.licenses = [
        {
            "id": "LIC-2024-001",
            "cliente": "Oficina São João",
            "tipo": "Premium",
            "data_ativacao": "2024-01-15",
            "data_expiracao": "2025-12-31",
            "status": "ativa",
            "features": ["updates", "premium", "suporte", "diagnostico"],
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
            "features": ["updates", "suporte_basico"],
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
            "features": ["updates", "premium", "suporte_24h", "api", "multiusuario"],
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
    
    # Histórico de atualizações
    st.session_state.update_history = []
    for i in range(20):
        date = datetime.now() - timedelta(days=random.randint(0, 30))
        st.session_state.update_history.append({
            "data": date,
            "dispositivo": random.choice(st.session_state.devices)["serial"],
            "versao_anterior": f"v2.1.{random.randint(0,3)}",
            "versao_nova": f"v2.1.{random.randint(3,5)}",
            "status": random.choice(["sucesso", "sucesso", "sucesso", "falha"]),
            "duracao": random.randint(60, 180)
        })
    
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
        {"timestamp": datetime.now() - timedelta(minutes=2), "mensagem": "Licença LIC-2024-001 renovada", "tipo": "success"},
        {"timestamp": datetime.now() - timedelta(minutes=1), "mensagem": "Dispositivo DEV-001 conectado", "tipo": "info"},
    ]

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
        "ativo": "green",
        "inativo": "red",
        "sucesso": "green",
        "falha": "red",
        "pendente": "orange"
    }
    return colors.get(status, "blue")

def add_log(mensagem, tipo="info"):
    """Adiciona um log ao sistema"""
    st.session_state.logs.insert(0, {
        "timestamp": datetime.now(),
        "mensagem": mensagem,
        "tipo": tipo
    })
    # Manter apenas últimos 100 logs
    if len(st.session_state.logs) > 100:
        st.session_state.logs.pop()

def create_bar_chart(data, labels, title):
    """Cria gráfico de barras sem plotly"""
    chart_data = pd.DataFrame({
        'labels': labels,
        'values': data
    })
    st.bar_chart(chart_data.set_index('labels'))

def create_line_chart(dates, values, title):
    """Cria gráfico de linhas sem plotly"""
    chart_data = pd.DataFrame({
        'date': dates,
        'value': values
    })
    st.line_chart(chart_data.set_index('date'))

# ============================================
# CARREGAR HTML
# ============================================
def load_html():
    """Carrega o arquivo HTML e injeta dados do Streamlit"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
            
        # Injetar dados do Streamlit no HTML
        html_content = html_content.replace(
            '</body>',
            f'''
            <script>
                // Dados injetados pelo Streamlit
                window.streamlitData = {json.dumps({
                    "devices": st.session_state.devices,
                    "licenses": st.session_state.licenses,
                    "stats": st.session_state.stats,
                    "logs": [
                        {{
                            "time": log["timestamp"].strftime("%H:%M:%S"),
                            "message": log["mensagem"],
                            "type": log["tipo"]
                        }} for log in st.session_state.logs[:10]
                    ]
                })};
                
                // Função para comunicação com Streamlit
                function sendToStreamlit(data) {{
                    if (window.Streamlit) {{
                        window.Streamlit.setComponentValue(data);
                    }}
                }}
            </script>
            </body>
            ''',
            html_content
        )
        
        return html_content
    except FileNotFoundError:
        st.error("Arquivo index.html não encontrado!")
        return None

# ============================================
# SIDEBAR - NAVEGAÇÃO
# ============================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px;">
        <h1 style="color: #3b82f6;">🔧 Rasther V29</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Menu de navegação
    menu_option = st.radio(
        "Navegação",
        ["📊 Dashboard", "📱 Dispositivos", "🔧 Firmware", "🔑 Licenças", "📈 Relatórios", "⚙️ Configurações"],
        index=0
    )
    
    st.markdown("---")
    
    # Status rápido
    st.markdown("### 📊 Status do Sistema")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Dispositivos", f"{st.session_state.stats['dispositivos_online']}/{st.session_state.stats['dispositivos_total']}")
    with col2:
        st.metric("Licenças", st.session_state.stats['licencas_ativas'])
    
    # Últimos logs
    st.markdown("### 📋 Últimos Logs")
    for log in st.session_state.logs[:3]:
        st.caption(f"🕐 {log['timestamp'].strftime('%H:%M:%S')}")
        st.caption(f"{log['mensagem']}")
        st.markdown("---")

# ============================================
# CONTEÚDO PRINCIPAL
# ============================================

if menu_option == "📊 Dashboard":
    st.title("📊 Dashboard Rasther V29")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Total de Atualizações",
            f"{st.session_state.stats['total_updates']:,}",
            f"+{st.session_state.stats['updates_hoje']} hoje"
        )
    with col2:
        st.metric(
            "Dispositivos Ativos",
            st.session_state.stats['dispositivos_online'],
            f"{st.session_state.stats['dispositivos_online'] - st.session_state.stats['dispositivos_total']} vs total"
        )
    with col3:
        st.metric(
            "Licenças Ativas",
            st.session_state.stats['licencas_ativas'],
            "100%"
        )
    with col4:
        st.metric(
            "Usuários Ativos",
            st.session_state.stats['usuarios_ativos'],
            "+5 esta semana"
        )
    
    # Gráficos sem Plotly
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Atualizações por Dia")
        # Dados simulados
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        updates = np.random.randint(5, 30, size=30)
        create_line_chart(dates, updates, "Atualizações nos últimos 30 dias")
    
    with col2:
        st.subheader("Dispositivos por Versão")
        versions = ['v2.1.5', 'v2.1.3', 'v2.0.9', 'v2.0.5']
        counts = [15, 42, 23, 8]
        create_bar_chart(counts, versions, "Distribuição de Versões")
    
    # Tabela de dispositivos
    st.subheader("📱 Dispositivos Recentes")
    df_devices = pd.DataFrame(st.session_state.devices)
    df_devices['ultimo_acesso'] = pd.to_datetime(df_devices['ultimo_acesso']).dt.strftime('%d/%m/%Y %H:%M')
    st.dataframe(
        df_devices[['nome', 'serial', 'versao', 'ultimo_acesso', 'status']],
        use_container_width=True,
        hide_index=True
    )
    
    # Logs recentes
    with st.expander("📋 Logs do Sistema", expanded=False):
        for log in st.session_state.logs:
            st.text(f"[{log['timestamp'].strftime('%H:%M:%S')}] {log['mensagem']}")

elif menu_option == "📱 Dispositivos":
    st.title("📱 Gerenciar Dispositivos")
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Status", ["Todos", "Online", "Offline"])
    with col2:
        version_filter = st.selectbox("Versão", ["Todas", "v2.1.5", "v2.1.3", "v2.0.9"])
    with col3:
        search = st.text_input("Buscar", placeholder="Serial ou cliente...")
    
    # Tabela de dispositivos
    df = pd.DataFrame(st.session_state.devices)
    
    # Aplicar filtros
    if status_filter != "Todos":
        df = df[df['status'] == status_filter.lower()]
    if version_filter != "Todas":
        df = df[df['versao'] == version_filter]
    if search:
        df = df[df['serial'].str.contains(search, case=False) | 
                df['cliente'].str.contains(search, case=False)]
    
    # Mostrar tabela com ações
    for idx, device in df.iterrows():
        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns([2, 2, 1, 1, 1, 1])
            with col1:
                st.write(f"**{device['nome']}**")
                st.caption(device['serial'])
            with col2:
                st.write(f"Cliente: {device['cliente']}")
                st.caption(f"Último acesso: {pd.to_datetime(device['ultimo_acesso']).strftime('%d/%m/%Y %H:%M')}")
            with col3:
                st.write(f"Versão: {device['versao']}")
                st.caption(f"Hardware: {device['hardware']}")
            with col4:
                status_color = get_status_color(device['status'])
                st.markdown(f"Status: :{status_color}[{device['status'].upper()}]")
                if device['status'] == 'online':
                    st.caption(f"Bateria: {device['bateria']}% | Sinal: {device['sinal']}%")
            with col5:
                if st.button("📊", key=f"stats_{device['id']}"):
                    st.info(f"Detalhes do dispositivo {device['serial']}")
            with col6:
                if st.button("⚡", key=f"update_{device['id']}"):
                    st.warning(f"Iniciar atualização do dispositivo {device['serial']}?")
            st.divider()

elif menu_option == "🔧 Firmware":
    st.title("🔧 Gerenciar Firmware")
    
    tab1, tab2, tab3 = st.tabs(["📦 Versões", "📤 Distribuir", "📋 Histórico"])
    
    with tab1:
        st.subheader("Versões Disponíveis")
        
        for modelo, data in st.session_state.firmwares.items():
            with st.expander(f"📱 {data['modelo']}", expanded=True):
                for versao in data['versoes']:
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col1:
                        st.markdown(f"### {versao['versao']}")
                        if versao['critica']:
                            st.markdown("🔴 **CRÍTICA**")
                    with col2:
                        st.write(f"📅 {versao['data']}")
                        st.write(f"📦 {format_bytes(versao['tamanho'])}")
                        st.write(f"📥 {versao['downloads']} downloads")
                        with st.expander("📋 Changelog"):
                            for item in versao['changelog']:
                                st.write(f"• {item}")
                    with col3:
                        if st.button("📥 Baixar", key=f"download_{modelo}_{versao['versao']}"):
                            st.success(f"Download de {versao['versao']} iniciado!")
                    st.divider()
    
    with tab2:
        st.subheader("Distribuir Nova Versão")
        
        col1, col2 = st.columns(2)
        with col1:
            versao = st.text_input("Versão", value="v2.1.6")
            data_lancamento = st.date_input("Data de Lançamento")
            arquivo = st.file_uploader("Arquivo do Firmware", type=['bin'])
            
        with col2:
            critica = st.checkbox("Atualização Crítica")
            changelog = st.text_area(
                "Changelog",
                height=150,
                value="• Correções de segurança\n• Melhorias de performance\n• Novos protocolos"
            )
        
        if st.button("📤 Publicar Nova Versão", type="primary"):
            st.success("Nova versão publicada com sucesso!")
            add_log(f"Nova versão {versao} publicada", "success")
    
    with tab3:
        st.subheader("Histórico de Atualizações")
        
        df_history = pd.DataFrame(st.session_state.update_history)
        df_history['data'] = pd.to_datetime(df_history['data']).dt.strftime('%d/%m/%Y %H:%M')
        
        # Estatísticas
        total = len(df_history)
        sucessos = len(df_history[df_history['status'] == 'sucesso'])
        falhas = len(df_history[df_history['status'] == 'falha'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total", total)
        with col2:
            st.metric("Sucessos", sucessos, f"{(sucessos/total*100):.1f}%")
        with col3:
            st.metric("Falhas", falhas, f"{(falhas/total*100):.1f}%")
        
        st.dataframe(df_history, use_container_width=True, hide_index=True)

elif menu_option == "🔑 Licenças":
    st.title("🔑 Gerenciar Licenças")
    
    # Estatísticas de licenças
    total_licencas = len(st.session_state.licenses)
    ativas = len([l for l in st.session_state.licenses if l['status'] == 'ativa'])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de Licenças", total_licencas)
    with col2:
        st.metric("Ativas", ativas, f"{ativas/total_licencas*100:.0f}%")
    with col3:
        st.metric("A vencer (30 dias)", 2)
    with col4:
        st.metric("Expiradas", 0)
    
    # Lista de licenças
    st.subheader("Licenças Ativas")
    
    for license in st.session_state.licenses:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
            with col1:
                st.write(f"**{license['cliente']}**")
                st.caption(license['id'])
            with col2:
                st.write(f"Tipo: {license['tipo']}")
                exp_date = datetime.strptime(license['data_expiracao'], '%Y-%m-%d')
                days_left = (exp_date - datetime.now()).days
                st.caption(f"Expira em {days_left} dias")
            with col3:
                st.write(f"Dispositivos: {license['dispositivos']}/{license['max_dispositivos']}")
            with col4:
                status_color = get_status_color(license['status'])
                st.markdown(f":{status_color}[{license['status'].upper()}]")
            with col5:
                if st.button("🔄 Renovar", key=f"renew_{license['id']}"):
                    st.success(f"Licença {license['id']} renovada com sucesso!")
            st.divider()
    
    # Ativar nova licença
    with st.expander("➕ Ativar Nova Licença", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            novo_cliente = st.text_input("Cliente")
            nova_licenca = st.text_input("Código da Licença")
        with col2:
            novo_tipo = st.selectbox("Tipo", ["Básico", "Profissional", "Premium", "Enterprise"])
            nova_expiracao = st.date_input("Data de Expiração", value=datetime.now() + timedelta(days=365))
        
        if st.button("✅ Ativar Licença", type="primary"):
            st.success(f"Licença ativada para {novo_cliente}!")

elif menu_option == "📈 Relatórios":
    st.title("📈 Relatórios e Analytics")
    
    # Período
    col1, col2 = st.columns(2)
    with col1:
        data_inicio = st.date_input("Data Início", value=datetime.now() - timedelta(days=30))
    with col2:
        data_fim = st.date_input("Data Fim", value=datetime.now())
    
    # Gráficos
    tab1, tab2, tab3 = st.tabs(["📊 Uso", "📥 Downloads", "📱 Dispositivos"])
    
    with tab1:
        st.subheader("Atividades no Período")
        # Dados simulados
        dates = pd.date_range(start=data_inicio, end=data_fim, freq='D')
        updates = np.random.randint(5, 30, size=len(dates))
        
        chart_data = pd.DataFrame({
            'data': dates,
            'atualizacoes': updates
        })
        st.line_chart(chart_data.set_index('data'))
    
    with tab2:
        st.subheader("Downloads por Versão")
        # Downloads por versão
        versoes = ['v2.1.5', 'v2.1.3', 'v2.0.9', 'v2.0.5']
        downloads = [1250, 3500, 850, 420]
        
        chart_data = pd.DataFrame({
            'versao': versoes,
            'downloads': downloads
        })
        st.bar_chart(chart_data.set_index('versao'))
    
    with tab3:
        st.subheader("Dispositivos por Cliente")
        # Dispositivos por cliente
        clientes = [d['cliente'] for d in st.session_state.devices]
        dispositivos_por_cliente = {}
        for cliente in clientes:
            dispositivos_por_cliente[cliente] = dispositivos_por_cliente.get(cliente, 0) + 1
        
        df_clientes = pd.DataFrame([
            {"cliente": k, "dispositivos": v} 
            for k, v in dispositivos_por_cliente.items()
        ])
        st.bar_chart(df_clientes.set_index('cliente'))
    
    # Botão para exportar
    if st.button("📥 Exportar Relatório", type="primary"):
        st.success("Relatório exportado com sucesso!")

elif menu_option == "⚙️ Configurações":
    st.title("⚙️ Configurações do Sistema")
    
    tab1, tab2, tab3 = st.tabs(["🔧 Geral", "🔌 API", "👥 Usuários"])
    
    with tab1:
        st.subheader("Configurações Gerais")
        
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Nome da Empresa", value="Rasther Diagnostics")
            st.text_input("Email de Suporte", value="suporte@rasther.com")
            st.number_input("Timeout de Conexão (s)", value=30)
            
        with col2:
            st.text_input("URL do Servidor", value="https://api.rasther.com")
            st.text_input("Chave de API", value="••••••••••••••••", type="password")
            st.checkbox("Notificações por Email", value=True)
        
        st.divider()
        
        st.subheader("Configurações de Backup")
        col1, col2 = st.columns(2)
        with col1:
            st.checkbox("Backup Automático", value=True)
            st.selectbox("Frequência", ["Diário", "Semanal", "Mensal"])
        with col2:
            st.number_input("Reter backups (dias)", value=30)
            st.text_input("Pasta de Backup", value="/backups/rasther")
        
        if st.button("💾 Salvar Configurações", type="primary"):
            st.success("Configurações salvas com sucesso!")
            add_log("Configurações gerais atualizadas", "success")
    
    with tab2:
        st.subheader("Configurações da API")
        
        st.code("""
        # Endpoints Disponíveis
        GET    /api/v1/status
        GET    /api/v1/devices
        POST   /api/v1/devices/register
        GET    /api/v1/firmware/check/{model}
        GET    /api/v1/firmware/download/{model}/{version}
        POST   /api/v1/license/validate
        POST   /api/v1/license/activate
        """)
        
        st.info("Documentação completa da API disponível em /docs")
        
        st.subheader("Tokens de Acesso")
        st.code("""
        Token API: rasther_live_xxxxxxxxxxxxxx
        Secret:    xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        """)
        
        if st.button("🔄 Regenerar Token"):
            st.warning("Novo token gerado!")
            add_log("Token de API regenerado", "warning")
    
    with tab3:
        st.subheader("Gerenciar Usuários")
        
        users = [
            {"nome": "Admin", "email": "admin@rasther.com", "tipo": "admin", "status": "ativo"},
            {"nome": "Suporte", "email": "suporte@rasther.com", "tipo": "suporte", "status": "ativo"},
            {"nome": "Cliente Teste", "email": "cliente@teste.com", "tipo": "cliente", "status": "ativo"},
        ]
        
        df_users = pd.DataFrame(users)
        st.dataframe(df_users, use_container_width=True, hide_index=True)
        
        with st.expander("➕ Adicionar Usuário"):
            col1, col2 = st.columns(2)
            with col1:
                nome = st.text_input("Nome")
                email = st.text_input("Email")
            with col2:
                tipo = st.selectbox("Tipo", ["admin", "suporte", "cliente"])
                senha = st.text_input("Senha", type="password")
            
            if st.button("✅ Criar Usuário"):
                st.success(f"Usuário {nome} criado com sucesso!")
                add_log(f"Novo usuário criado: {email}", "success")

# ============================================
# RODAPÉ
# ============================================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"Rasther V29 v1.0.0")
with col2:
    st.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
with col3:
    st.caption(f"Dispositivos: {st.session_state.stats['dispositivos_online']}/{st.session_state.stats['dispositivos_total']} online")

# ============================================
# INTEGRAÇÃO COM HTML (opcional - se quiser usar o HTML)
# ============================================
if st.sidebar.button("🔄 Alternar para Interface HTML"):
    html_content = load_html()
    if html_content:
        st.components.v1.html(html_content, height=800, scrolling=True)
