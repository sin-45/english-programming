import tkinter as tk
import threading
import queue
from compiler import EnglishCompiler

class EnglishIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("English-programming IDE (拡張子 .eng)")
        self.root.geometry("600x400")

        # タイマー用の変数
        self.debounce_timer = None
        
        # スレッド間通信用のキュー（マルチスレッド用）
        self.result_queue = queue.Queue()

        # コンパイラの読み込み
        self.compiler = EnglishCompiler()

        # 上部：コード入力エリア
        self.text_area = tk.Text(self.root, font=("Consolas", 14), height=10)
        self.text_area.pack(expand=True, fill='both', padx=10, pady=10)
        
        # キーを離したときに待機処理を呼び出す
        self.text_area.bind('<KeyRelease>', self.on_key_release)

        # 下部：コンソール（エラー出力エリア）
        self.console_area = tk.Text(self.root, font=("Consolas", 12), height=8, bg="#1e1e1e", fg="#cccccc")
        self.console_area.pack(expand=False, fill='x', padx=10, pady=(0, 10))
        self.console_area.insert(tk.END, "Ready. 英文を入力してください...\n")
        self.console_area.config(state=tk.DISABLED)
        
        # キューを定期的にチェックするループを開始
        self.check_queue()

    def on_key_release(self, event=None):
        """ユーザーが文字を入力するたびに呼ばれるが、コンパイルを0.5秒遅らせる"""
        # 連続入力中はタイマーをリセット
        if self.debounce_timer is not None:
            self.root.after_cancel(self.debounce_timer)
            
        # タイピングが止まってから500ミリ秒後にコンパイル開始処理を呼ぶ
        self.debounce_timer = self.root.after(500, self.start_syntax_check)

    def start_syntax_check(self):
        """別スレッドでコンパイル処理を開始する（画面をフリーズさせないため）"""
        code = self.text_area.get("1.0", tk.END).strip()
        
        if not code:
            self.update_console_ui([], empty=True)
            return
            
        self.console_area.config(state=tk.NORMAL)
        self.console_area.delete("1.0", tk.END)
        self.console_area.insert(tk.END, "Compiling...\n")
        self.console_area.config(fg="#888888")
        self.console_area.config(state=tk.DISABLED)

        # 重いコンパイル処理を、画面とは別のスレッド（裏側）で実行する
        threading.Thread(target=self.run_compiler, args=(code,), daemon=True).start()

    def run_compiler(self, code):
        """バックグラウンドで実行されるコンパイル処理"""
        errors = self.compiler.compile(code)
        # 処理が終わったら結果をキュー（受け渡し窓口）に入れる
        self.result_queue.put(errors)

    def check_queue(self):
        """定期的にキューをチェックし、裏側からの結果があればUIを更新する"""
        try:
            # キューから結果を取り出す
            errors = self.result_queue.get_nowait()
            self.update_console_ui(errors)
        except queue.Empty:
            pass
        finally:
            # 100ミリ秒ごとに再度チェック（画面の動きを邪魔しないほど一瞬です）
            self.root.after(100, self.check_queue)
            
    def update_console_ui(self, errors, empty=False):
        """コンパイル結果を画面に反映する処理"""
        self.console_area.config(state=tk.NORMAL)
        self.console_area.delete("1.0", tk.END)
        
        if empty:
            self.console_area.insert(tk.END, "Ready...\n")
            self.console_area.config(state=tk.DISABLED)
            self.text_area.configure(bg="white")
            return

        if not errors:
            self.console_area.insert(tk.END, "✓ Build Succeeded [0 errors]\n")
            self.console_area.config(fg="#4CAF50")
            self.text_area.configure(bg="#f0fff0")
        else:
            self.console_area.insert(tk.END, f"✗ Build Failed [{len(errors)} errors]\n")
            for err in errors:
                self.console_area.insert(tk.END, f"  - {err}\n")
            self.console_area.config(fg="#ff5252")
            self.text_area.configure(bg="#fff0f0")

        self.console_area.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = EnglishIDE(root)
    root.mainloop()