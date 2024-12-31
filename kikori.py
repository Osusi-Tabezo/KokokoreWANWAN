import json
import pyxel

# 音楽のパス
MUSIC_FILE = "music/game"

# シーン番号の定義
SNO_TITLE = 0
SNO_STAGESET = 10
SNO_PLAY = 11
SNO_SFINISH = 12
SNO_END = 20

scene = SNO_TITLE  # ゲームの進行を管理する変数
tmr = 0  # シーン内でカウントするタイマー変数

# イヌの状態 0:通常 1:斬る 2:ダメージ
ply_state = 0
PLY_ANIM_NORMAL = 0
PLY_ANIM_SLASH = 1
PLY_ANIM_DAMAGE = 2
# イヌの位置 0:左 1:右
ply_pos = 0
PLY_POS_LEFT = 0
PLY_POS_RIGHT = 1

# アニメーション管理用
animation_timer = 0
ply_ani = 0
FRAME_INTERVAL = 15

PLY_ANIM = [(0, 0), (16, 0)]
PLY_END_ANIM = [(0, 64), (16, 64), (0, 64), (16, 64)]

# 木 0:ノーマル 1:茨(左) 2:茨(右) 3:虫(左) 4:虫(右)
TREE = [
    0,
    0,
    0,
    0,
    0,
    0,
    1,
    0,
    3,
    0,
    2,
    0,
    2,
    0,
    1,
    0,
    4,
    0,
    4,
    4,
    0,
    4,
    0,
    1,
    0,
    1,
    0,
    4,
    0,
    2,
    0,
    4,
    0,
    0,
    3,
    0,
    4,
    0,
    3,
    0,
    2,
    0,
    3,
    0,
    2,
    0,
    3,
    0,
    2,
    0,
    0,
    3,
    0,
    3,
    0,
    1,
    0,
    3,
    0,
    0,
    2,
    0,
    3,
    0,
    1,
    0,
    3,
    0,
    4,
    0,
    1,
    0,
    2,
    0,
    2,
    0,
    1,
    0,
    3,
    0,
    3,
    0,
    1,
    0,
    2,
    0,
    4,
    0,
    3,
    0,
    4,
    0,
    4,
    0,
    4,
    0,
    1,
    0,
    2,
    0,
]
tree_work = [0]
TREE_NORMAL = 0
TREE_THORN_LEFT = 1
TREE_THORN_RIGHT = 2
TREE_BUG_LEFT = 3
TREE_BUG_RIGHT = 4
# 各木とイヌの位置の対照表 TREE_TABLE[TREE][ply_pos] 0:何もなし 1:ダメージ
# 0,0
# 1,0
# 0,1
# 0,1
# 1,0
TREE_TABLE = [[0, 0], [1, 0], [0, 1], [0, 1], [1, 0]]
TREE_TABLE_NORMAL = 0
TREE_TABLE_DAMAGE = 1

# 今一番下にある木
slash_point = 0

# コンボ
combo = 0
max_combo = 0
current_combo_time = 0
COMBO_TIME = 30

# 制限時間
TIME_LIMIT = 60

# デバッグモード
DEBUG_MODE = False


