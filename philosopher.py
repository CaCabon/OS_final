import pygame
import sys
import math
import random
import socket
import threading
import time

# 初始化 Pygame
pygame.init()

# 設定遊戲視窗大小
width, height = 1710, 960
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("哲學家的晚餐")
# 在檔案開頭新增全域變數
my_score = 0
opponent_score = 0
is_multiplayer = False
# 載入背景圖片並調整大小
background_image = pygame.image.load("images/background.jpg")
background_image = pygame.transform.scale(background_image, (width, height))
story_image = pygame.image.load("images/story.png")
story_image = pygame.transform.scale(story_image, (200, 200))
storybg_image = pygame.image.load("images/storybg.png")
storybg_image = pygame.transform.scale(storybg_image, (width, height))

# 定義遊戲中使用的顏色
table_Color = (139, 69, 19)        # 桌子的顏色（深褐色）
text_Color = (30, 30, 30)      # 盤子的顏色（淺灰色）
background_Color = (255, 248, 220)  # 背景顏色（米色）
title_Color = (200, 200, 200)      # 標題顏色（灰色）
button_Color = (255, 120, 0)       # 按鈕顏色（橙色）
button_Hover_Color = (200, 100, 50)  # 按鈕懸停顏色（紅褐色）
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# 設定遊戲時鐘和FPS
clock = pygame.time.Clock()
FPS = 60

class GameState:
    def __init__(self):
        self.my_score = 0
        self.opponent_score = 0
        self.connection = None

    def update_score(self):
        if self.connection:
            try:
                message = f"SCORE:{self.my_score}"
                print(f"發送分數: {message}")
                self.connection.send(message.encode())
            except Exception as e:
                print(f"發送分數錯誤: {e}")


# 載入並設定字體
title_font = pygame.font.Font("fonts/NotoSerifCJKtc-Black.otf", 120)
button_font = pygame.font.Font("fonts/NotoSerifCJKtc-Black.otf", 50)
description_font = pygame.font.Font("fonts/NotoSerifCJKtc-Black.otf", 40)

