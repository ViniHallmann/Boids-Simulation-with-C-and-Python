# --- Compilador e Flags ---
# Define o compilador a ser usado (GNU C Compiler)
CC = gcc-15
# Flags do compilador:
# -Ibackend/include:  Adiciona o diretório de includes para que o compilador encontre os .h
# -fPIC:              Gera código de posição independente, necessário para bibliotecas compartilhadas
# -fopenmp:           Habilita o suporte a OpenMP para paralelismo
# -g:                 Inclui informações de debug
# -Wall:              Mostra todos os avisos (boa prática)
CFLAGS = -O3 -Ibackend/include -fPIC -fopenmp -g -Wall

# --- Arquivos e Diretórios ---
# Diretório onde os arquivos de código-fonte .c estão
SRC_DIR = backend/src
# Encontra todos os arquivos .c no diretório de fontes
SRCS = $(wildcard $(SRC_DIR)/*.c)
# Gera uma lista de arquivos objeto (.o) a partir dos arquivos de fonte (.c)
OBJS = $(SRCS:.c=.o)

# Onde a biblioteca final (.so) deve ser colocada para o Python encontrar
# O Python está procurando em "frontend/boids/"
TARGET_DIR = frontend/boids
# Nome completo do arquivo da biblioteca compartilhada
TARGET_LIB = $(TARGET_DIR)/libboids.so

# --- Regras (Targets) ---

# Regra padrão (o que acontece quando você digita apenas "make")
# Primeiro, ela garante que a biblioteca seja compilada, depois executa o Python
all: run

# Regra para compilar a biblioteca C
# Depende de todos os arquivos objeto (.o)
# O comando cria o diretório de destino e depois linka os objetos na biblioteca final
$(TARGET_LIB): $(OBJS)
	@echo "--- Linkando a biblioteca compartilhada: $(TARGET_LIB) ---"
	@mkdir -p $(TARGET_DIR)
	$(CC) $(CFLAGS) -shared -o $@ $(OBJS)

# Regra padrão para compilar um arquivo .c em um arquivo .o
# Esta é uma regra de padrão do Make
$(SRC_DIR)/%.o: $(SRC_DIR)/%.c
	@echo "--- Compilando $< ---"
	$(CC) $(CFLAGS) -c $< -o $@

# Regra para executar o frontend em Python
# Ela "depende" da biblioteca, então o make irá compilar a C primeiro se necessário
run: $(TARGET_LIB)
	@echo "--- Executando o Frontend Python ---"
	cd frontend && python3 main.py

# Regra explícita apenas para compilação
compile: $(TARGET_LIB)
	@echo "--- Compilação da biblioteca C finalizada ---"

# Regra para limpar os arquivos gerados
# Remove os arquivos objeto e o diretório com a biblioteca .so
clean:
	@echo "--- Limpando arquivos compilados ---"
	@rm -f $(SRC_DIR)/*.o
	@rm -rf $(TARGET_DIR)
	@echo "--- Limpeza finalizada ---"

# Declara que 'all', 'run', 'compile' e 'clean' não são nomes de arquivos
.PHONY: all run compile clean