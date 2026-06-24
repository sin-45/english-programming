import language_tool_python

class EnglishCompiler:
    def __init__(self):
        # 安全にローカルエンジンを起動
        self.tool = language_tool_python.LanguageTool('en-US')

    def compile(self, code: str) -> list:
        if not code.strip():
            return []

        errors = []
        
        # NLPエンジンでコード（英文）を解析
        matches = self.tool.check(code)
        
        for match in matches:
            # 1. 【安全対策】メッセージを安全に取得
            # getattr(オブジェクト, '属性名', '無い場合の代わりの値') を使用
            msg = getattr(match, 'message', '文法エラーが検出されました。')
            msg_lower = msg.lower()
            
            error_type = "SyntaxError"
            if "spelling" in msg_lower or "misspelled" in msg_lower:
                error_type = "NameError (未定義の単語/スペルミス)"
            elif "whitespace" in msg_lower or "punctuation" in msg_lower or "comma" in msg_lower:
                error_type = "FormatError (記号や空白の誤り)"
            elif "agreement" in msg_lower or "verb" in msg_lower or "plural" in msg_lower or "singular" in msg_lower:
                error_type = "TypeError (文法・型の不一致)"

            # 2. 【安全対策】エラー箇所の特定（今回のクラッシュの根本原因を修正）
            # offset が無い場合は -1、errorLength が無い場合は length を探し、それでも無ければ 0
            err_offset = getattr(match, 'offset', -1)
            err_len = getattr(match, 'errorLength', getattr(match, 'length', 0))
            
            if err_offset >= 0 and err_len > 0:
                # オフセットと長さが取れれば、該当箇所の文字を切り出す
                error_text = code[err_offset:err_offset + err_len]
            else:
                # 文字数が取れなかった場合は、直接 matchedText を探すか、固定文字にする
                error_text = getattr(match, 'matchedText', '該当箇所')

            # エラーメッセージの組み立て
            err_msg = f"{error_type}: '{error_text}' -> {msg}"
            
            # 3. 【安全対策】修正提案も安全に取得
            replacements = getattr(match, 'replacements', [])
            if replacements:
                suggestions = ", ".join(replacements[:3])
                err_msg += f"\n      [Suggestion] もしかして: {suggestions} ?"
                
            errors.append(err_msg)

        return errors