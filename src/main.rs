use std::collections::HashMap;
use std::fs;

// ==========================================
// 1. トークンの定義 (Lexerが生成するもの)
// ==========================================
#[derive(Debug, Clone, PartialEq)]
enum Token {
    Let,
    Ident(String),
    Colon,
    Assign,
    StringLit(String),
    Dot,
    Semi,
}

// ==========================================
// 2. 抽象構文木 (AST) と 型の定義
// 教育目的に特化し、基本5文型を構成する品詞のみに限定
// ==========================================
#[derive(Debug, Clone, PartialEq)]
enum WordType {
    Noun,        // 名詞 (S, O, Cになる)
    Verb,        // 一般動詞 (Vになる)
    BeVerb,      // be動詞 (SVCを作るための特別なV)
    Adjective,   // 形容詞 (Cになる)
}

#[derive(Debug, Clone)]
enum AstNode {
    // 単語の定義: let he: 名詞 = "彼";
    WordDef {
        name: String,
        word_type: WordType,
        meaning: String,
    },
    // 文の定義: let s: 文 = he.play.tennis;
    SentenceDef {
        name: String,
        expected_type: String, // "文", "SV", "SVC" など
        chain: Vec<String>,
    },
}

// ==========================================
// 3. 字句解析器 (Lexer)
// ==========================================
fn tokenize(code: &str) -> Vec<Token> {
    let mut tokens = Vec::new();
    let chars: Vec<char> = code.chars().collect();
    let mut pos = 0;

    while pos < chars.len() {
        let c = chars[pos];

        if c.is_whitespace() {
            pos += 1;
            continue;
        }

        // コメントのスキップ
        if c == '/' && pos + 1 < chars.len() && chars[pos + 1] == '/' {
            while pos < chars.len() && chars[pos] != '\n' {
                pos += 1;
            }
            continue;
        }

        match c {
            ':' => { tokens.push(Token::Colon); pos += 1; }
            '=' => { tokens.push(Token::Assign); pos += 1; }
            '.' => { tokens.push(Token::Dot); pos += 1; }
            ';' => { tokens.push(Token::Semi); pos += 1; }
            '"' => {
                pos += 1;
                let mut string_lit = String::new();
                while pos < chars.len() && chars[pos] != '"' {
                    string_lit.push(chars[pos]);
                    pos += 1;
                }
                tokens.push(Token::StringLit(string_lit));
                pos += 1; // 閉じる "
            }
            _ => {
                // 識別子（アルファベット、日本語）の読み取り
                if c.is_alphanumeric() || is_japanese_char(c) {
                    let mut ident = String::new();
                    while pos < chars.len() && (chars[pos].is_alphanumeric() || is_japanese_char(chars[pos]) || chars[pos] == '_') {
                        ident.push(chars[pos]);
                        pos += 1;
                    }
                    if ident == "let" {
                        tokens.push(Token::Let);
                    } else {
                        tokens.push(Token::Ident(ident));
                    }
                } else {
                    panic!("Lexer Error: 不正な文字が見つかりました -> '{}'", c);
                }
            }
        }
    }
    tokens
}

fn is_japanese_char(c: char) -> bool {
    // 簡易的な日本語判定（ひらがな、カタカナ、漢字など）
    c >= '\u{3040}' && c <= '\u{9FFF}'
}

// ==========================================
// 4. 構文解析器 (Parser)
// ==========================================
fn parse(tokens: Vec<Token>) -> Vec<AstNode> {
    let mut ast = Vec::new();
    let mut pos = 0;

    while pos < tokens.len() {
        if tokens[pos] == Token::Let {
            pos += 1;
            
            let name = match &tokens[pos] {
                Token::Ident(n) => n.clone(),
                _ => panic!("Parse Error: 変数名が期待されます"),
            };
            pos += 1;

            if tokens[pos] != Token::Colon { panic!("Parse Error: ':' が期待されます"); }
            pos += 1;

            let type_name = match &tokens[pos] {
                Token::Ident(t) => t.clone(),
                _ => panic!("Parse Error: 型名が期待されます"),
            };
            pos += 1;

            if tokens[pos] != Token::Assign { panic!("Parse Error: '=' が期待されます"); }
            pos += 1;

            // 「文」の定義の場合（メソッドチェーン）
            if type_name == "文" || type_name == "Sentence" || 
               type_name == "SV" || type_name == "SVC" || type_name == "SVO" || 
               type_name == "SVOO" || type_name == "SVOC" {
                let mut chain = Vec::new();
                
                // 最初の単語
                match &tokens[pos] {
                    Token::Ident(w) => chain.push(w.clone()),
                    _ => panic!("Parse Error: 単語が期待されます"),
                }
                pos += 1;

                // ドットで繋がる単語をパース
                while pos < tokens.len() && tokens[pos] == Token::Dot {
                    pos += 1;
                    match &tokens[pos] {
                        Token::Ident(w) => chain.push(w.clone()),
                        _ => panic!("Parse Error: ドットの後には単語が期待されます"),
                    }
                    pos += 1;
                }

                if pos < tokens.len() && tokens[pos] == Token::Semi {
                    pos += 1;
                }

                ast.push(AstNode::SentenceDef { name, expected_type: type_name, chain });
            } 
            // 「単語」の定義の場合
            else {
                let word_type = match type_name.as_str() {
                    "名詞" | "Noun" => WordType::Noun,
                    "動詞" | "Verb" => WordType::Verb,
                    "be動詞" | "BeVerb" => WordType::BeVerb,
                    "形容詞" | "Adjective" => WordType::Adjective,
                    _ => panic!("Parse Error: 基本5文型を構成しない未知の型 '{}' です", type_name),
                };

                let meaning = match &tokens[pos] {
                    Token::StringLit(s) => s.clone(),
                    _ => panic!("Parse Error: 文字列が期待されます"),
                };
                pos += 1;

                if pos < tokens.len() && tokens[pos] == Token::Semi {
                    pos += 1;
                }

                ast.push(AstNode::WordDef { name, word_type, meaning });
            }
        } else {
            panic!("Parse Error: 'let' から始まる構文が期待されます");
        }
    }
    ast
}

