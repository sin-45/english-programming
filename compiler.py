import spacy

class EnglishCompiler:
    def __init__(self):
        # ターミナル側の表示と被らないよう、準備完了の合図だけ返すようにします
        self.nlp = spacy.load("en_core_web_sm")

    def compile(self, code: str) -> list:
        """入力されたコード（英文）を解析し、エラーのリストを返す"""
        doc = self.nlp(code)
        errors = []

        # 1. SyntaxError: 先頭の大文字チェック
        if code and not code[0].isupper():
            errors.append("SyntaxError: 行の先頭は必ず大文字で始める必要があります。")

        # 2. SyntaxError: 文末の句読点チェック
        if doc[-1].text not in ['.', '!', '?']:
            errors.append("SyntaxError: 文末にピリオド '.' がありません。")

        # 3. TypeError: 主語と動詞の不一致（三単現のs）チェック
        for token in doc:
            if token.dep_ == "nsubj":
                verb = token.head
                
                is_third_person_singular = (
                    token.tag_ in ["NN", "NNP"] or 
                    (token.tag_ == "PRP" and token.text.lower() in ["he", "she", "it"])
                )
                
                if is_third_person_singular:
                    if verb.tag_ == "VBP":
                        errors.append(f"TypeError: 主語 '{token.text}' は三人称単数ですが、動詞 '{verb.text}' が原形です。'{verb.lemma_}s' に修正してください。")

        return errors