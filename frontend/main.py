import sys
import cProfile
import pstats
import io
from c_definitions import c_interfaces
from app import App

def main():
    """
    Ponto de entrada principal da aplicação.
    """
    if not c_interfaces.setup_library_interface(): sys.exit(1)

    app = App()
    app.run()

    print("P: Aplicação encerrada.")
    sys.exit(0)

def main_with_profiling():
    """
    Versão com profiling usando cProfile.
    """
    print("P: Iniciando aplicação com profiling...")
    
    # Cria o profiler
    profiler = cProfile.Profile()
    
    try:
        # Inicia o profiling
        profiler.enable()
        main()
    except KeyboardInterrupt:
        print("\nP: Aplicação interrompida pelo usuário.")
    finally:
        # Para o profiling
        profiler.disable()
        
        # Salva os resultados em arquivo
        profiler.dump_stats('profiling_results.prof')
        
        # Mostra estatísticas no terminal
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s)
        ps.sort_stats('cumulative')
        ps.print_stats(30)  # Top 30 funções mais pesadas
        
        print("\n" + "="*60)
        print("RELATÓRIO DE PROFILING - TOP 30 FUNÇÕES:")
        print("="*60)
        print(s.getvalue())
        
        # Salva relatório em arquivo
        with open('profiling_report.txt', 'w') as f:
            f.write(s.getvalue())
        
        print(f"\nP: Relatório salvo em 'profiling_report.txt'")
        print(f"P: Dados brutos salvos em 'profiling_results.prof'")

if __name__ == "__main__":
    # Para usar profiling, descomente a linha abaixo e comente a main()
    #main_with_profiling()
    main()