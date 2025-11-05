import turtle
import time
import random
import sqlite3
import winsound
from enum import Enum

# 音频文件路径（需要用户提供实际.wav文件）
MOVE_SOUND_FILE = "move.wav"
LEVEL_UP_SOUND_FILE = "level_up.wav"
COLLISION_SOUND_FILE = "collision.wav"

# 定义游戏状态
class GameState(Enum):
    MAIN_MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4
    SHOP = 5

# 全局变量
current_state = GameState.MAIN_MENU

# 游戏设置
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

# 数据库设置
DB_NAME = "turtle_crossing.db"

# 音频文件路径（需要用户提供实际文件）
BGM_FILE = "bgm.mp3"
MOVE_SOUND_FILE = "move.mp3"
LEVEL_UP_SOUND_FILE = "level_up.mp3"
COLLISION_SOUND_FILE = "collision.mp3"

# 创建屏幕
screen = turtle.Screen()
screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
screen.title("Turtle Crossing")
screen.bgcolor("black")
screen.tracer(0)  # 关闭自动更新

# 注册海龟行走GIF（需要用户提供实际文件）
# screen.addshape("turtle_walk1.gif")
# screen.addshape("turtle_walk2.gif")

# 数据库初始化
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 创建排行榜表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT,
            level INTEGER,
            score INTEGER,
            date DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建商店购买表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shop_purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            upgrade_type TEXT,
            purchased INTEGER DEFAULT 0
        )
    ''')
    
    # 初始化商店升级项
    cursor.execute('''
        INSERT OR IGNORE INTO shop_purchases (upgrade_type, purchased) VALUES
        ('speed_boost', 0),
        ('extra_life', 0)
    ''')
    
    conn.commit()
    conn.close()

# 主菜单绘制类
class MainMenu:
    def __init__(self):
        self.buttons = []
        self.selected_button = 0
        self.draw()
    
    def draw(self):
        screen.clear()
        
        # 绘制标题
        title = turtle.Turtle()
        title.color("#FF6600")
        title.penup()
        title.hideturtle()
        title.goto(0, 150)
        title.write("TURTLE CROSSING", align="center", font=("Arial", 30, "bold"))
        
        # 绘制按钮
        button_y = 50
        button_spacing = 60
        
        # 开始游戏按钮
        start_button = turtle.Turtle()
        start_button.shape("square")
        start_button.color("#00FF00", "#008000")
        start_button.shapesize(stretch_wid=2, stretch_len=10)
        start_button.penup()
        start_button.goto(0, button_y)
        self.buttons.append(start_button)
        
        start_text = turtle.Turtle()
        start_text.color("white")
        start_text.penup()
        start_text.hideturtle()
        start_text.goto(0, button_y)
        start_text.write("开始游戏", align="center", font=("Arial", 16, "bold"))
        
        button_y -= button_spacing
        
        # 排行榜按钮
        leaderboard_button = turtle.Turtle()
        leaderboard_button.shape("square")
        leaderboard_button.color("#00FFFF", "#0080FF")
        leaderboard_button.shapesize(stretch_wid=2, stretch_len=10)
        leaderboard_button.penup()
        leaderboard_button.goto(0, button_y)
        self.buttons.append(leaderboard_button)
        
        leaderboard_text = turtle.Turtle()
        leaderboard_text.color("white")
        leaderboard_text.penup()
        leaderboard_text.hideturtle()
        leaderboard_text.goto(0, button_y)
        leaderboard_text.write("排行榜", align="center", font=("Arial", 16, "bold"))
        
        button_y -= button_spacing
        
        # 商店按钮
        shop_button = turtle.Turtle()
        shop_button.shape("square")
        shop_button.color("#FF00FF", "#8000FF")
        shop_button.shapesize(stretch_wid=2, stretch_len=10)
        shop_button.penup()
        shop_button.goto(0, button_y)
        self.buttons.append(shop_button)
        
        shop_text = turtle.Turtle()
        shop_text.color("white")
        shop_text.penup()
        shop_text.hideturtle()
        shop_text.goto(0, button_y)
        shop_text.write("商店", align="center", font=("Arial", 16, "bold"))
        
        button_y -= button_spacing
        
        # 退出按钮
        exit_button = turtle.Turtle()
        exit_button.shape("square")
        exit_button.color("#FF0000", "#800000")
        exit_button.shapesize(stretch_wid=2, stretch_len=10)
        exit_button.penup()
        exit_button.goto(0, button_y)
        self.buttons.append(exit_button)
        
        exit_text = turtle.Turtle()
        exit_text.color("white")
        exit_text.penup()
        exit_text.hideturtle()
        exit_text.goto(0, button_y)
        exit_text.write("退出", align="center", font=("Arial", 16, "bold"))
    
    def check_click(self, x, y):
        for i, button in enumerate(self.buttons):
            button_x, button_y = button.position()
            if abs(x - button_x) < 100 and abs(y - button_y) < 20:
                return i
        return -1

# 玩家类
class TurtlePlayer(turtle.Turtle):
    def __init__(self):
        super().__init__()
        self.shape("turtle")
        self.color("#FF6600")
        self.penup()
        self.goto(0, -280)
        self.setheading(90)
        self.move_distance = 10
        self.current_frame = 1
    
    def up(self):
        self.forward(self.move_distance)
        # 播放移动音效
        try:
            winsound.PlaySound(MOVE_SOUND_FILE, winsound.SND_ASYNC)
        except Exception:
            pass  # 如果音效未加载，忽略
        # 切换行走动画帧
        # self.current_frame = 1 if self.current_frame == 2 else 2
        # self.shape(f"turtle_walk{self.current_frame}.gif")
    
    def reset(self):
        self.goto(0, -280)
    
    def get_bounds(self):
        # AABB碰撞检测：返回玩家的边界框
        x, y = self.position()
        return (x - 10, y - 10, x + 10, y + 10)

# 汽车类
class Car(turtle.Turtle):
    def __init__(self, x, y, color, speed):
        super().__init__()
        self.shape("square")
        self.color(color)
        self.shapesize(stretch_len=2, stretch_wid=1)
        self.penup()
        self.goto(x, y)
        self.setheading(180)
        self.speed = speed
    
    def move(self):
        self.forward(self.speed)
    
    def get_bounds(self):
        # AABB碰撞检测：返回汽车的边界框
        x, y = self.position()
        return (x - 20, y - 10, x + 20, y + 10)

# 汽车管理器类
class CarManager:
    def __init__(self):
        self.all_cars = []
        self.car_colors = ["#FFFF00", "#FF0000", "#00FF00", "#00FFFF", "#FF00FF"]
    
    def make_car(self, speed_multiplier=1.0):
        random_car = random.randint(1, 6)
        if random_car == 1:
            rand_y = random.randint(-200, 200)
            base_speed = 5
            car = Car(350, rand_y, random.choice(self.car_colors), base_speed * speed_multiplier)
            self.all_cars.append(car)
    
    def move_cars(self):
        for car in self.all_cars:
            car.move()
    
    def clear_cars(self):
        for car in self.all_cars:
            car.hideturtle()
        self.all_cars.clear()

# 分数类
class Score(turtle.Turtle):
    def __init__(self):
        super().__init__()
        self.color("white")
        self.penup()
        self.hideturtle()
        self.level = 1
        self.score = 0
        self.update_score()
    
    def update_score(self):
        self.clear()
        self.goto(-240, 260)
        self.write(f"Level: {self.level}", align="center", font=("Arial", 13, "normal"))
        self.goto(240, 260)
        self.write(f"Score: {self.score}", align="center", font=("Arial", 13, "normal"))
    
    def new_level(self):
        self.level += 1
        self.score += 10  # 每关奖励10分
        self.update_score()
        # 播放升级音效
        try:
            winsound.PlaySound(LEVEL_UP_SOUND_FILE, winsound.SND_ASYNC)
        except Exception:
            pass  # 如果音效未加载，忽略
    
    def game_over(self):
        self.goto(0, 0)
        self.write("GAME OVER", align="center", font=("Arial", 20, "bold"))

# 粒子效果类
class Particle(turtle.Turtle):
    def __init__(self, x, y):
        super().__init__()
        self.shape("circle")
        self.color(random.choice(["#FF0000", "#FF6600", "#FFFF00"]))
        self.shapesize(stretch_wid=0.5, stretch_len=0.5)
        self.penup()
        self.goto(x, y)
        self.speed = random.randint(5, 15)
        self.direction = random.randint(0, 360)
        self.setheading(self.direction)
    
    def move(self):
        self.forward(self.speed)
        self.speed *= 0.95  # 逐渐减速
    
    def is_dead(self):
        return self.speed < 0.5

# 粒子管理器类
class ParticleManager:
    def __init__(self):
        self.particles = []
    
    def create_explosion(self, x, y):
        for _ in range(30):
            particle = Particle(x, y)
            self.particles.append(particle)
    
    def update_particles(self):
        for particle in self.particles:
            particle.move()
            if particle.is_dead():
                particle.hideturtle()
                self.particles.remove(particle)

# 商店类
class Shop:
    def __init__(self):
        self.upgrades = [
            {"name": "速度提升", "type": "speed_boost", "cost": 50, "description": "永久提升10%移动速度"},
            {"name": "额外生命", "type": "extra_life", "cost": 100, "description": "获得额外1条生命"}
        ]
    
    def draw(self):
        screen.clear()
        
        # 绘制标题
        title = turtle.Turtle()
        title.color("#FF6600")
        title.penup()
        title.hideturtle()
        title.goto(0, 200)
        title.write("商店", align="center", font=("Arial", 24, "bold"))
        
        # 绘制当前分数
        score_text = turtle.Turtle()
        score_text.color("white")
        score_text.penup()
        score_text.hideturtle()
        score_text.goto(0, 150)
        score_text.write(f"当前分数: {score.score}", align="center", font=("Arial", 16, "bold"))
        
        # 绘制升级项
        y_pos = 100
        upgrade_spacing = 80
        
        for i, upgrade in enumerate(self.upgrades):
            # 检查是否已购买
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT purchased FROM shop_purchases WHERE upgrade_type = ?", (upgrade["type"],))
            purchased = cursor.fetchone()[0]
            conn.close()
            
            # 绘制升级按钮
            upgrade_button = turtle.Turtle()
            if purchased:
                upgrade_button.color("#808080", "#404040")
            else:
                upgrade_button.color("#00FF00", "#008000")
            upgrade_button.shape("square")
            upgrade_button.shapesize(stretch_wid=2, stretch_len=15)
            upgrade_button.penup()
            upgrade_button.goto(0, y_pos)
            upgrade_button.upgrade_type = upgrade["type"]  # 添加自定义属性
            upgrade_button.purchased = purchased
            
            # 绘制升级信息
            upgrade_info = turtle.Turtle()
            upgrade_info.color("white")
            upgrade_info.penup()
            upgrade_info.hideturtle()
            upgrade_info.goto(0, y_pos)
            
            if purchased:
                text = f"✓ {upgrade['name']} - 已购买"
            else:
                text = f"{upgrade['name']} - {upgrade['cost']}分"
            
            upgrade_info.write(text, align="center", font=("Arial", 14, "bold"))
            
            # 绘制升级描述
            desc_text = turtle.Turtle()
            desc_text.color("#808080")
            desc_text.penup()
            desc_text.hideturtle()
            desc_text.goto(0, y_pos - 25)
            desc_text.write(upgrade["description"], align="center", font=("Arial", 12, "normal"))
            
            y_pos -= upgrade_spacing
        
        # 返回主菜单按钮
        back_button = turtle.Turtle()
        back_button.shape("square")
        back_button.color("#00FFFF", "#0080FF")
        back_button.shapesize(stretch_wid=1.5, stretch_len=8)
        back_button.penup()
        back_button.goto(0, -200)
        
        back_text = turtle.Turtle()
        back_text.color("white")
        back_text.penup()
        back_text.hideturtle()
        back_text.goto(0, -200)
        back_text.write("返回主菜单", align="center", font=("Arial", 14, "bold"))
    
    def handle_click(self, x, y):
        global current_state
        
        # 检查返回主菜单按钮
        if abs(x) < 80 and abs(y + 200) < 15:
            current_state = GameState.MAIN_MENU
            screen.clear()
            main_menu.draw()
            screen.onclick(handle_click)
            return
        
        # 检查升级按钮
        y_pos = 100
        upgrade_spacing = 80
        
        for i, upgrade in enumerate(self.upgrades):
            if abs(x) < 150 and abs(y - y_pos) < 20:
                # 点击了该升级项
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("SELECT purchased FROM shop_purchases WHERE upgrade_type = ?", (upgrade["type"],))
                purchased = cursor.fetchone()[0]
                
                if not purchased and score.score >= upgrade["cost"]:
                    # 购买升级
                    cursor.execute("UPDATE shop_purchases SET purchased = 1 WHERE upgrade_type = ?", (upgrade["type"],))
                    score.score -= upgrade["cost"]
                    
                    # 应用升级效果
                    if upgrade["type"] == "speed_boost":
                        player.move_distance *= 1.1  # 提升10%速度
                    elif upgrade["type"] == "extra_life":
                        # 实现额外生命逻辑（需要在游戏中添加生命系统）
                        pass
                    
                    conn.commit()
                    conn.close()
                    
                    # 重新绘制商店
                    self.draw()
                    return
                
                conn.close()
            
            y_pos -= upgrade_spacing

# 初始化游戏组件
init_db()
main_menu = MainMenu()
player = TurtlePlayer()
cars = CarManager()
score = Score()
particle_manager = ParticleManager()
shop = Shop()

# 游戏循环
previous_state = None
def game_loop():
    global current_state, previous_state
    
    screen.update()
    
    # 状态切换处理
    if current_state != previous_state:
        # 清除当前界面
        screen.clear()
        screen.bgcolor("white")
        screen.onclick(None)  # 移除所有点击事件
        
        if current_state == GameState.PLAYING:
            # 进入游戏状态
            player.reset()
            cars.clear_cars()
            score.__init__()
            particle_manager.reset()
        
        elif current_state == GameState.PAUSED:
            # 进入暂停状态
            pass
        
        elif current_state == GameState.GAME_OVER:
            # 进入游戏结束状态
            # 将分数添加到排行榜
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO leaderboard (player_name, level, score) VALUES (?, ?, ?)",
                          ("Player", score.level, score.score))
            conn.commit()
            conn.close()
            
            # 显示游戏结束信息
            game_over_text = turtle.Turtle()
            game_over_text.color("#FF0000")
            game_over_text.penup()
            game_over_text.hideturtle()
            game_over_text.goto(0, 0)
            game_over_text.write("GAME OVER", align="center", font=("Arial", 24, "bold"))
            
            # 显示最终分数
            final_score_text = turtle.Turtle()
            final_score_text.color("black")
            final_score_text.penup()
            final_score_text.hideturtle()
            final_score_text.goto(0, -50)
            final_score_text.write(f"最终关卡: {score.level} - 最终分数: {score.score}", align="center", font=("Arial", 16, "bold"))
            
            # 返回主菜单按钮
            back_button = turtle.Turtle()
            back_button.shape("square")
            back_button.color("#00FF00", "#008000")
            back_button.shapesize(stretch_wid=1.5, stretch_len=8)
            back_button.penup()
            back_button.goto(0, -150)
            
            back_text = turtle.Turtle()
            back_text.color("white")
            back_text.penup()
            back_text.hideturtle()
            back_text.goto(0, -150)
            back_text.write("返回主菜单", align="center", font=("Arial", 14, "bold"))
            
            def back_to_menu(x, y):
                global current_state
                current_state = GameState.MAIN_MENU
                screen.clear()
                main_menu.draw()
                screen.onclick(handle_click)
            
            screen.onclick(back_to_menu)
        
        elif current_state == GameState.SHOP:
            # 进入商店状态
            shop.draw()
            screen.onclick(shop.handle_click)
        
        previous_state = current_state
    
    # 状态持续处理
    if current_state == GameState.MAIN_MENU:
        # 主菜单逻辑
        pass
    
    elif current_state == GameState.PLAYING:
        # 游戏中逻辑
        cars.make_car(speed_multiplier=1.0 + (score.level - 1) * 0.1)
        cars.move_cars()
        
        # 碰撞检测（AABB）
        player_bounds = player.get_bounds()
        for car in cars.all_cars:
            car_bounds = car.get_bounds()
            if (player_bounds[0] < car_bounds[2] and player_bounds[2] > car_bounds[0] and
                player_bounds[1] < car_bounds[3] and player_bounds[3] > car_bounds[1]):
                # 碰撞发生
                particle_manager.create_explosion(player.xcor(), player.ycor())
                # 播放碰撞音效
                try:
                    winsound.PlaySound(COLLISION_SOUND_FILE, winsound.SND_ASYNC)
                except Exception:
                    pass  # 如果音效未加载，忽略
                current_state = GameState.GAME_OVER
                break  # 跳出循环避免重复处理
        
        # 检查是否到达终点
        if current_state == GameState.PLAYING and player.ycor() > 220:
            score.new_level()
            player.reset()
            # 增加汽车速度
            for car in cars.all_cars:
                car.speed *= 1.1  # 每关增加10%速度
    
    elif current_state == GameState.PAUSED:
        # 暂停逻辑
        pass
    
    elif current_state == GameState.GAME_OVER:
        # 游戏结束逻辑
        particle_manager.update_particles()
    
    elif current_state == GameState.SHOP:
        # 商店逻辑
        pass
    
    screen.ontimer(game_loop, 16)  # 约60fps

# 点击事件处理
def handle_click(x, y):
    global current_state
    
    if current_state == GameState.MAIN_MENU:
        button_clicked = main_menu.check_click(x, y)
        if button_clicked == 0:
            # 开始游戏
            screen.clear()
            # 重新初始化游戏组件
            player.reset()
            cars.clear_cars()
            score.__init__()
            current_state = GameState.PLAYING
        elif button_clicked == 1:
            # 显示排行榜
            show_leaderboard()
        elif button_clicked == 2:
            # 打开商店
            current_state = GameState.SHOP
            shop.draw()
            screen.onclick(shop.handle_click)
        elif button_clicked == 3:
            # 退出游戏
            screen.bye()

# 显示排行榜
def show_leaderboard():
    screen.clear()
    
    title = turtle.Turtle()
    title.color("#FF6600")
    title.penup()
    title.hideturtle()
    title.goto(0, 200)
    title.write("排行榜", align="center", font=("Arial", 24, "bold"))
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT player_name, level, score, date FROM leaderboard ORDER BY level DESC, score DESC LIMIT 10")
    results = cursor.fetchall()
    conn.close()
    
    y_pos = 150
    for i, (name, level, score, date) in enumerate(results, 1):
        text = turtle.Turtle()
        text.color("white")
        text.penup()
        text.hideturtle()
        text.goto(0, y_pos)
        text.write(f"{i}. {name} - Level: {level} - Score: {score} - {date}", align="center", font=("Arial", 12, "normal"))
        y_pos -= 30
    
    # 返回主菜单按钮
    back_button = turtle.Turtle()
    back_button.shape("square")
    back_button.color("#00FF00", "#008000")
    back_button.shapesize(stretch_wid=1.5, stretch_len=8)
    back_button.penup()
    back_button.goto(0, -200)
    
    back_text = turtle.Turtle()
    back_text.color("white")
    back_text.penup()
    back_text.hideturtle()
    back_text.goto(0, -200)
    back_text.write("返回主菜单", align="center", font=("Arial", 14, "bold"))
    
    def back_to_menu(x, y):
        main_menu.draw()
        screen.onclick(handle_click)
    
    screen.onclick(back_to_menu)

# 键盘事件处理
def handle_key(key):
    global current_state
    
    if current_state == GameState.PLAYING:
        if key == "Up":
            player.up()
        elif key == "p" or key == "P":
            current_state = GameState.PAUSED
            show_pause_menu()
    
    elif current_state == GameState.PAUSED:
        if key == "p" or key == "P":
            current_state = GameState.PLAYING

# 显示暂停菜单
def show_pause_menu():
    pause_text = turtle.Turtle()
    pause_text.color("white")
    pause_text.penup()
    pause_text.hideturtle()
    pause_text.goto(0, 100)
    pause_text.write("已暂停", align="center", font=("Arial", 24, "bold"))
    
    # 继续按钮
    resume_button = turtle.Turtle()
    resume_button.shape("square")
    resume_button.color("#00FF00", "#008000")
    resume_button.shapesize(stretch_wid=2, stretch_len=10)
    resume_button.penup()
    resume_button.goto(0, 0)
    
    resume_text = turtle.Turtle()
    resume_text.color("white")
    resume_text.penup()
    resume_text.hideturtle()
    resume_text.goto(0, 0)
    resume_text.write("继续游戏", align="center", font=("Arial", 16, "bold"))
    
    # 返回主菜单按钮
    main_menu_button = turtle.Turtle()
    main_menu_button.shape("square")
    main_menu_button.color("#00FFFF", "#0080FF")
    main_menu_button.shapesize(stretch_wid=2, stretch_len=10)
    main_menu_button.penup()
    main_menu_button.goto(0, -60)
    
    main_menu_text = turtle.Turtle()
    main_menu_text.color("white")
    main_menu_text.penup()
    main_menu_text.hideturtle()
    main_menu_text.goto(0, -60)
    main_menu_text.write("返回主菜单", align="center", font=("Arial", 16, "bold"))
    
    def handle_pause_click(x, y):
        global current_state
        
        # 检查继续按钮
        resume_x, resume_y = resume_button.position()
        if abs(x - resume_x) < 100 and abs(y - resume_y) < 20:
            current_state = GameState.PLAYING
            # 清除暂停菜单
            for turtle_obj in screen.turtles():
                if turtle_obj != player and turtle_obj not in cars.all_cars and turtle_obj != score:
                    turtle_obj.hideturtle()
            screen.onclick(None)  # 移除暂停菜单的点击事件
        
        # 检查返回主菜单按钮
        main_menu_x, main_menu_y = main_menu_button.position()
        if abs(x - main_menu_x) < 100 and abs(y - main_menu_y) < 20:
            current_state = GameState.MAIN_MENU
            screen.clear()
            main_menu.draw()
            screen.onclick(handle_click)
    
    screen.onclick(handle_pause_click)

# 设置事件监听
screen.onclick(handle_click)
screen.onkey(lambda: handle_key("Up"), "Up")
screen.onkey(lambda: handle_key("P"), "p")
screen.onkey(lambda: handle_key("P"), "P")
screen.listen()

# 启动游戏循环
game_loop()

# 保持窗口打开
screen.mainloop()