class App:
    def __init__(self):
        # ここで起動時の処理をします
        pyxel.init(80, 80, title="Kokokore WANWAN")
        pyxel.load("kikori.pyxres")
        pyxel.run(self.update, self.draw)

    def update(self):
        # ここで毎フレームの更新作業をします
        global scene, tmr, ply_state, animation_timer, ply_ani, ply_pos, tree_work, slash_point, combo, max_combo, current_combo_time
        tmr += 1

        if scene == SNO_TITLE:
            ply_ani += 1

            if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
                scene = SNO_STAGESET
                ply_ani = 0
                tmr = 0

        elif scene == SNO_STAGESET:
            if tmr == 1:
                pyxel.play(3, 6)
                tree_work = TREE[:]
                combo = 0
                max_combo = 0
                current_combo_time = 0
                ply_pos = 0
                slash_point = 0
                ply_ani = 0

            # カウントダウン
            if 30 * 3 == tmr:
                pyxel.play(3, 7)
            elif 30 * 2 == tmr:
                pyxel.play(3, 6)
            elif 30 * 1 == tmr:
                pyxel.play(3, 6)

            if 30 * 4 < tmr:
                tmr = 0
                scene = SNO_PLAY

                with open(f"./{MUSIC_FILE}.json", "rt") as fin:
                    self.music = json.loads(fin.read())

                for ch, sound in enumerate(self.music):
                    pyxel.sounds[ch].set(*sound)
                    pyxel.play(ch, ch, loop=True)
                pyxel.load("kikori.pyxres")

        elif scene == SNO_PLAY:
            # ダメージ判定 一番最初に置かないとボタン押しっぱなしで避けられる
            if (
                ply_state == PLY_ANIM_NORMAL
                and slash_point < len(tree_work)
                and TREE_TABLE[tree_work[slash_point]][ply_pos] == TREE_TABLE_DAMAGE
            ):
                ply_state = PLY_ANIM_DAMAGE
                pyxel.play(3, 0)
                # ダメージ食らったら今の木をノーマルに戻す
                tree_work[slash_point] = 0
                # コンボ終了
                combo = 0
                current_combo_time = 0

            # 移動
            if (
                pyxel.btn(pyxel.KEY_RIGHT)
                or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
                and ply_pos == PLY_POS_LEFT
            ) and ply_state == PLY_ANIM_NORMAL:
                # 右に移動
                ply_pos = PLY_POS_RIGHT

            if (
                pyxel.btn(pyxel.KEY_LEFT)
                or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)
                and ply_pos == PLY_POS_RIGHT
            ) and ply_state == PLY_ANIM_NORMAL:
                # 左に移動
                ply_pos = PLY_POS_LEFT

            # 斬る
            if (
                pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B)
            ) and ply_state == PLY_ANIM_NORMAL:
                ply_state = PLY_ANIM_SLASH
                pyxel.play(3, 1)

                slash_point += 1

                # コンボ追加
                combo += 1
                if combo > max_combo:
                    max_combo = combo

                current_combo_time = COMBO_TIME

            # コンボ
            if current_combo_time > 0:
                current_combo_time -= 1
            elif current_combo_time == 0:
                combo = 0

            # 終了判定
            if slash_point == len(TREE) or TIME_LIMIT == (tmr // 30):
                scene = SNO_SFINISH
                tmr = 0

        elif scene == SNO_SFINISH:
            if ply_state == PLY_ANIM_NORMAL:
                if FRAME_INTERVAL == tmr:
                    pyxel.stop()
                    pyxel.play(3, 2)

                # 5秒経過後にステージ更新(1秒30フレームなので3倍待つ)
                if 30 * 5 < tmr:
                    scene = SNO_END
                    tmr = 0

        elif scene == SNO_END:
            ply_ani += 1

            if tmr == 1:
                pyxel.playm(0)

            if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
                scene = SNO_TITLE
                pyxel.stop()
                ply_ani = 0
                tmr = 0

        if ply_state != PLY_ANIM_NORMAL:
            animation_timer += 1
            if animation_timer >= FRAME_INTERVAL:
                animation_timer = 0
                ply_state = PLY_ANIM_NORMAL  # アニメーション終了

    def draw(self):
        # ここで毎フレームの描画作業をします
        pyxel.cls(0)
        # pyxel.bltm(0, 0, 0, 0, 0, 128, 128)

        if scene == SNO_TITLE:
            # pyxel.blt(30, 16, 1, 0, 0, 64, 32, 0)

            pyxel.blt(8, 0, 1, 0, 0, 64, 32, 0)
            u, v = PLY_ANIM[pyxel.frame_count // 15 % 2]
            pyxel.blt(28, 35, 0, u, v, 16, 16, 0)
            pyxel.text(16, 54, "PRESS [SPACE]", 7)
            pyxel.text(20, 62, "GAME START", 7)

            pyxel.text(5, 72, "2024 OSUSHI TABEZO", 7)

        if scene == SNO_STAGESET or scene == SNO_PLAY or scene == SNO_SFINISH:
            # 木の描画
            tree_index = 0
            # [slash_point:]で配列の途中からループを開始する
            for wk_tree in tree_work[slash_point:]:
                if wk_tree == TREE_NORMAL:
                    # 普通の木
                    pyxel.blt(33, 60 - (16 * tree_index), 0, 0, 16, 16, 16, 0)
                elif wk_tree == TREE_THORN_LEFT:
                    # 茨の木(左)
                    pyxel.blt(33, 60 - (16 * tree_index), 0, 16, 16, 16, 16, 0)
                    pyxel.blt(19, 60 - (16 * tree_index), 0, 16, 32, 16, 16, 0)
                elif wk_tree == TREE_THORN_RIGHT:
                    # 茨の木(右)
                    pyxel.blt(33, 60 - (16 * tree_index), 0, 16, 16, 16, 16, 0)
                    pyxel.blt(47, 60 - (16 * tree_index), 0, 16, 32, -16, 16, 0)
                elif wk_tree == TREE_BUG_LEFT:
                    # 虫系は二つ前に移動予兆、一つ前で反対側に移動する
                    # 虫の木(左)
                    pyxel.blt(33, 60 - (16 * tree_index), 0, 32, 16, 16, 16, 0)
                    if tree_index <= 1:
                        pyxel.blt(47, 60 - (16 * tree_index), 0, 32, 32, -8, 16, 0)
                    elif tree_index == 2:
                        pyxel.blt(27, 60 - (16 * tree_index), 0, 40, 32, 8, 16, 0)
                    else:
                        pyxel.blt(27, 60 - (16 * tree_index), 0, 32, 32, 8, 16, 0)
                elif wk_tree == TREE_BUG_RIGHT:
                    # 虫の木(右)
                    pyxel.blt(33, 60 - (16 * tree_index), 0, 32, 16, 16, 16, 0)
                    if tree_index <= 1:
                        pyxel.blt(27, 60 - (16 * tree_index), 0, 32, 32, 8, 16, 0)
                    elif tree_index == 2:
                        pyxel.blt(47, 60 - (16 * tree_index), 0, 40, 32, -8, 16, 0)
                    else:
                        pyxel.blt(47, 60 - (16 * tree_index), 0, 32, 32, -8, 16, 0)

                tree_index += 1
            pyxel.blt(33, 73, 0, 48, 16, 16, 16, 0)

            # プレイヤーの描画
            u, v = PLY_ANIM[pyxel.frame_count // 15 % 2]

            # プレイヤーの場所によって反転
            if ply_pos == PLY_POS_LEFT:
                x = 15
                w = 1
            else:
                x = 51
                w = -1

            if ply_state == PLY_ANIM_NORMAL:
                pyxel.blt(x, 60, 0, u, v, w * 16, 16, 0)
            elif ply_state == PLY_ANIM_SLASH:
                pyxel.blt(x + (8 * w), 60, 0, 32, 0, w * 16, 16, 0)
            elif ply_state == PLY_ANIM_DAMAGE:
                pyxel.blt(x, 60, 0, 48, 0, w * 16, 16, 0)

            # 開始時のカウントダウン
            if scene == SNO_STAGESET:
                if tmr > 30 * 3:
                    pyxel.text(30, 30, "START!!", 7)
                elif tmr > 30 * 2:
                    pyxel.text(40, 30, "1", 7)
                elif tmr > 30 * 1:
                    pyxel.text(40, 30, "2", 7)
                else:
                    pyxel.text(40, 30, "3", 7)

            # 制限時間
            if scene == SNO_PLAY:
                pyxel.text(0, 2, "TIME:" + str(TIME_LIMIT - (tmr // 30)), 7)
                # コンボ
                if combo != 0:
                    if combo < 10:
                        pyxel.text(60, 2, str(combo), 7)
                    else:
                        pyxel.text(58, 2, str(combo), 7)

                    pyxel.text(52, 10, "COMBO", 7)

            if scene == SNO_SFINISH:
                pyxel.text(28, 30, "FINISH!", 7)

        if scene == SNO_END:

            u, v = PLY_END_ANIM[ply_ani // 15 % 4]
            pyxel.text(16, 8, "RESULT", 7)
            pyxel.text(16, 18, "POINT " + str(slash_point), 7)
            pyxel.text(16, 26, "MAX COMBO  " + str(max_combo), 7)
            if max_combo == len(TREE):
                pyxel.text(26, 34, "PERFECT!", 10)

            pyxel.blt(33, 60, 0, u, v, 16, 16, 0)

            pyxel.text(16, 42, "PRESS [SPACE]", 7)
            pyxel.text(16, 50, "BACK TO TITLE", 7)

        # デバッグ用
        if DEBUG_MODE:
            pyxel.text(0, 0, "ply_pos:" + str(ply_pos), 7)
            pyxel.text(0, 8, "slash_point:" + str(slash_point), 7)
            pyxel.text(0, 16, "combo:" + str(combo), 7)
            pyxel.text(0, 24, "max_combo:" + str(max_combo), 7)
            pyxel.text(0, 32, "combo_time:" + str(current_combo_time), 7)

            if scene == SNO_SFINISH:
                pyxel.text(0, 40, "FINISH", 7)


App()
