# Calculadora de Desempenho de Aeronaves

Aplicação desktop baseada em Python para análise de parâmetros de desempenho de aeronaves, incluindo efeitos de altitude, autonomia, consumo de combustível e análise de envoltória de voo.

## Visão Geral

Esta ferramenta processa planos de voo e especificações de aeronave para calcular métricas de desempenho sob diversas condições atmosféricas e operacionais. Apresenta uma interface gráfica interativa construída com PySide2 (Qt) e fornece cálculos aeronáuticos abrangentes.

## Características

- **Parâmetros da Aeronave**: Define características da aeronave (massa, área de asa, motores, coeficientes aerodinâmicos)
- **Condições de Voo**: Define condições atmosféricas, altitude de cruzeiro, perfis de velocidade e carga útil
- **Análise de Desempenho**: 
  - Cálculos de envoltória de altitude
  - Previsões de autonomia e resistência
  - Estimativas de consumo de combustível
  - Desempenho de decolagem e pouso
  - Desempenho de subida
- **Interface Gráfica Interativa**: Interface baseada em abas para visualização de entrada e resultados
- **Referência Geográfica**: Integração de dados de aeroportos com suporte a basemap

## Requisitos

- Python 3.7+
- Dependências listadas em `requirements.txt`

```bash
numpy
pandas
matplotlib==3.5.3
frozendict==2.4.0
PySide2==5.15.2.1
basemap==1.3.3
```

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/AlessandroMDO/aircraft_performance_calculator.git
cd aircraft_performance_calculator
```

2. Crie um ambiente virtual (recomendado):
```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

Execute a aplicação:
```bash
python app/main_gui.py
```

A interface gráfica abrirá com três abas principais:

1. **Parâmetros da Aeronave**: Insira especificações de aeronave e dados aerodinâmicos
2. **Condições de Voo**: Define o cenário de voo (altitude, velocidade, peso, etc.)
3. **Resultados**: Visualize métricas de desempenho calculadas e gráficos

## Estrutura do Projeto

```
aircraft_performance_calculator/
├── app/
│   ├── main_gui.py          # Ponto de entrada principal da aplicação
│   ├── functions/           # Módulos de cálculo aeronáutico
│   └── guis/                # Componentes da interface
├── guis/                    # Definições da interface (PySide2)
├── tests/                   # Testes unitários
├── requirements.txt         # Dependências Python
└── gui_icon.png            # Ícone da aplicação
```

## Desenvolvimento

### Executar testes:
```bash
python -m pytest tests/
```

### Estrutura do código:
- `app/functions/aero.py`: Cálculos aeronáuticos principais
- `app/guis/`: Componentes individuais da interface (abas, diálogos)
- `app/main_gui.py`: Janela principal e manipulação de eventos

## Autor

Desenvolvido como projeto de trabalho de conclusão de curso (TCC) na EESC-USP (Escola de Engenharia de São Carlos, Universidade de São Paulo).

**Aluno:** Alessandro Melooliver de Oliveira  
**Orientador:** Ricardo Afonso Angélico  
**Ano:** 2024
**Trabalho**: https://bdta.abcd.usp.br/directbitstream/e44ebba3-2047-45d3-8439-e578d883c6d1/Oliveira_Alessandro_Melo_de_VFinal-Autorizado.pdf


## Contato

Para dúvidas ou contribuições, abra uma *issue* no GitHub.

---

**Nota:** Este projeto foi desenvolvido como trabalho acadêmico. Pode conter suposições específicas do domínio adequadas ao contexto da tese, mas pode necessitar adaptação para uso em produção.
