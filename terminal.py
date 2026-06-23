# 先ほど作った compiler.py から EnglishCompiler クラスを読み込む
from compiler import EnglishCompiler

# ターミナル出力用のカラーコード
COLOR_RED = '\033[91m'
COLOR_GREEN = '\033[92m'
COLOR_YELLOW = '\033[93m'
COLOR_CYAN = '\033[96m'
COLOR_RESET = '\033[0m'

def start_terminal():
    print(f"{COLOR_YELLOW}[System] Booting English-programming terminal...{COLOR_RESET}")
    print(f"{COLOR_YELLOW}[System] Loading Language Model (This may take a few seconds)...{COLOR_RESET}")
    
    # ここでコンパイラ（頭脳）を起動
    compiler = EnglishCompiler()
    
    print(f"{COLOR_GREEN}[System] Terminal is ready!{COLOR_RESET}\n")
    print("=" * 50)
    print(f"{COLOR_CYAN} English-programming Interactive CLI{COLOR_RESET}")
    print(" Type your code below. (Type 'exit' or 'quit' to stop)")
    print("=" * 50)

    while True:
        try:
            # 入力プロンプト
            code = input(f"\n{COLOR_CYAN}english>{COLOR_RESET} ")
            
            if not code.strip():
                continue
                
            if code.lower() in ['exit', 'quit']:
                print("Exiting terminal. Goodbye!")
                break
            
            # コンパイラにコードを渡してエラーを受け取る
            errors = compiler.compile(code)
            
            # 結果の表示
            if not errors:
                print(f"{COLOR_GREEN}Build Succeeded [0 errors]{COLOR_RESET}")
            else:
                print(f"{COLOR_RED}Build Failed [{len(errors)} errors]{COLOR_RESET}")
                for i, err in enumerate(errors, 1):
                    print(f"{COLOR_RED}  {i}. {err}{COLOR_RESET}")

        except KeyboardInterrupt:
            print("\nExiting terminal. Goodbye!")
            break

if __name__ == "__main__":
    start_terminal()