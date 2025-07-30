#!/usr/bin/env python3
"""
Benchmark script para medir performance das otimizações
"""
import time
import sys
import os
sys.path.append('frontend')

import globals
from frontend.simulation import Simulation

def benchmark_simulation(num_birds, duration_seconds=10):
    """Executa benchmark da simulação por um tempo específico"""
    print(f"🔥 BENCHMARK: {num_birds} boids por {duration_seconds}s")
    
    # Configurar simulação
    globals.NUM_BIRDS = num_birds
    globals.PAUSED = False
    globals.SHOW_UI_PANEL = False
    
    sim = Simulation(num_birds)
    
    start_time = time.time()
    frame_count = 0
    
    try:
        while time.time() - start_time < duration_seconds:
            sim.update()
            frame_count += 1
            
            # Progress indicator
            if frame_count % 100 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                print(f"  📊 Frame {frame_count}: {fps:.1f} FPS")
                
    except KeyboardInterrupt:
        print("⏹️  Benchmark interrompido")
    finally:
        sim.cleanup()
    
    elapsed = time.time() - start_time
    avg_fps = frame_count / elapsed
    
    print(f"📈 RESULTADOS:")
    print(f"   Boids: {num_birds}")
    print(f"   Frames: {frame_count}")
    print(f"   Tempo: {elapsed:.2f}s")
    print(f"   FPS Médio: {avg_fps:.1f}")
    print(f"   Boids×FPS: {num_birds * avg_fps:.0f}")
    print("-" * 50)
    
    return avg_fps

def main():
    print("🚀 BENCHMARK DE OTIMIZAÇÕES BOIDS")
    print("=" * 50)
    
    # Teste com diferentes quantidades de boids
    test_cases = [500, 1000, 2000, 3000, 4000, 5000]
    results = []
    
    for num_birds in test_cases:
        try:
            fps = benchmark_simulation(num_birds, duration_seconds=5)
            results.append((num_birds, fps))
        except Exception as e:
            print(f"❌ Erro com {num_birds} boids: {e}")
            break
    
    print("\n📊 RESUMO DOS RESULTADOS:")
    print("Boids\tFPS\tBoids×FPS")
    print("-" * 30)
    for num_birds, fps in results:
        throughput = num_birds * fps
        print(f"{num_birds}\t{fps:.1f}\t{throughput:.0f}")

if __name__ == "__main__":
    main()
