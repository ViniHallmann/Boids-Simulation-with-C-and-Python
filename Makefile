CC = gcc-15
CFLAGS = -O3 -Ibackend/include -fPIC -fopenmp -g -Wall


SRC_DIR = backend/src
SRCS = $(wildcard $(SRC_DIR)/*.c)
OBJS = $(SRCS:.c=.o)


TARGET_DIR = frontend/boids
TARGET_LIB = $(TARGET_DIR)/libboids.so


all: run
$(TARGET_LIB): $(OBJS)
	@echo "--- Linkando a biblioteca compartilhada: $(TARGET_LIB) ---"
	@mkdir -p $(TARGET_DIR)
	$(CC) $(CFLAGS) -shared -o $@ $(OBJS)

$(SRC_DIR)/%.o: $(SRC_DIR)/%.c
	@echo "--- Compilando $< ---"
	$(CC) $(CFLAGS) -c $< -o $@

run: $(TARGET_LIB)
	@echo "--- Executando o Frontend Python ---"
	cd frontend && python3 main.py

compile: $(TARGET_LIB)
	@echo "--- Compilação da biblioteca C finalizada ---"

clean:
	@echo "--- Limpando arquivos compilados ---"
	@rm -f $(SRC_DIR)/*.o
	@rm -rf $(TARGET_DIR)
	@echo "--- Limpeza finalizada ---"

.PHONY: all run compile clean