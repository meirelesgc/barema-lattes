INSTRUCAO_BASE = """
Responda à pergunta com base apenas no documento fornecido.
Elenque até três exemplos separados por virgulas
Pule duas linhas e transcreva o trecho exato que contem esses exemplos
"""

PROMPTS_AVALIACAO = {
    "publico_produto": f"""
Qual é o público-alvo e o produto exato proposto pelo projeto?
{INSTRUCAO_BASE}
""",
    "objetivos_metas_relevancia": f"""
    Quais são os objetivos, as metas e a relevância deste projeto para o setor produtivo?
    {INSTRUCAO_BASE}
""",
    "metodologia_gestao": f"""
    Como estão estruturadas a metodologia e a gestão da execução do projeto?
    {INSTRUCAO_BASE}
""",
    "colaboracoes_financiamento": f"""
    O projeto cita instituições colaboradoras, empresas financiadoras, ou algum financiamento anterior/atual de órgão de fomento?
    {INSTRUCAO_BASE}
""",
    "potencial_inovacao_empreendedorismo": f"""
    Qual é o potencial do projeto para a produção tecnológica, inovação e para ações de empreendedorismo inovador?
    {INSTRUCAO_BASE}
""",
    "demandas_escalabilidade": f"""
    O projeto atende a demandas reais do mercado ou sociedade? Existe indicação clara de como será a escalabilidade e a adoção em larga escala da solução?
    {INSTRUCAO_BASE}
""",
    "maturidade_resultados": f"""
    Qual é o nível de maturidade tecnológica atual (TRL) do projeto e quais resultados científicos e tecnológicos já foram alcançados?
    {INSTRUCAO_BASE}
""",
    "organizacao_parcerias_extensao": f"""
    Como é descrita a organização do projeto, a coerência com as pesquisas em desenvolvimento, as parcerias e a participação clara do proponente em atividades de desenvolvimento tecnológico ou extensão inovadora?
    {INSTRUCAO_BASE}
""",
    "perfil_tecnologico": f"""
    Qual é o perfil de enquadramento do projeto: EDU (Tecnologias Educacionais) ou SOC (Tecnologias Sociais)?
    {INSTRUCAO_BASE}
""",
}

INSTRUCAO_ESTRUTURADA = """
Você deve extrair informações do documento e retornar EXCLUSIVAMENTE um objeto JSON com as seguintes chaves:

1. "sumula": Texto com até 5 realizações, formação, histórico profissional, financiamentos, indicadores e links de bases.
2. "transferencia_tecnologia_nota": Número inteiro correspondente à nota de impacto/abrangência.
3. "transferencia_tecnologia_observacao": Justificativa textual da nota atribuída.
4. "extensao_inovadora_nota": Número inteiro correspondente à nota da ação de extensão.
5. "extensao_inovadora_observacao": Justificativa textual da nota atribuída.
6. "trajetoria_proponente": Número inteiro correspondente à nota de aderência.

Critérios para Transferência de Tecnologia (Impacto/Abrangência):
- 10: Nacional e Estado
- 9: Regional (mais de 1 município)
- 8: Município
- 7: Entidade/Organização

Critérios para Extensão Inovadora:
- 10: Processo formativo no contexto de transferência de tecnologia
- 9: Parcerias público/privadas para transferência de conhecimento
- 8: Relação com projetos de extensão
- 7: Popularização da ciência

Critérios para Trajetória do Proponente em Tecnologias Sociais e Educacionais:
- 10: Aderência com a área ALTA
- 7: Aderência com a área MÉDIA
- 4: Aderência com a área BAIXA
"""

PROMPT_BAREMA_NOVO = f"""
Analise o currículo fornecido e preencha os campos conforme as instruções.
{INSTRUCAO_ESTRUTURADA}
"""
