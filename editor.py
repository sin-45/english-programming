import tkinter as tk
from compiler import EnglishCompiler

class EnglishIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("English-programming IDE (拡張子 .eng)")
        self.root.geometry("600x400")

        # コンパイラの読み込み
        self.compiler = EnglishCompiler()

        # 上部：コード入力エリア
        self.text_area = tk.Text(self.root, font=("Consolas", 14), height=10)
        self.text_area.pack(expand=True, fill='both', padx=10, pady=10)
        
        # キーボードを叩くたびに構文チェックを実行
        self.text_area.bind('<KeyRelease>', self.check_syntax)

        # 下部：コンソール（エラー出力エリア）
        self.console_area = tk.Text(self.root, font=("Consolas", 12), height=8, bg="#1e1e1e", fg="#cccccc")
        self.console_area.pack(expand=False, fill='x', padx=10, pady=(0, 10))
        self.console_area.insert(tk.END, "Ready. 英文を入力してください...\n")
        self.console_area.config(state=tk.DISABLED) # 直接編集できないようにする

    def check_syntax(self, event=None):
        # 入力されたテキストを取得
        code = self.text_area.get("1.0", tk.END).strip()
        
        # エラー表示エリアをクリア
        self.console_area.config(state=tk.NORMAL)
        self.console_area.delete("1.0", tk.END)

        if not code:
            self.console_area.insert(tk.END, "Ready...\n")
            self.console_area.config(state=tk.DISABLED)
            self.text_area.configure(bg="white")
            return

        # コンパイル実行！
        errors = self.compiler.compile(code)

        if not errors:
            self.console_area.insert(tk.END, "✓ Build Succeeded [0 errors]\n")
            self.console_area.config(fg="#4CAF50") # 成功時は緑色
            self.text_area.configure(bg="#f0fff0") # 入力背景もうっすら緑に
        else:
            self.console_area.insert(tk.END, f"✗ Build Failed [{len(errors)} errors]\n")
            for err in errors:
                self.console_area.insert(tk.END, f"  - {err}\n")
            self.console_area.config(fg="#ff5252") # エラー時は赤色
            self.text_area.configure(bg="#fff0f0") # 入力背景もうっすら赤に

        self.console_area.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = EnglishIDE(root)
    root.mainloop()