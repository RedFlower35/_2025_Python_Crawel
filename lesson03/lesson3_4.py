# 猜數字遊戲
import random

def play_game():
    min = 1
    max = 100
    count = 0
    target = random.randint(min,max)
    print('target: ',target)
    print('== 猜數字遊戲 ============')
    while(True):
        count+=1
        key = int(input('猜數字:'))
        if (key == target):
            print(f'賓果,你猜了{count}次')
            break
        elif (key >target):
            max = key -1
        else:
            min = key +1
        
        print(f'請輸入{min}~{max}之間的數')

def main():
    while True:
        play_game()    
        isPlayAgain = input('請問是否繼續? y/n ')
        if (isPlayAgain == 'n' or isPlayAgain == 'N'):
            print('謝謝你來猜數字，再見了 !!')
            break

    print('遊戲結束 !!')

if __name__ == '__main__':
    main()

