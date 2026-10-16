import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="Quiz Show")

# 1. INJEÇÃO DE CSS (FONTES GIGANTES E AJUSTE DO PLACAR)
st.markdown("""
    <style>
    .pergunta-gigante {
        font-size: 45px !important;
        font-weight: bold;
        line-height: 1.3;
        color: #1f77b4;
        background-color: #f0f2f6;
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 30px;
    }
    div.stButton > button:first-child {
        font-size: 35px !important;
        font-weight: bold !important;
        height: auto !important;
        padding: 25px 20px !important;
        border-radius: 12px !important;
        white-space: normal !important;
        text-align: left !important;
    }
    /* Ajuste para evitar que o nome "Equipe" quebre no placar */
    .stAlert p {
        font-size: 30px !important;
        line-height: 1.4 !important;
        font-weight: bold !important;
        white-space: nowrap; 
    }
    p, h2, h3 {
        font-size: 30px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. CONFIGURAÇÃO INICIAL DA MEMÓRIA
if 'fase' not in st.session_state:
    st.session_state.fase = 'configuracao'

# ==========================================
# TELA 1: CONFIGURAÇÃO DO JOGO
# ==========================================
if st.session_state.fase == 'configuracao':
    st.title("⚙️ Configuração do Quiz - Estilo Show do Milhão")
    
    col_cfg1, col_cfg2 = st.columns(2)
    with col_cfg1:
        num_equipes = st.number_input("Número de Equipes", min_value=2, max_value=10, value=6)
    with col_cfg2:
        lista_de_equipes = [f"Equipe {i+1}" for i in range(num_equipes)]
        st.selectbox("Quem vai começar o jogo?", lista_de_equipes, key="equipe_start")
    
    st.markdown("### Cole as perguntas e opções abaixo.")
    st.error("**REGRA:** Separe com PONTO E VÍRGULA ( ; ) e coloque um ASTERISCO (*) na resposta certa!")
    
    perguntas_exemplo = """Qual comando mostra mensagens na tela em Python? ; A) input() ; *B) print() ; C) show() ; D) display()"""
    
    perguntas_texto = st.text_area("Lista de Perguntas", height=200, value=perguntas_exemplo)
    
    if st.button("▶️ Começar Jogo", use_container_width=True):
        linhas = [p.strip() for p in perguntas_texto.strip().split('\n') if p.strip()]
        
        if len(linhas) == 0:
            st.error("Adicione pelo menos uma pergunta para começar!")
        else:
            st.session_state.equipes = lista_de_equipes
            st.session_state.pontos = {equipe: 0 for equipe in st.session_state.equipes}
            
            st.session_state.perguntas = {i+1: linha for i, linha in enumerate(linhas)}
            st.session_state.perguntas_disponiveis = list(st.session_state.perguntas.keys())
            
            st.session_state.pergunta_selecionada = None 
            st.session_state.turno_atual = lista_de_equipes.index(st.session_state.equipe_start) 
            st.session_state.valor_pergunta = 3
            st.session_state.fase = 'jogo'
            st.session_state.mostrar_resultado = False
            st.session_state.resultado_atual = None
            st.session_state.opcao_clicada = None
            st.rerun()

# ==========================================
# TELA 2: O JOGO ROLANDO
# ==========================================
elif st.session_state.fase == 'jogo':
    
    def proxima_equipe():
        st.session_state.turno_atual = (st.session_state.turno_atual + 1) % len(st.session_state.equipes)

    st.markdown("<h1 style='text-align: center;'>🏆 Quiz de Redes 🏆</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # PLACAR
    colunas_placar = st.columns(len(st.session_state.equipes))
    for i, equipe in enumerate(st.session_state.equipes):
        with colunas_placar[i]:
            if i == st.session_state.turno_atual:
                st.success(f"**{equipe}**\n\n🎯 {st.session_state.pontos[equipe]} pts")
            else:
                st.info(f"**{equipe}**\n\n{st.session_state.pontos[equipe]} pts")
    st.write("---")

    equipe_da_vez = st.session_state.equipes[st.session_state.turno_atual]

    if len(st.session_state.perguntas_disponiveis) == 0 and st.session_state.pergunta_selecionada is None:
        st.success("🎉 Fim do Jogo! Todas as perguntas foram respondidas.")
        if st.button("🔄 Novo Jogo"):
            st.session_state.clear()
            st.rerun()

    # CENA A: PAINEL DE NÚMEROS
    elif st.session_state.pergunta_selecionada is None:
        # NOVO: Interface para alterar manualmente a equipa
        col_vez1, col_vez2 = st.columns([3, 1])
        with col_vez1:
            st.markdown(f"<h2>Vez da {equipe_da_vez}</h2>", unsafe_allow_html=True)
        with col_vez2:
            nova_equipe_idx = st.selectbox(
                "Passar a vez manualmente para:",
                range(len(st.session_state.equipes)),
                format_func=lambda i: st.session_state.equipes[i],
                index=st.session_state.turno_atual
            )
            if nova_equipe_idx != st.session_state.turno_atual:
                st.session_state.turno_atual = nova_equipe_idx
                st.rerun()
        
        st.write("") # Espaço
        cols = st.columns(5)
        for index, num in enumerate(st.session_state.perguntas_disponiveis):
            if cols[index % 5].button(f"Pergunta {num}", use_container_width=True):
                st.session_state.pergunta_selecionada = num
                st.session_state.valor_pergunta = 3 
                st.session_state.mostrar_resultado = False
                st.rerun()

    # CENA B: A PERGUNTA NA TELA
    else:
        num_atual = st.session_state.pergunta_selecionada
        linha_completa = st.session_state.perguntas[num_atual]
        
        partes = [parte.strip() for parte in linha_completa.split(';')]
        pergunta_texto = partes[0]
        opcoes_brutas = partes[1:]
        
        indice_correto = -1
        opcoes_limpas = []
        for i, op in enumerate(opcoes_brutas):
            if op.startswith('*'):
                indice_correto = i
                opcoes_limpas.append(op[1:].strip())
            else:
                opcoes_limpas.append(op)
        
        colEsq, colDir = st.columns([3, 1])
        with colEsq:
            st.markdown(f"<h2>Vez da {equipe_da_vez} 💰 Valendo {st.session_state.valor_pergunta} pts</h2>", unsafe_allow_html=True)
        with colDir:
            if not st.session_state.mostrar_resultado:
                timer_html = """
                <div id="relogio" style="font-size: 50px; font-weight: bold; color: #ff4b4b; text-align: right;">60s</div>
                <script>
                    var tempo = 60;
                    var display = document.getElementById('relogio');
                    var intervalo = setInterval(function() {
                        tempo--;
                        if (tempo > 10) { display.innerHTML = "⏳ " + tempo + "s"; }
                        else if (tempo > 0) { display.innerHTML = "⚠️ " + tempo + "s"; display.style.color = 'red'; }
                        else { display.innerHTML = "🚨 ACABOU!"; clearInterval(intervalo); }
                    }, 1000);
                </script>
                """
                components.html(timer_html, height=100)
        
        st.markdown(f'<div class="pergunta-gigante">Pergunta {num_atual}:<br>{pergunta_texto}</div>', unsafe_allow_html=True)
        
        if not st.session_state.mostrar_resultado:
            for i, op_texto in enumerate(opcoes_limpas):
                if st.button(f"👉 {op_texto}", use_container_width=True):
                    st.session_state.opcao_clicada = i
                    st.session_state.mostrar_resultado = True
                    
                    if i == indice_correto:
                        st.session_state.resultado_atual = 'acertou'
                        st.session_state.pontos[equipe_da_vez] += st.session_state.valor_pergunta
                    else:
                        st.session_state.resultado_atual = 'errou'
                        st.session_state.pontos[equipe_da_vez] -= 1
                    st.rerun()
                    
            st.write("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⏭️ PULOU (0 pts)", use_container_width=True):
                    st.session_state.resultado_atual = 'pulou'
                    st.session_state.mostrar_resultado = True
                    st.rerun()
            with col2:
                if st.button("🗑️ DESCARTAR", use_container_width=True):
                    st.session_state.perguntas_disponiveis.remove(num_atual)
                    st.session_state.pergunta_selecionada = None
                    proxima_equipe()
                    st.rerun()
                    
        else:
            clicada = st.session_state.opcao_clicada
            resultado = st.session_state.resultado_atual
            
            if resultado == 'acertou':
                st.success("✅ **CORRETO!**")
                for i, op_texto in enumerate(opcoes_limpas):
                    if i == indice_correto:
                        st.info(f"✔️ **{op_texto}**")
                    else:
                        st.markdown(f"<p style='color:gray;'>{op_texto}</p>", unsafe_allow_html=True)
                        
                if st.button("▶️ Voltar ao Painel (Próxima Equipe)", use_container_width=True):
                    st.session_state.perguntas_disponiveis.remove(num_atual)
                    st.session_state.pergunta_selecionada = None
                    st.session_state.mostrar_resultado = False
                    proxima_equipe()
                    st.rerun()
                    
            elif resultado == 'errou':
                st.error("❌ **ERRADO!** (-1 pt)")
                for i, op_texto in enumerate(opcoes_limpas):
                    if i == clicada:
                        st.error(f"✖️ **{op_texto}**")
                    else:
                        st.markdown(f"<p style='color:gray;'>{op_texto}</p>", unsafe_allow_html=True)
                        
                if st.button("▶️ Passar Pergunta (Valendo 2 pts)", use_container_width=True):
                    st.session_state.valor_pergunta = 2
                    st.session_state.mostrar_resultado = False
                    proxima_equipe()
                    st.rerun()
                    
            elif resultado == 'pulou':
                st.warning("⏭️ **PULOU!** (0 pts)")
                for op_texto in opcoes_limpas:
                    st.markdown(f"<p>{op_texto}</p>", unsafe_allow_html=True)
                    
                if st.button("▶️ Passar Pergunta (Valendo 2 pts)", use_container_width=True):
                    st.session_state.valor_pergunta = 2
                    st.session_state.mostrar_resultado = False
                    proxima_equipe()
                    st.rerun()