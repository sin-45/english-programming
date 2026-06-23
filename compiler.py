import spacy

class EnglishCompiler:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def compile(self, code: str) -> list:
        if not code.strip():
            return []

        doc = self.nlp(code.strip())
        errors = []

        # 1. 構文エラー: 行の先頭の大文字チェック
        if code and code[0].isalpha() and not code[0].isupper():
            errors.append("SyntaxError: 文の先頭は必ず大文字で始める必要があります。")

        # 2. 構文エラー: 文末のピリオドチェック
        if doc[-1].text not in ['.', '!', '?']:
            errors.append("SyntaxError: 文末に句読点 ('.', '!', '?') がありません。")

        for token in doc:
            # -----------------------------------------------------
            # A. 主語と動詞の不一致 (Subject-Verb Agreement)
            # -----------------------------------------------------
            if token.dep_ in ["nsubj", "nsubjpass"]:
                verb = token.head
                
                # 主語の単数・複数を判定
                is_third_singular = (
                    token.tag_ in ["NN", "NNP"] or 
                    (token.tag_ == "PRP" and token.text.lower() in ["he", "she", "it"])
                )
                is_plural = (
                    token.tag_ in ["NNS", "NNPS"] or
                    (token.tag_ == "PRP" and token.text.lower() in ["we", "they", "you"])
                )
                
                # be動詞の不一致チェック (例: He are -> error)
                if verb.lemma_ == "be":
                    if is_third_singular and verb.text.lower() in ["are", "were"]:
                        errors.append(f"TypeError: 主語 '{token.text}' (単数) に対して、be動詞 '{verb.text}' は不適切です。'is' または 'was' を使用してください。")
                    elif is_plural and verb.text.lower() in ["is", "was"]:
                        errors.append(f"TypeError: 主語 '{token.text}' (複数) に対して、be動詞 '{verb.text}' は不適切です。'are' または 'were' を使用してください。")
                else:
                    # 一般動詞の三単現・複数形チェック (例: They plays -> error)
                    if is_third_singular and verb.tag_ == "VBP":
                        errors.append(f"TypeError: 主語 '{token.text}' は三人称単数ですが、動詞 '{verb.text}' が原形です。'{verb.lemma_}s' などに修正してください。")
                    elif is_plural and verb.tag_ == "VBZ":
                        errors.append(f"TypeError: 主語 '{token.text}' は複数形ですが、動詞 '{verb.text}' に三単現の's'がついています。原形に戻してください。")

            # -----------------------------------------------------
            # B. 冠詞と名詞の不一致 (Articles)
            # -----------------------------------------------------
            if token.text.lower() in ['a', 'an']:
                head_noun = token.head
                if head_noun.tag_ in ['NNS', 'NNPS']:
                    errors.append(f"TypeError: 単数の冠詞 '{token.text}' の後に、複数形の名詞 '{head_noun.text}' が続いています。")
            
            # -----------------------------------------------------
            # C. 助動詞の後ろは原形 (Modal Verbs)
            # -----------------------------------------------------
            # 例: I can plays -> error
            if token.tag_ == "MD": 
                verb = token.head
                if verb.tag_ in ["VBZ", "VBD", "VBN"]:
                    errors.append(f"TypeError: 助動詞 '{token.text}' の後続動詞 '{verb.text}' が原形 (Base form) ではありません。")

            # -----------------------------------------------------
            # D. To不定詞の後ろは原形 (Infinitives)
            # -----------------------------------------------------
            # 例: I want to went -> error
            if token.tag_ == "TO" and token.dep_ in ["aux", "mark"]:
                verb = token.head
                if verb.tag_ in ["VBZ", "VBD", "VBN", "VBG"]:
                    errors.append(f"TypeError: To不定詞 '{token.text}' の後続動詞 '{verb.text}' が原形 (Base form) ではありません。")

            # -----------------------------------------------------
            # E. be動詞 + 動詞の原形はNG (Continuous / Passive)
            # -----------------------------------------------------
            # 例: I am play -> error (I am playing ならOK)
            if token.lemma_ == "be" and token.dep_ in ["aux", "auxpass"]:
                verb = token.head
                if verb.tag_ in ["VB", "VBP", "VBZ"]:
                    errors.append(f"SyntaxError: be動詞 '{token.text}' の後に、動詞の原形/現在形 '{verb.text}' が直接続いています。進行形(-ing) または 受動態(過去分詞) にしてください。")

            # -----------------------------------------------------
            # F. 動詞の連続による構文エラー (Consecutive Verbs)
            # -----------------------------------------------------
            # 例: I want go -> error (I want to go ならOK)
            if token.pos_ == "VERB" and token.head.pos_ == "VERB":
                if token.dep_ == "xcomp" and token.tag_ in ["VB", "VBP"]:
                    has_to = any(child.tag_ == "TO" for child in token.children)
                    if not has_to:
                         errors.append(f"SyntaxError: 動詞 '{token.head.text}' の直後に動詞 '{token.text}' が直接続いています。'to' 不定詞や動名詞(-ing)を使用してください。")

        return errors