// ==========================================
// 5. 評価器 兼 翻訳エンジン (Evaluator & Translator)
// ==========================================
fn evaluate(ast: Vec<AstNode>) {
    // 辞書（環境メモリ）
    let mut env: HashMap<String, (WordType, String)> = HashMap::new();

    println!("==========================================");
    println!("     English-Chain Compiler (Rust)        ");
    println!("     〜 基本5文型 厳格チェックモード 〜   ");
    println!("==========================================");
    println!("[INFO] 辞書の登録を開始します...");

    for node in ast {
        match node {
            AstNode::WordDef { name, word_type, meaning } => {
                env.insert(name.clone(), (word_type.clone(), meaning.clone()));
                println!("  + 登録: {} = \"{}\" ({:?})", name, meaning, word_type);
            }
            AstNode::SentenceDef { name, expected_type, chain } => {
                println!("\n▶ 文 '{}' を解析中: {} (指定型: {})", name, chain.join("."), expected_type);
                
                let mut current_types = Vec::new();
                let mut meanings = Vec::new();
                let mut has_error = false;

                for word in &chain {
                    if let Some((t, m)) = env.get(word) {
                        current_types.push(t.clone());
                        meanings.push(m.clone());
                    } else {
                        println!("  [エラー] NameError: 未定義の単語 '{}' が使われています", word);
                        has_error = true;
                        break;
                    }
                }

                if has_error { continue; }

                // 型の並び（文型）のチェックと、自然な日本語への「翻訳構築」
                let (is_valid, actual_type, translation) = match current_types.as_slice() {
                    // 第1文型: SV (名詞 -> 動詞)
                    [WordType::Noun, WordType::Verb] => {
                        (true, "SV", format!("{} が {}", meanings[0], meanings[1]))
                    }
                    // 第2文型: SVC (名詞 -> be動詞 -> 形容詞 または 名詞)
                    [WordType::Noun, WordType::BeVerb, WordType::Adjective] | 
                    [WordType::Noun, WordType::BeVerb, WordType::Noun] => {
                        (true, "SVC", format!("{} は {} {}", meanings[0], meanings[2], meanings[1]))
                    }
                    // 第3文型: SVO (名詞 -> 動詞 -> 名詞)
                    [WordType::Noun, WordType::Verb, WordType::Noun] => {
                        (true, "SVO", format!("{} は {} を {}", meanings[0], meanings[2], meanings[1]))
                    }
                    // 第4文型: SVOO (名詞 -> 動詞 -> 名詞 -> 名詞)
                    [WordType::Noun, WordType::Verb, WordType::Noun, WordType::Noun] => {
                        (true, "SVOO", format!("{} は {} に {} を {}", meanings[0], meanings[2], meanings[3], meanings[1]))
                    }
                    // 第5文型: SVOC (名詞 -> 動詞 -> 名詞 -> 形容詞)
                    [WordType::Noun, WordType::Verb, WordType::Noun, WordType::Adjective] => {
                        (true, "SVOC", format!("{} は {} を {} と {}", meanings[0], meanings[2], meanings[3], meanings[1]))
                    }
                    _ => {
                        (false, "", String::new())
                    }
                };

                if is_valid {
                    // 初心者向けの「文」指定か、中級者向けの「SV」などの厳格指定かでチェックを分ける
                    if expected_type == "文" || expected_type == "Sentence" || expected_type == actual_type {
                        println!("  [成功] 型チェック通過: {}", actual_type);
                        println!("  [翻訳] {}", translation);
                    } else {
                        println!("  [エラー] TypeError: 実際の文型は '{}' ですが、変数宣言で '{}' が要求されています", actual_type, expected_type);
                        println!("           (ヒント: 英単語の並びと指定した型が一致していません)");
                    }
                } else {
                    println!("  [エラー] TypeError: 5文型のルールに違反しています -> {:?}", current_types);
                    println!("           (ヒント: 英単語の型(品詞)の並びが間違っていませんか？)");
                }
            }
        }
    }
    println!("\n==========================================");
    println!("             コンパイル終了               ");
    println!("==========================================");
}

// ==========================================
// メイン関数 (テスト実行)
// ==========================================
fn main() {
    // すべてのコードを1つのファイル (main.eng) から読み込む
    let code = fs::read_to_string("main.eng")
        .expect("エラー: 'main.eng' ファイルが見つかりません。実行ディレクトリに配置してください。");

    // 1. 字句解析
    let tokens = tokenize(&code);
    
    // 2. 構文解析
    let ast = parse(tokens);
    
    // 3. 評価と翻訳
    evaluate(ast);
}