# 設定遊戲標題文字
title_text = "老師們的晚餐"
title_surface = title_font.render(title_text, True, title_Color)
title_rect = title_surface.get_rect(center=(width // 2, height // 4))

# 設定圓桌和哲學家的基本參數
table_Radius = 250                # 圓桌半徑
table_Center = (width // 2, height // 2)  # 圓桌中心位置
philosopher_Radius = 40           # 哲學家圖示半徑
plate_Radius = 65                # 盤子半徑
num_philosophers = 5              # 哲學家數量

# 創建按鈕的函數
def create_button(text, center):
    """
    創建一個帶有文字的按鈕
    text: 按鈕上的文字
    center: 按鈕的中心位置
    """
    button_surface = button_font.render(text, True, BLACK)
    button_width, button_height = 300, 100  
    button_rect = pygame.Rect(0, 0, button_width, button_height)
    button_rect.center = center
    pygame.draw.rect(screen, button_Color, button_rect, border_radius=20)
    text_rect = button_surface.get_rect(center=button_rect.center)
    return button_surface, text_rect

# 創建開始和確認按鈕
start_button_surface, start_button_rect = create_button("開始遊戲", (width // 2 - 100, height // 2 + 290))
exit_button_surface, exit_button_rect = create_button("離開", (width // 2 + 200, height // 2 + 290))
confirm_button_surface, confirm_button_rect = create_button("確定", (width // 2, height // 1.5 + 220))
# 新增模式選擇按鈕
single_button_surface, single_button_rect = create_button("單人模式", (width // 2, height // 2))
multi_button_surface, multi_button_rect = create_button("多人模式", (width // 2, height // 2 + 150))

# IP輸入框的字體
input_font = pygame.font.Font("fonts/NotoSerifCJKtc-Regular.otf", 36)
# 繪製遊戲說明的函數

def receive_data(connection, game_state):
    while True:
        try:
            data = connection.recv(1024).decode()
            print(f"收到資料: {data}")
            if data.startswith("SCORE:"):
                game_state.opponent_score = int(data.split(":")[1])
                print(f"更新對手分數: {game_state.opponent_score}")
        except Exception as e:
            print(f"接收資料錯誤: {e}")
            break

def draw_game_instructions():
    """繪製遊戲說明畫面，包含標題和遊戲規則"""
    # 繪製標題
    title_font = pygame.font.Font("fonts/NotoSerifCJKtc-Black.otf", 80)
    title_text = title_font.render("遊戲說明", True, BLACK)
    title_rect = title_text.get_rect(center=(width // 2, height // 7))
    screen.blit(title_text, title_rect)

    # 繪製說明文字
    instruction_font = pygame.font.Font("fonts/NotoSerifCJKtc-Black.otf", 40)
    instructions = [
                "                        1. 老師有3種狀態: 思考、飢餓、用餐。(例外: 憤怒)",
                "                        2. 每位老師左右手各有一支筷子，共5支。",
                "                        3. 當哲學家 '飢餓' 時，可以點選「EAT」按鈕。",
                "                        4. 哲學家只有在拿到左右兩根筷子後才能開始「用餐」，若左右",
                "                             筷子有其他人正在使用，則可能造成 Deadlock，請注意。",
                "                        5. 用餐後，哲學家會繼續思考，直到他們又餓了。",
                "                        6. 不能讓哲學家餓太久，否則遊戲結束。",
                "                        7. 遊戲難度會隨時間越來越高。",
                # "",
                "                                                        挑戰更高分吧 !!"
    ]
    
    y_offset = height // 4
    for instruction in instructions:
        instruction_text = instruction_font.render(instruction, True, BLACK)
        screen.blit(instruction_text, (width // 10, y_offset))
        y_offset += 60

# 載入遊戲中使用的圖片
eat_button_image = pygame.image.load("images/eat_button.png")
eat_button_image = pygame.transform.scale(eat_button_image, (110, 100))
hungry_image = pygame.image.load("images/hungry.png")
hungry_image = pygame.transform.scale(hungry_image, (95, 95))
eat_image = pygame.image.load("images/eat.png")
eat_image = pygame.transform.scale(eat_image, (95, 95))
ready_eat_image = pygame.image.load("images/ready_eat.png")
ready_eat_image = pygame.transform.scale(ready_eat_image, (95, 95))
think_image = pygame.image.load("images/think.png")
think_image = pygame.transform.scale(think_image, (95, 95))
think_rect = think_image.get_rect()

def typewriter_effect(lines, font, color, start_pos, speed=100):
    # """逐字顯示文字"""

    current_time = pygame.time.get_ticks()
    total_characters = 0
    y_offset = start_pos[1]

    for line in lines:
        # total_characters += len(line)
        visible_chars = (current_time - total_characters * speed) // speed 
        
        if visible_chars > len(line): 
            visible_chars = len(line)  

        partial_line = line[:visible_chars]
        text_surface = font.render(partial_line, True, color)
        text_rect = text_surface.get_rect(midtop=(start_pos[0] + 300, y_offset))
        screen.blit(text_surface, text_rect)
        y_offset += 60

        total_characters += visible_chars
        if visible_chars == len(line):
            continue


def mode_selection():
    """顯示模式選擇畫面"""
    running = True
    while running:
        screen.fill(background_Color)
        screen.blit(storybg_image, (0, 0))
        
        # 繪製標題
        mode_title = title_font.render("選擇遊戲模式", True, BLACK)
        mode_title_rect = mode_title.get_rect(center=(width // 2, height // 4))
        screen.blit(mode_title, mode_title_rect)
        
        # 處理滑鼠懸停效果
        mouse_pos = pygame.mouse.get_pos()
        single_hovered = single_button_rect.collidepoint(mouse_pos)
        multi_hovered = multi_button_rect.collidepoint(mouse_pos)
        
        # 繪製按鈕
        pygame.draw.rect(screen, 
            button_Hover_Color if single_hovered else button_Color,
            single_button_rect, border_radius=10)
        pygame.draw.rect(screen,
            button_Hover_Color if multi_hovered else button_Color,
            multi_button_rect, border_radius=10)
            
        screen.blit(single_button_surface, single_button_rect)
        screen.blit(multi_button_surface, multi_button_rect)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if single_button_rect.collidepoint(mouse_pos):
                    return "single"
                elif multi_button_rect.collidepoint(mouse_pos):
                    return "multi"
                    
        pygame.display.flip()
        

def network_setup():
    """顯示網路設定畫面，提供改進的使用者介面和視覺效果"""
    
    # 初始化變數
    ip_text = ""
    port_text = ""
    input_active = "ip"  # 當前活動的輸入框
    
    # 設定輸入框的尺寸和位置
    input_width = 400
    input_height = 50
    padding = 20  # 輸入框內部padding
    
    # 創建輸入框
    ip_rect = pygame.Rect(width//2 - input_width//2, height//2 - 80, input_width, input_height)
    port_rect = pygame.Rect(width//2 - input_width//2, height//2 + 20, input_width, input_height)
    
    # 設定顏色
    input_bg_color = (250, 250, 250)  # 輸入框背景色
    input_active_color = (230, 240, 255)  # 活動輸入框背景色
    input_border_color = (200, 200, 200)  # 輸入框邊框顏色
    input_active_border_color = (100, 150, 255)  # 活動輸入框邊框顏色
    
    # 創建陰影效果
    shadow_surface = pygame.Surface((input_width + 4, input_height + 4), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, (0, 0, 0, 50), shadow_surface.get_rect(), border_radius=10)
    
    # 設定字體
    title_font = pygame.font.Font("fonts/NotoSerifCJKtc-Black.otf", 60)
    input_font = pygame.font.Font("fonts/NotoSerifCJKtc-Black.otf", 30)
    label_font = pygame.font.Font("fonts/NotoSerifCJKtc-Black.otf", 25)
    
    # 創建漸變背景色
    def create_gradient_background():
        background = pygame.Surface((width, height))
        color1 = (240, 244, 248)
        color2 = (220, 230, 240)
        for y in range(height):
            factor = y / height
            color = tuple(c1 * (1 - factor) + c2 * factor for c1, c2 in zip(color1, color2))
            pygame.draw.line(background, color, (0, y), (width, y))
        return background
    
    gradient_bg = create_gradient_background()
    
    while True:
        # 繪製背景
        screen.blit(gradient_bg, (0, 0))
        screen.blit(storybg_image, (0, 0))
        
        # 繪製標題
        title_shadow = title_font.render("網路設定", True, (0, 0, 0, 128))
        title_text = title_font.render("網路設定", True, (50, 50, 50))
        title_rect = title_text.get_rect(center=(width//2, height//4))
        screen.blit(title_shadow, (title_rect.x + 2, title_rect.y + 2))
        screen.blit(title_text, title_rect)
        
        # 繪製輸入框標籤
        for label_text, rect, is_active in [("IP 位址", ip_rect, input_active == "ip"),
                                          ("連接埠", port_rect, input_active == "port")]:
            label = label_font.render(label_text, True, (80, 80, 80))
            label_rect = label.get_rect(bottomleft=(rect.left, rect.top - 5))
            screen.blit(label, label_rect)
        
        # 繪製輸入框
        for rect, active, text in [(ip_rect, input_active == "ip", ip_text),
                                 (port_rect, input_active == "port", port_text)]:
            # 繪製陰影
            screen.blit(shadow_surface, (rect.x + 2, rect.y + 2))
            
            # 繪製輸入框背景
            pygame.draw.rect(screen, 
                           input_active_color if active else input_bg_color,
                           rect,
                           border_radius=8)
            
            # 繪製邊框
            pygame.draw.rect(screen,
                           input_active_border_color if active else input_border_color,
                           rect,
                           2,
                           border_radius=8)
            
            # 繪製文字
            text_surface = input_font.render(text, True, (60, 60, 60))
            text_rect = text_surface.get_rect(midleft=(rect.left + padding, rect.centery))
            screen.blit(text_surface, text_rect)
            
            # 如果是活動輸入框，繪製閃爍的游標
            #  if active and time.time() % 1 > 0.5:
            # cursor_x = text_rect.right + 2
            # pygame.draw.line(screen, (60, 60, 60),
                        #  (cursor_x, rect.centery - 15),
                        #     (cursor_x, rect.centery + 15),
                        #    2)
        
        # 繪製確認按鈕
        mouse_pos = pygame.mouse.get_pos()
        button_hovered = confirm_button_rect.collidepoint(mouse_pos)
        
        # 按鈕陰影效果
        pygame.draw.rect(screen, (0, 0, 0, 50),
                        confirm_button_rect.inflate(4, 4),
                        border_radius=10)
        
        # 按鈕本體
        pygame.draw.rect(screen,
                        button_Hover_Color if button_hovered else button_Color,
                        confirm_button_rect,
                        border_radius=10)
        
        # 按鈕文字
        button_text = pygame.font.Font("fonts/NotoSerifCJKtc-Black.otf", 40).render(
            "確認", True, (255, 255, 255))
        button_text_rect = button_text.get_rect(center=confirm_button_rect.center)
        screen.blit(button_text, button_text_rect)
        
        # 事件處理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # 檢查點擊位置
                if ip_rect.collidepoint(event.pos):
                    input_active = "ip"
                elif port_rect.collidepoint(event.pos):
                    input_active = "port"
                elif confirm_button_rect.collidepoint(event.pos):
                    if validate_input(ip_text, port_text):  # 添加輸入驗證
                        return ip_text, port_text
                    else:
                        # 顯示錯誤提示
                        show_error_message()
                        
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    # 使用 Tab 鍵切換輸入框
                    input_active = "port" if input_active == "ip" else "ip"
                elif event.key == pygame.K_RETURN:
                    if validate_input(ip_text, port_text):
                        return ip_text, port_text
                    else:
                        show_error_message()
                elif input_active == "ip":
                    if event.key == pygame.K_BACKSPACE:
                        ip_text = ip_text[:-1]
                    elif len(ip_text) < 15:  # 限制IP長度
                        if event.unicode in '0123456789.':  # 只允許數字和點
                            ip_text += event.unicode
                elif input_active == "port":
                    if event.key == pygame.K_BACKSPACE:
                        port_text = port_text[:-1]
                    elif len(port_text) < 5:  # 限制埠號長度
                        if event.unicode.isnumeric():
                            port_text += event.unicode
        
        pygame.display.flip()
        clock.tick(60)

def validate_input(ip, port):
    """驗證IP和埠號的輸入"""
    # 驗證IP格式
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        for part in parts:
            if not 0 <= int(part) <= 255:
                return False
    except:
        return False
    
    # 驗證埠號
    try:
        port_num = int(port)
        if not 0 <= port_num <= 65535:
            return False
    except:
        return False
    
    return True

def show_error_message():
    """顯示錯誤訊息"""
    error_surface = pygame.Surface((400, 100))
    error_surface.fill((255, 200, 200))
    error_text = input_font.render("輸入格式錯誤", True, (200, 0, 0))
    error_rect = error_text.get_rect(center=(error_surface.get_width()//2,
                                           error_surface.get_height()//2))
    error_surface.blit(error_text, error_rect)
    
    error_rect = error_surface.get_rect(center=(width//2, height - 100))
    screen.blit(error_surface, error_rect)
    pygame.display.flip()
    pygame.time.delay(1000)  # 顯示1秒
 
def create_server(port):
    """建立 TCP 伺服器"""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', int(port)))
    server.listen(1)
    return server

def show_server_info():
    """顯示伺服器資訊畫面"""
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    server_port = 12345
    
    running = True
    while running:
        screen.fill(background_Color)
        
        # 顯示標題
        info_title = title_font.render("伺服器資訊", True, BLACK)
        title_rect = info_title.get_rect(center=(width//2, height//4))
        screen.blit(storybg_image, (0, 0))
        screen.blit(info_title, title_rect)

        
        # 顯示 IP 和 Port
        ip_text = input_font.render(f"IP: {ip}", True, BLACK)
        port_text = input_font.render(f"Port: {server_port}", True, BLACK)
        
        screen.blit(ip_text, (width//2 - 150, height//2 - 50))
        screen.blit(port_text, (width//2 - 150, height//2 + 50))
        
        # 顯示確認按鈕
        mouse_pos = pygame.mouse.get_pos()
        button_hovered = confirm_button_rect.collidepoint(mouse_pos)
        pygame.draw.rect(screen,
            button_Hover_Color if button_hovered else button_Color,
            confirm_button_rect, border_radius=10)
        screen.blit(confirm_button_surface, confirm_button_rect)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if confirm_button_rect.collidepoint(mouse_pos):
                    return
                    
        pygame.display.flip()

# 新增分數同步相關函數
def send_score(connection, score):
    """傳送分數更新"""
    try:
        message = f"SCORE:{score}"
        connection.send(message.encode())
    except:
        pass

def handle_received_data(connection):
    """處理接收到的資料"""
    global opponent_score
    while True:
        try:
            data = connection.recv(1024).decode()
            if data.startswith("SCORE:"):
                opponent_score = int(data.split(":")[1])
        except:
            break

# 修改顯示分數函數
def draw_scores():
    """繪製分數"""
    if not is_multiplayer:
        return
        
    score_font = pygame.font.Font("fonts/NotoSerifCJKtc-Regular.otf", 36)
    
    # 繪製自己的分數（左上角）
    my_score_text = score_font.render(f"我的分數: {my_score}", True, BLACK)
    screen.blit(my_score_text, (50, 30))
    
    # 繪製對手的分數（右上角）
    opp_score_text = score_font.render(f"對手分數: {opponent_score}", True, BLACK)
    opp_score_rect = opp_score_text.get_rect()
    opp_score_rect.topright = (width - 50, 30)
    screen.blit(opp_score_text, opp_score_rect)
       
# 主選單函數

def main_menu():
    """處理遊戲主選單的邏輯和顯示"""
    running = True
    while running:
        screen.fill((255, 255, 255))
        screen.blit(background_image, (0, 0))
        screen.blit(title_surface, title_rect)

        # 處理滑鼠懸停效果
        mouse_pos = pygame.mouse.get_pos()
        button_hovered = start_button_rect.collidepoint(mouse_pos)

        # 繪製按鈕
        pygame.draw.rect(
            screen, 
            button_Hover_Color if button_hovered else button_Color, 
            start_button_rect, 
            border_radius=10
        )
        screen.blit(start_button_surface, start_button_rect.topleft)
        pygame.draw.rect(
            screen,
            button_Hover_Color if exit_button_rect.collidepoint(mouse_pos) else button_Color,
            exit_button_rect,
            border_radius=10
        )
        screen.blit(exit_button_surface, exit_button_rect.topleft)

        # 事件處理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()
                elif button_hovered:
                    return  # Transition to the description panel

        pygame.display.flip()

# 遊戲說明面板函數
def description_panel():
    """顯示遊戲說明面板"""
    running = True
    image_rect = pygame.Rect(width // 2 - 750, height // 2 - 400, story_image.get_width(), story_image.get_height())
    enlarged_image_scale = 1.2  # 放大比例
    original_image = story_image  # 保留原始圖片
    enlarged_image = pygame.transform.scale(story_image, (int(story_image.get_width() * enlarged_image_scale), int(story_image.get_height() * enlarged_image_scale)))

    in_background_story = False
    back_button_surface, back_button_rect = create_button("返回", (width // 2, height // 1.5 + 200))

    while running:
        screen.fill(background_Color)
        screen.blit(storybg_image, (0, 0))


        # 滑鼠懸停效果
        mouse_pos = pygame.mouse.get_pos()
        button_hovered = confirm_button_rect.collidepoint(mouse_pos)

        # 繪製確認按鈕
        if not in_background_story:
            if image_rect.collidepoint(mouse_pos):
                current_image = enlarged_image
                current_image_rect = current_image.get_rect(center=image_rect.center)
            else:
                current_image = original_image
                current_image_rect = image_rect
            screen.blit(current_image, current_image_rect.topleft)

            font = pygame.font.Font("fonts/NotoSerifCJKtc-Black.otf", 32)
            text = font.render("故事背景", True, text_Color)
            text_rect = text.get_rect(center=(width // 9 + 10 , current_image_rect.bottom + 25))
            screen.blit(text, text_rect)

        
            pygame.draw.rect(
                screen, 
                button_Hover_Color if button_hovered else button_Color, 
                confirm_button_rect, 
                border_radius=10
            )
            screen.blit(confirm_button_surface, confirm_button_rect.topleft)
            draw_game_instructions()

        else:
            dialog_font = pygame.font.Font("fonts/NotoSerifCJKtc-Black.otf", 44)
            dialog_text = [
                "               在一個疲憊的星期五晚上，",
                "               五位老師一起去一家特別的餐廳吃晚餐，",
                "               而你剛好看到，想打聲招呼於是也走了進去。",
                "               進去發現，餐廳裡的客人都被施加了奇怪的「狀態」，",
                "               老師們也不例外。",
                "               此時，服務生來了。",
                "               「你，是他們的學生嗎?」",
                "               「我們來玩個遊戲吧!」",
                "               「他們會怎麼樣，全掌握在你手中。」",
                "",
                "               你，能成功幫助老師他們嗎...?"
            ]
            typewriter_effect(dialog_text, dialog_font, BLACK, (width // 4 + 50, height // 7 -30))

            
            pygame.draw.rect(
                screen,
                button_Hover_Color if back_button_rect.collidepoint(mouse_pos) else button_Color,
                back_button_rect,
                border_radius=10
            )
            screen.blit(back_button_surface, back_button_rect.topleft)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not in_background_story and image_rect.collidepoint(mouse_pos):
                    in_background_story = True  # 切換到背景故事畫面

                elif in_background_story and back_button_rect.collidepoint(mouse_pos):
                    in_background_story = False  # 返回遊戲說明畫面
   
                elif not in_background_story and confirm_button_rect.collidepoint(mouse_pos):
                    return  # 進入遊戲主畫面

        pygame.display.flip()

def multiplayer_selection():
    """多人模式選擇頁面"""
    host_button_surface, host_button_rect = create_button("開設伺服器", (width // 2, height // 2))
    join_button_surface, join_button_rect = create_button("加入連線", (width // 2, height // 2 + 150))
    
    running = True
    while running:
        screen.fill(background_Color)
        screen.blit(storybg_image, (0, 0))
        
        # 標題
        title = title_font.render("多人模式", True, BLACK)
        title_rect = title.get_rect(center=(width // 2, height // 4))
        screen.blit(title, title_rect)
        
        # 按鈕處理
        mouse_pos = pygame.mouse.get_pos()
        host_hovered = host_button_rect.collidepoint(mouse_pos)
        join_hovered = join_button_rect.collidepoint(mouse_pos)
        
        pygame.draw.rect(screen, 
            button_Hover_Color if host_hovered else button_Color,
            host_button_rect, border_radius=20)
        pygame.draw.rect(screen,
            button_Hover_Color if join_hovered else button_Color,
            join_button_rect, border_radius=20)
            
        screen.blit(host_button_surface, host_button_rect)
        screen.blit(join_button_surface, join_button_rect)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if host_button_rect.collidepoint(mouse_pos):
                    return "host"
                elif join_button_rect.collidepoint(mouse_pos):
                    return "join"
        
        pygame.display.flip()

def wait_for_connection(server):
    """等待連線畫面"""
    waiting_start = time.time()
    dots = 0
    while True:
        screen.fill(background_Color)
        
        # 顯示等待訊息
        waiting_text = title_font.render("等待玩家連線" + "." * dots, True, BLACK)
        waiting_rect = waiting_text.get_rect(center=(width // 2, height // 2))
        screen.blit(waiting_text, waiting_rect)
        
        # 更新動畫點點
        if time.time() - waiting_start > 0.5:
            dots = (dots + 1) % 4
            waiting_start = time.time()
            
        pygame.display.flip()
        
        # 檢查連線
        server.settimeout(0.1)
        try:
            client_socket, addr = server.accept()
            return client_socket
        except socket.timeout:
            continue
        except:
            return None

def connect_to_server(ip, port):
    """連線到伺服器"""
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(5)  # 5秒超時
        client.connect((ip, int(port)))
        return client
    except:
        return None

def show_error_message(message):
    """顯示錯誤訊息"""
    start_time = time.time()
    while time.time() - start_time < 3:  # 顯示3秒
        screen.fill(background_Color)
        error_text = title_font.render(message, True, (255, 0, 0))
        error_rect = error_text.get_rect(center=(width // 2, height // 2))
        screen.blit(error_text, error_rect)
        pygame.display.flip()

# 修改主遊戲函數
def main_game(connection=None):
    game_state = GameState()
    game_state.connection = connection
    
    # 設置連線接收執行緒
    if connection:
        receive_thread = threading.Thread(
            target=receive_data, 
            args=(connection, game_state)
        )
        receive_thread.daemon = True
        receive_thread.start()
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        # 事件處理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for philosopher in philosophers:
                    if philosopher['state'] == 'hungry':
                        if philosopher['button_rect'].collidepoint(mouse_pos):
                            if check_eat_condition(philosopher):  # 確認是否可以吃飯
                                game_state.my_score += 10
                                game_state.update_score()
                                philosopher['state'] = 'eating'
                                philosopher['image'] = eat_image
                                philosopher['last_state_change'] = current_time
        
        # 更新所有哲學家的狀態
        for philosopher in philosophers:
            update_philosopher_state(philosopher, current_time)
        
        # 繪製遊戲畫面
        screen.fill(background_Color)
        
        # 繪製圓桌
        pygame.draw.circle(screen, table_Color, table_Center, table_Radius)
        
        # 繪製盤子
        positions2 = position_plate()
        for position in positions2:
            plate_rect.center = position 
            screen.blit(plate_image, plate_rect)
        
        # 繪製筷子
        positions3 = position_chopsticks()
        for i, position in enumerate(positions3):
            angle = 81 + 108 * i 
            rotate_image = pygame.transform.rotate(chopsticks_image, angle)  
            chopsticks_rect = rotate_image.get_rect(center=position) 
            screen.blit(rotate_image, chopsticks_rect.topleft)
        
        # 繪製哲學家
        position1 = position_philosophers()
        for i, position in enumerate(position1):
            philosopher = philosophers[i]
            philosopher_rect = philosopher['image'].get_rect(center=position)
            screen.blit(philosopher['image'], philosopher_rect)
            
            if philosopher['state'] == 'hungry':         
                screen.blit(eat_button_image, philosopher['button_rect'].topleft)
        
               # 繪製畫面最後加入分數顯示
        score_font = pygame.font.Font("fonts/NotoSerifCJKtc-Black.otf", 36)
        
        # 繪製我的分數（左上角）
        my_score_text = score_font.render(f"我的分數: {game_state.my_score}", True, BLACK)
        screen.blit(my_score_text, (50, 30))
        
        # 繪製對手分數（右上角）
        if connection:  # 只在多人模式顯示對手分數
            opp_score_text = score_font.render(f"對手分數: {game_state.opponent_score}", True, BLACK)
            opp_score_rect = opp_score_text.get_rect()
            opp_score_rect.topright = (width - 50, 30)  # 設定右上角位置
            screen.blit(opp_score_text, opp_score_rect)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

def check_eat_condition(philosopher):
    """檢查哲學家是否能夠吃飯"""
    # 確認當前哲學家是否餓了
    if philosopher['state'] != 'hungry':
        return False
    
    philosopher_id = philosophers.index(philosopher)
    left_neighbor = (philosopher_id + 1) % num_philosophers
    right_neighbor = (philosopher_id + 4) % num_philosophers
    
    # 檢查左右鄰居是否在吃飯
    left_eating = philosophers[left_neighbor]['state'] == 'eating'
    right_eating = philosophers[right_neighbor]['state'] == 'eating'
    
    # 如果左右鄰居都沒在吃飯，則可以吃
    return not (left_eating or right_eating)

# 計算哲學家位置的函數
def position_philosophers():
    """計算每個哲學家在圓桌旁的位置"""
    offset = 60  # 距離圓桌的偏移距離
    position = []
    angle_step = 2 * math.pi / num_philosophers  # 每個哲學家之間的角度
    start_angle = math.pi / 2  # 起始角度
    for i in range(num_philosophers):
        angle = start_angle - i * angle_step
        x = table_Center[0] + (table_Radius + offset) * math.cos(angle)
        y = table_Center[1] + (table_Radius + offset) * math.sin(angle)
        position.append((x, y))
    return position

# 初始化哲學家
positions = position_philosophers()
philosophers = []
for i, position in enumerate(positions):
    philosopher = {
        'id': i + 1,  # 哲學家編號
        'state': 'thinking',  # 初始狀態為思考
        'image': think_image,
        'pos': position,
        'next_hungry_time': pygame.time.get_ticks() + random.randint(1000, 3000),
        'button_rect': pygame.Rect(position[0] + 30, position[1] + 50, 95, 95),
        'last_state_change': pygame.time.get_ticks(),
        'has_left_chopstick': False,
        'has_right_chopstick': False,
        'left_chopstick': i,
        'right_chopstick': (i + 1) % num_philosophers,
        'left_chopstick_rect': pygame.Rect(position[0], position[1] - 20, 70, 70),
        'right_chopstick_rect': pygame.Rect(position[0] + 70, position[1] - 20, 70, 70)
    }
    philosophers.append(philosopher)

# 載入和設定盤子圖片
plate_image = pygame.image.load("images/plate.png")
plate_image = pygame.transform.scale(plate_image, (160, 160)) 
plate_rect = plate_image.get_rect()

# 計算盤子位置的函數
def position_plate():
    """計算每個盤子在圓桌上的位置"""
    position = []
    angle_step = 2 * math.pi / num_philosophers 
    start_angle = math.pi / 2  
    for i in range(num_philosophers):
        angle = start_angle + i * angle_step
        x = table_Center[0] + (table_Radius -90) * math.cos(angle)
        y = table_Center[1] + (table_Radius -90) * math.sin(angle)
        position.append((x, y))
    return position

# 載入和設定筷子圖片
chopsticks_image = pygame.image.load("images/chopsticks.png")
chopsticks_image = pygame.transform.scale(chopsticks_image, (80, 80))
chopsticks_rect = chopsticks_image.get_rect()

# 計算筷子位置的函數
def position_chopsticks():
    """計算每雙筷子在圓桌上的位置"""
    position = []
    angle_step = 2 * math.pi / num_philosophers  # 計算每雙筷子之間的角度
    start_angle = 54 * math.pi / 180  # 設定起始角度為54度（轉換為弧度）
    for i in range(num_philosophers):
        # 計算每雙筷子的位置
        angle = start_angle + i * angle_step
        x = table_Center[0] + (table_Radius -75) * math.cos(angle)
        y = table_Center[1] + (table_Radius -75) * math.sin(angle)
        position.append((x, y))
    return position

# 初始化筷子狀態（None表示沒有人使用）
chopsticks_status = [None] * num_philosophers

# 更新哲學家狀態的函數
def update_philosopher_state(philosopher, current_time):
    """
    更新哲學家的狀態（思考、飢餓、用餐）
    philosopher: 要更新的哲學家對象
    current_time: 當前時間
    """
    # 檢查是否到達下一次飢餓時間
    if current_time >= philosopher['next_hungry_time']:
        if philosopher['state'] == 'thinking':
            # 從思考狀態變為飢餓狀態
            philosopher['state'] = 'hungry'
            philosopher['image'] = hungry_image 
            # 設定下一次飢餓時間（5-30秒後）
            philosopher['next_hungry_time'] = current_time + random.randint(3000, 7000)

            # 根據哲學家的編號調整用餐按鈕的位置
            if philosopher['id'] == 1:  # 1號哲學家 - 右邊下面
                philosopher['button_rect'].topleft = (philosopher['pos'][0] + 55, philosopher['pos'][1])
            elif philosopher['id'] == 2:  # 2號哲學家
                philosopher['button_rect'].topleft = (philosopher['pos'][0] - 52, philosopher['pos'][1] + 60)
            elif philosopher['id'] == 3:  # 3號哲學家
                philosopher['button_rect'].topleft = (philosopher['pos'][0] + 47, philosopher['pos'][1] + 20)
            elif philosopher['id'] == 4:  # 4號哲學家
                philosopher['button_rect'].topleft = (philosopher['pos'][0] - 147, philosopher['pos'][1] + 20)
            elif philosopher['id'] == 5:  # 5號哲學家 - 左邊下面
                philosopher['button_rect'].topleft = (philosopher['pos'][0] - 52, philosopher['pos'][1] + 57)
            else:  # 預設位置
                philosopher['button_rect'].topleft = (philosopher['pos'][0] - 100, philosopher['pos'][1] + 50)

    # 處理用餐狀態
    if philosopher['state'] == 'eating':
        # 用餐持續5秒
        if current_time - philosopher['last_state_change'] >= 5000:
            # 用餐結束，回到思考狀態
            philosopher['state'] = 'thinking'
            philosopher['image'] = think_image
            # 設定下一次飢餓時間
            philosopher['next_hungry_time'] = current_time + random.randint(5000, 30000)
            philosopher['last_state_change'] = current_time

# 遊戲主要流程
def main():
    main_menu()
    description_panel()
    mode = mode_selection()
    
    if mode == "single":
        main_game()
    elif mode == "multi":
        multi_mode = multiplayer_selection()
        
        if multi_mode == "host":
            server = create_server(12345)  # 使用預設port
            show_server_info()
            client_socket = wait_for_connection(server)
            if client_socket:
                main_game()
            else:
                show_error_message("連線失敗")
                main()
        
        elif multi_mode == "join":
            ip, port = network_setup()
            client_socket = connect_to_server(ip, port)
            if client_socket:
                main_game()
            else:
                show_error_message("無法連線到伺服器")
                main()

if __name__ == "__main__":
    main()