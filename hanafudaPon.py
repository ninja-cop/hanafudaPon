import pyxel
import random
import math

class Particle:
    def __init__(self, x, y, color=None):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-4, -1)
        self.gravity = 0.1
        self.life = random.randint(30, 60)  # フレーム数
        self.max_life = self.life
        self.color = color if color else random.choice([8, 9, 10, 11, 12, 14, 15])
        self.size = random.randint(1, 3)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1
        
        # 軽い空気抵抗
        self.vx *= 0.98
        
        return self.life > 0
    
    def draw(self):
        # ライフに応じて透明度を調整（色の明度で表現）
        alpha_ratio = self.life / self.max_life
        if alpha_ratio > 0.7:
            color = self.color
        elif alpha_ratio > 0.4:
            color = max(0, self.color - 1)
        elif alpha_ratio > 0.2:
            color = max(0, self.color - 2)
        else:
            color = 0
        
        if self.size == 1:
            pyxel.pset(int(self.x), int(self.y), color)
        elif self.size == 2:
            pyxel.rect(int(self.x), int(self.y), 2, 2, color)
        else:
            pyxel.rect(int(self.x), int(self.y), 3, 3, color)

class HanafudaPon:
    def __init__(self):
        pyxel.init(256, 240, title="Hanafuda Pon")  # 元の画面比率に戻す

        # ゲーム状態管理
        self.game_state = "title"  # "title", "playing", "game_over"
        self.title_timer = 0  # タイトル画面のアニメーション用

        # 花札の設定
        self.card_width = 32
        self.card_height = 53
        self.cards_per_row = 8
        self.max_rows = 4
        self.max_cards = 32
        
        # ゲーム状態
        self.cards = []  # 画面上の花札
        self.selected_cards = []  # 選択中の花札
        self.score = 0
        self.spawn_timer = 0
        self.spawn_interval = 90  # フレーム数（3秒）
        self.game_over = False
        self.bonus_timer = 0
        self.bonus_multiplier = 1
        self.combo_message = ""  # 役成立メッセージ
        self.combo_timer = 0     # メッセージ表示時間
        
        # パーティクルシステム
        self.particles = []
        
        # 花札の種類（月ごと、4枚ずつ）
        self.months = ["松", "梅", "桜", "藤", "菖", "牡", "萩", "芒", "菊", "紅", "柳", "桐"]
        
        # 花札の画像データ初期化
        self.load_hanafuda_images()
        
        # 花札の役定義（カードタイプと月の組み合わせ）
        # 各月のカード構成: [光札, タン札, タネ札, カス札]の順
        self.card_types = {
            "松": ["光", "Akatan", "タネ", "カス"],   # 1月
            "梅": ["タネ", "Akatan", "カス", "カス"], # 2月
            "桜": ["光", "Akatan", "タネ", "カス"],   # 3月
            "藤": ["タネ", "タン", "カス", "カス"], # 4月
            "菖": ["タネ", "タン", "カス", "カス"], # 5月
            "牡": ["タネ", "Aotan", "カス", "カス"], # 6月
            "萩": ["タネ", "タン", "タネ", "カス"], # 7月（猪）
            "芒": ["光", "タネ", "タン", "カス"],   # 8月
            "菊": ["タネ", "Aotan", "カス", "カス"], # 9月
            "紅": ["タネ", "Aotan", "カス", "カス"], # 10月（鹿）
            "柳": ["光", "タン", "タネ", "カス"],   # 11月（雨）
            "桐": ["光", "タン", "カス", "カス"]    # 12月
        }
        
        # 特殊役の定義
        self.special_combinations = {
            "Aotan": {
                "cards": [("牡", 1), ("菊", 1), ("紅", 1)],  # 6月青タン、9月青タン、10月青タン
                "score": 800
            },
            "Akatan": {
                "cards": [("松", 1), ("梅", 1), ("桜", 1)],  # 1月赤タン、2月赤タン、3月赤タン
                "score": 800
            },
            "Inoshikacho": {
                "cards": [("萩", 0), ("紅", 0), ("牡", 0)],  # 7月猪、10月鹿、6月蝶
                "score": 2000
            },
            "Hanami": {
                "cards": [("桜", 0), ("菊", 0)],  # 3月光、9月酒
                "score": 500,
                "requires_only": 2
            },
            "Tsukimi": {
                "cards": [("芒", 0), ("菊", 0)],  # 8月光、9月酒
                "score": 500,
                "requires_only": 2
            }
        }
        
        # 光札の定義（三光判定用）
        self.light_cards = [("松", 0), ("桜", 0), ("芒", 0), ("桐", 0)]  # 1月、3月、8月、12月の光
        
        # 花札デッキの初期化（月とカード番号のペア）
        self.deck = []
        self.init_deck()
        
        pyxel.run(self.update, self.draw)

    def load_hanafuda_images(self):
        """
        花札の画像データを読み込みます
        my_resource.pyxres ファイルを使用します
        イメージバンク0: 1～6月の花札（3段目まで）
        イメージバンク1: 7～12月の花札（4～6段目）
        """
        try:
            # hanafuda_resource.pyxres ファイルを読み込み
            pyxel.load("my_resource.pyxres")
            self.use_image_bank = True
            print("my_resource.pyxres を読み込みました")
        except:
            self.use_image_bank = False
            print("my_resource.pyxres が見つかりません。")
            print("テキスト表示モードで実行します。")

    def init_deck(self):
        """デッキを初期化"""
        self.deck = []
        for month_idx, month in enumerate(self.months):
            for card_num in range(4):  # 各月4枚
                self.deck.append((month, month_idx, card_num))
        random.shuffle(self.deck)
    
    def create_particles(self, x, y, card_color=None, is_special=False):
        """パーティクルを生成"""
        particle_count = 15 if is_special else 8
        
        # 特殊役の場合はより派手な色を使用
        if is_special:
            colors = [8, 9, 10, 11, 12, 14, 15]  # より鮮やかな色
        else:
            colors = [7, 8, 10, 11, 14]  # 通常の色
        
        for _ in range(particle_count):
            # カードの中央付近からパーティクルを発生
            px = x + self.card_width // 2 + random.randint(-8, 8)
            py = y + self.card_height // 2 + random.randint(-8, 8)
            color = random.choice(colors)
            self.particles.append(Particle(px, py, color))
    
    def update(self):
        if self.game_state == "title":
            self.update_title()
        elif self.game_state == "playing":
            self.update_playing()
        elif self.game_state == "game_over":
            self.update_game_over()

    def update_title(self):
        """タイトル画面の更新"""
        self.title_timer += 1
        
        # キー入力またはマウスクリックでゲーム開始
        if (pyxel.btnp(pyxel.KEY_RETURN) or 
            pyxel.btnp(pyxel.KEY_SPACE) or 
            pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)):
            self.start_game()

    def update_playing(self):
        """プレイ中の更新"""
        # パーティクルの更新
        self.particles = [p for p in self.particles if p.update()]
        
        # ボーナスタイム管理
        if self.bonus_timer > 0:
            self.bonus_timer -= 1
            if self.bonus_timer == 0:
                self.bonus_multiplier = 1
        
        # 役成立メッセージ管理
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer == 0:
                self.combo_message = ""
        
        # 花札のスポーン
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval and len(self.cards) < self.max_cards:
            self.spawn_card()
            self.spawn_timer = 0
            
            # 時間経過で難易度上昇
            if self.spawn_interval > 30:  # 最小0.5秒
                self.spawn_interval = max(30, self.spawn_interval - 1)
        
        # マウス・タッチ入力処理
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.handle_click(pyxel.mouse_x, pyxel.mouse_y)
        
        # ゲームオーバー判定
        if len(self.cards) >= self.max_cards:
            self.game_state = "game_over"
            pyxel.play(0, 0)

    def update_game_over(self):
        """ゲームオーバー画面の更新"""
        # パーティクルの更新（ゲームオーバー画面でも継続）
        self.particles = [p for p in self.particles if p.update()]
        
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.restart_game()

    def start_game(self):
        """ゲームを開始"""
        self.game_state = "playing"
        self.cards = []
        self.selected_cards = []
        self.score = 0
        self.spawn_timer = 0
        self.spawn_interval = 90
        self.bonus_timer = 0
        self.bonus_multiplier = 1
        self.combo_message = ""
        self.combo_timer = 0
        self.particles = []  # パーティクルもリセット
        self.init_deck()
    
    def spawn_card(self):
        if not self.deck:
            # デッキが空の場合、新しくシャッフル
            self.init_deck()
        
        month, month_idx, card_num = self.deck.pop()
        
        # 空いている位置を探す
        available_positions = []
        for row in range(self.max_rows):
            for col in range(self.cards_per_row):
                x = col * self.card_width
                y = row * self.card_height
                
                # この位置に既に花札があるかチェック
                position_occupied = False
                for card in self.cards:
                    if card['x'] == x and card['y'] == y:
                        position_occupied = True
                        break
                
                if not position_occupied:
                    available_positions.append((x, y))
        
        # ランダムに位置を選択
        if available_positions:
            x, y = random.choice(available_positions)
            
            self.cards.append({
                'month': month,
                'month_idx': month_idx,
                'card_num': card_num,
                'x': x,
                'y': y,
                'selected': False
            })
    
    def handle_click(self, mouse_x, mouse_y):
        for card in self.cards:
            if (card['x'] <= mouse_x <= card['x'] + self.card_width and
                card['y'] <= mouse_y <= card['y'] + self.card_height):
                
                if card['selected']:
                    # 既に選択されている場合は選択解除
                    card['selected'] = False
                    self.selected_cards.remove(card)
                else:
                    # 新しく選択
                    if len(self.selected_cards) < 3:
                        card['selected'] = True
                        self.selected_cards.append(card)
                        
                        # 3枚選択されたら消去判定
                        if len(self.selected_cards) == 3:
                            self.check_completion()
                        # 2枚選択されたら2枚役の判定も行う
                        elif len(self.selected_cards) == 2:
                            special_score, combo_name = self.check_special_combinations()
                            if special_score > 0:
                                self.check_completion()
                break
    
    def check_completion(self):
        # 特殊役の判定
        special_score, combo_name = self.check_special_combinations()
        
        is_special_combo = False
        
        if special_score > 0:
            self.score += special_score * self.bonus_multiplier
            # 特殊役表示用のメッセージを設定
            self.show_combo_message(combo_name, special_score)
            is_special_combo = True
            
            if special_score >= 1000:  # 高得点役の場合
                self.bonus_timer = 600  # 10秒間
                self.bonus_multiplier = 2
        else:
            # 同じ月の3枚消しかチェック
            if len(self.selected_cards) == 3 and self.is_same_month_combo():
                self.score += 100 * self.bonus_multiplier
            else:
                # 無効な組み合わせの場合、選択をリセットして終了
                self.reset_selection()
                return
        
        # パーティクル生成（カードが消える前に）
        for card in self.selected_cards:
            self.create_particles(card['x'], card['y'], is_special=is_special_combo)
        
        # 選択された花札を削除
        for card in self.selected_cards:
            self.cards.remove(card)
            pyxel.play(0, 2)
        
        self.reset_selection()
    
    def is_same_month_combo(self):
        """選択されたカードが全て同じ月かチェック"""
        if len(self.selected_cards) != 3:
            return False
        
        first_month = self.selected_cards[0]['month']
        return all(card['month'] == first_month for card in self.selected_cards)
    
    def check_special_combinations(self):
        """特殊役の判定を行う"""
        selected_cards_info = []
        
        # 選択されたカードの情報を整理
        for card in self.selected_cards:
            month = card['month']
            card_num = card['card_num']
            card_type = self.card_types[month][card_num]
            selected_cards_info.append((month, card_num, card_type))
        
        # 三光の特別判定（光札3枚の組み合わせ、重複OK）
        if len(self.selected_cards) == 3:
            light_count = 0
            
            for month, card_num, card_type in selected_cards_info:
                if (month, card_num) in self.light_cards:
                    light_count += 1
            
            # 3枚全てが光札の場合
            if light_count == 3:
                return 1000, "Sanko"
        
        # 青タンの特別判定（重複OK）
        if len(self.selected_cards) == 3:
            aotan_count = 0
            for month, card_num, card_type in selected_cards_info:
                if card_type == "Aotan":
                    aotan_count += 1
            
            if aotan_count == 3:
                return 800, "Aotan"
        
        # 赤タンの特別判定（重複OK）
        if len(self.selected_cards) == 3:
            akatan_count = 0
            for month, card_num, card_type in selected_cards_info:
                if card_type == "Akatan":
                    akatan_count += 1
            
            if akatan_count == 3:
                return 800, "Akatan"
        
        # 通常の役をチェック（猪鹿蝶、花見で一杯、月見で一杯は従来通り）
        for combo_name, combo_data in self.special_combinations.items():
            # 青タンと赤タンは上で処理済みなのでスキップ
            if combo_name in ["Aotan", "Akatan"]:
                continue
                
            required_cards = combo_data["cards"]
            score = combo_data["score"]
            requires_only = combo_data.get("requires_only", 3)
            
            # 選択されたカード数が要求数と一致するかチェック
            if len(self.selected_cards) != requires_only:
                continue
            
            # 必要なカードが全て揃っているかチェック
            if self.check_cards_match(selected_cards_info, required_cards):
                return score, combo_name
        
        return 0, ""
    
    def check_cards_match(self, selected_cards_info, required_cards):
        """選択されたカードが必要なカードと一致するかチェック"""
        # 必要なカードのリストをコピー
        required_copy = required_cards.copy()
        
        # 選択されたカード情報をチェック
        for month, card_num, card_type in selected_cards_info:
            # 必要なカードリストから一致するものを探す
            found = False
            for i, (req_month, req_card_num) in enumerate(required_copy):
                if month == req_month and card_num == req_card_num:
                    required_copy.pop(i)  # 見つかったら削除
                    found = True
                    break
            
            if not found:
                return False
        
        # 全ての必要なカードが見つかった場合
        return len(required_copy) == 0
    
    def show_combo_message(self, combo_name, score):
        """役の成立メッセージを表示"""
        self.combo_message = f"{combo_name} - {score}点!"
        self.combo_timer = 60  # 2秒間表示
    
    def reset_selection(self):
        for card in self.selected_cards:
            card['selected'] = False
        self.selected_cards = []
    
    def restart_game(self):
        """ゲームをリスタート（タイトル画面に戻る）"""
        self.game_state = "title"
        self.title_timer = 0
        self.particles = []  # パーティクルもクリア
    
    def draw(self):
        pyxel.cls(0)
        
        if self.game_state == "title":
            self.draw_title()
        elif self.game_state == "playing":
            self.draw_playing()
        elif self.game_state == "game_over":
            self.draw_game_over()

    def draw_title(self):
        """タイトル画面の描画"""
        pyxel.cls(3)  # 濃い青の背景
        
        # タイトルロゴ
        title_text = "HANAFUDA PON"
        title_x = 128 - len(title_text) * 4 // 2
        
        # タイトルの影
        pyxel.text(title_x + 1, 61, title_text, 0)
        pyxel.text(title_x, 60, title_text, 10)
        
        # サブタイトル
        subtitle = "Matching Game"
        sub_x = 128 - len(subtitle) * 4 // 2
        pyxel.text(sub_x, 80, subtitle, 14)
        
        # 花札の装飾表示（タイトル画面用）
        for i in range(6):
            x = 40 + i * 30
            y = 100 + math.sin(self.title_timer * 0.05 + i * 0.5) * 5
            
            month_idx = i * 2
            if month_idx < len(self.months):
                if hasattr(self, 'use_image_bank') and self.use_image_bank:
                    # リソース画像を使用して装飾用花札を描画
                    card_num = 0  # 各月の最初のカード（光札など）を使用
                    
                    # 画像の位置を計算（ゲーム本体と同じロジック）
                    if month_idx < 6:  # 1-6月
                        img_bank = 0
                        row = month_idx // 2
                        col_base = (month_idx % 2) * 4
                        img_x = (col_base + card_num) * self.card_width
                        img_y = row * self.card_height
                    else:  # 7-12月
                        img_bank = 1
                        adjusted_month = month_idx - 6
                        row = adjusted_month // 2
                        col_base = (adjusted_month % 2) * 4
                        img_x = (col_base + card_num) * self.card_width
                        img_y = row * self.card_height
                    
                    # 小さめのサイズで描画（縮小して表示）
                    card_w, card_h = 32, 53
                    pyxel.blt(x, y, img_bank, img_x, img_y, card_w, card_h, None, None, 0.6)
                else:
                    # 画像データがない場合は従来の描画方法
                    month = self.months[month_idx]
                    pyxel.rect(x, y, 20, 32, 7)
                    pyxel.rectb(x, y, 20, 32, 1)
                    pyxel.text(x + 6, y + 12, month, 8)
        
        # 操作説明
        instructions = [
            "How to Play:",
            "Same month: Select 3 cards",
            "Special combos: Select specific cards",
            "Akatan/Aotan: 800pt  Inoshikacho: 2000pt",
            "Sanko: 1000pt  Hanami/Tsukimi: 500pt",
            "",
            "SPACE or CLICK to Start"
        ]
        
        start_y = 150
        for i, instruction in enumerate(instructions):
            text_x = 128 - len(instruction) * 4 // 2
            color = 7 if i == len(instructions) - 1 else 7
            
            # 最後の行（スタート案内）を点滅させる
            if i == len(instructions) - 1:
                if (self.title_timer // 4) % 2 == 0:
                    pyxel.text(text_x, start_y + i * 10, instruction, color)
            else:
                pyxel.text(text_x, start_y + i * 10, instruction, color)

    def draw_playing(self):
        """プレイ中の描画"""
        # 花札を描画
        for card in self.cards:
            if hasattr(self, 'use_image_bank') and self.use_image_bank:
                # 画像データを使用して描画
                month_idx = card['month_idx']  # 0-11 (1月-12月)
                card_num = card['card_num']    # 0-3 (各月の1-4枚目)
                
                if month_idx < 6:  # 1-6月
                    img_bank = 0
                    row = month_idx // 2  # 0,1,2行目
                    col_base = (month_idx % 2) * 4  # 0または4
                    img_x = (col_base + card_num) * self.card_width
                    img_y = row * self.card_height
                else:  # 7-12月
                    img_bank = 1
                    adjusted_month = month_idx - 6
                    row = adjusted_month // 2  # 0,1,2行目
                    col_base = (adjusted_month % 2) * 4  # 0または4
                    img_x = (col_base + card_num) * self.card_width
                    img_y = row * self.card_height
                
                # 花札を描画
                pyxel.blt(card['x'], card['y'], img_bank, img_x, img_y, self.card_width, self.card_height)
                
                # 選択状態の表示
                if card['selected']:
                    pyxel.rectb(card['x'], card['y'], self.card_width, self.card_height, 11)
                    pyxel.rectb(card['x']+1, card['y']+1, self.card_width-2, self.card_height-2, 11)
            else:
                # 画像データがない場合は従来の描画方法
                color = 11 if card['selected'] else 7
                pyxel.rect(card['x'], card['y'], self.card_width, self.card_height, color)
                pyxel.rectb(card['x'], card['y'], self.card_width, self.card_height, 1)
                
                # 月の文字を描画
                text_x = card['x'] + self.card_width // 2 - 4
                text_y = card['y'] + self.card_height // 2 - 4
                pyxel.text(text_x, text_y, card['month'], 1)
                
                # カード番号も表示
                num_text = str(card['card_num'] + 1)
                pyxel.text(card['x'] + 2, card['y'] + 2, num_text, 8)
        
        # パーティクルを描画
        for particle in self.particles:
            particle.draw()
        
        # UI表示
        score_text = f"SCORE: {self.score:06d}"
        pyxel.text(8, 230, score_text, 7)
        
        if self.bonus_timer > 0:
            pyxel.text(8, 220, "BONUS x2!", 10)
        
        # 役成立メッセージの表示
        if self.combo_message and self.combo_timer > 0:
            msg_x = 128 - len(self.combo_message) * 4 // 2
            # 背景
            pyxel.rect(msg_x - 4, 46, len(self.combo_message) * 4 + 8, 12, 0)
            pyxel.rectb(msg_x - 4, 46, len(self.combo_message) * 4 + 8, 12, 11)
            # テキスト
            pyxel.text(msg_x, 50, self.combo_message, 11)
        
        if self.selected_cards:
            if len(self.selected_cards) == 1:
                selected_text = f"選択: {len(self.selected_cards)}/3 ({self.selected_cards[0]['month']})"
            else:
                months = [card['month'] for card in self.selected_cards]
                selected_text = f"選択: {len(self.selected_cards)}/3 ({', '.join(months)})"
            pyxel.text(8, 200, selected_text, 12)
        
        # マウスカーソル描画
        self.draw_cursor()

    def draw_game_over(self):
        """ゲームオーバー画面の描画"""
        # ゲーム画面を暗く表示
        self.draw_playing()
        
        # オーバーレイ
        pyxel.rect(0, 0, 256, 240, 0)
        
        # ゲームオーバーボックス
        box_x, box_y = 64, 80
        box_w, box_h = 128, 80
        
        pyxel.rect(box_x, box_y, box_w, box_h, 1)
        pyxel.rectb(box_x, box_y, box_w, box_h, 7)
        
        # テキスト
        pyxel.text(100, 100, "GAME OVER", 8)
        
        final_score_text = f"FINAL SCORE: {self.score}"
        score_x = 128 - len(final_score_text) * 4 // 2
        pyxel.text(score_x, 120, final_score_text, 7)
        
        restart_text = "Click to Return to Title"
        restart_x = 128 - len(restart_text) * 4 // 2
        pyxel.text(restart_x, 140, restart_text, 11)

    def draw_cursor(self):
        """マウスカーソルの描画"""
        mouse_x = pyxel.mouse_x
        mouse_y = pyxel.mouse_y
        
        # カーソルが画面内にある場合のみ描画
        if 0 <= mouse_x < 256 and 0 <= mouse_y < 240:
            # シンプルな十字カーソル
            pyxel.line(mouse_x - 3, mouse_y, mouse_x + 3, mouse_y, 7)
            pyxel.line(mouse_x, mouse_y - 3, mouse_x, mouse_y + 3, 7)
            pyxel.pset(mouse_x, mouse_y, 11)

if __name__ == "__main__":
    HanafudaPon()