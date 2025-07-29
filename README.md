
# Boids Simulation with C and Python
Uma implementação híbrida da simulação de boids (bandos de pássaros artificiais) que combina a performance do C com a flexibilidade do Python. O projeto utiliza OpenMP para paralelização e Pygame para renderização, oferecendo uma simulação fluida e interativa de comportamentos emergentes de enxame.

##  Sobre o Algoritmo Boids
O algoritmo Boids, criado por Craig Reynolds em 1986, simula o comportamento de bandos através de três regras fundamentais:

- Separação: Evita colisões mantendo distância mínima entre boids
- Alinhamento: Sincroniza a direção de movimento com vizinhos próximos
- Coesão: Mantém o grupo unido direcionando boids para o centro do bando

## Características do Projeto

- Backend em C: Lógica de simulação otimizada com OpenMP para processamento paralelo
- Frontend em Python: Interface gráfica interativa com Pygame
- Sistema de Grid: Otimização espacial para melhor performance
- Interação com Mouse: Modos de medo e atração responsivos
- Interface Configurável: Controles em tempo real para todos os parâmetros
- Múltiplos Comportamentos de Borda: Turn, Bounce e Wrap
- Sistema de Importação/Exportação: Salve e carregue configurações personalizadas

## Pré-requisitos

### Sistema Operacional

- Linux, macOS ou Windows

### Compilador C

- GCC com suporte a OpenMP (versão 4.9 ou superior recomendada)
- No Ubuntu/Debian: sudo apt-get install gcc
- No macOS: brew install gcc ou usar Xcode Command Line Tools
- No Windows: MinGW-w64 ou Visual Studio Build Tools

### Python

- Python 3.7+ com pip

### Dependências Python

```
pip install -r requirements.txt
```

## Instalação e Execução

###  1. Clone o Repositório
```
git clone <repository-url> 
cd boids-simulation 
```

### 2. Instale as Dependências Python
```
pip install -r requirements.txt
```

### 3. Compile e Execute

```
make
```
Ou execute os passos separadamente:
```
make compile

make run
```

### 4.Limpeza(opcional)

```
make clean
```

## Estrutura do Projeto

```
boids-simulation/
├── backend/
│   ├── src/           # Código fonte C
│   └── include/       # Headers C
├── frontend/
│   ├── main.py        # Ponto de entrada
│   ├── app.py         # Classe principal da aplicação
│   ├── simulation.py  # Interface com biblioteca C
│   ├── renderer.py    # Sistema de renderização
│   ├── input_handler.py # Processamento de eventos
│   ├── UI.py          # Interface de usuário
│   ├── globals.py     # Configurações globais
│   ├── state.py       # Estado da aplicação
│   └── c_definitions/ # Definições de interface C
├── Makefile          # Build system
└── requirements.txt  # Dependências Python
```

## Controles

### Teclado

- **Barra de Espaço:** Pausar/Continuar simulação
- **H:** Mostrar/Ocultar painel de controle
- **M:** Ativar/Desativar interação com mouse
- **B:** Ativar/Desativar modo blur
- **V:** Mostrar/Ocultar raio visual dos boids
- **P:** Mostrar/Ocultar raio de proteção dos boids
- **D:** Ativar modo debug (mostra todos os raios)
- **F:** Desativar modo debug
- **6/7/8:** Alternar comportamento de borda (Turn/Bounce/Wrap)
- **Q/ESC:** Sair da aplicação

### Mouse

- **Movimento:** Influencia o movimento dos boids (quando ativo)
- **Clique Esquerdo:** Ativar modo medo (boids fogem do cursor)
- **Clique Direito:** Ativar modo atração (boids se aproximam do cursor)

### Interface Gráfica

- **Sliders:** Ajuste em tempo real de todos os parâmetros de simulação
- **Botões de Comportamento:** Alterne entre diferentes comportamentos de borda
- **Controles de População:** Modifique o número de boids e reinicie a simulação
- **Import/Export:** Salve e carregue configurações personalizadas

## Parâmetros Configuráveis

### Comportamento

- **Turn Factor:** Força de curvatura nas bordas
- **Cohesion:** Força de atração para o centro do grupo
- **Separation:** Força de repulsão entre boids próximos
- **Alignment:** Força de alinhamento com vizinhos
- **Min/Max Speed:** Limites de velocidade dos boids

### Visualização

- **Visual Range:** Distância de detecção de vizinhos
- **Protected Range:** Distância mínima entre boids
- **Population:** Número total de boids (10-5000)

### Interação

- **Mouse Fear/Attraction Radius:** Raio de influência do mouse

## Troubleshooting
### Erro de Compilação

- Verifique se o GCC está instalado e suporta OpenMP
- No macOS, pode ser necessário usar gcc-<version> específico do Homebrew

### Biblioteca Não Encontrada

 - Execute make clean seguido de make compile
- Verifique se o diretório frontend/boids/ foi criado

### Performance Baixa

- Reduza o número de boids nas configurações
- Verifique se a compilação foi feita com otimizações (-O3)

### Erro de Import Python

- Confirme que o pygame está instalado: pip list | grep pygame
- Execute pip install --upgrade pygame

### Licença
Este projeto foi desenvolvido para fins educacionais como parte do curso de Conceitos de Linguagens de Programação.

### Referências 

- Boids Algorithm Explanation
- Craig Reynolds - "Flocks, Herds, and Schools: A Distributed Behavioral Model" (1987)






