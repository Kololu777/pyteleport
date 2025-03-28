def add(a, b):
    return a + b

def main():
    print("足し算を行います。")
    a = int(input("一つ目の数を入力してください: "))
    b = int(input("二つ目の数を入力してください: "))
    result = add(a, b)
    print(f"結果: {result}")

if __name__ == '__main__':
    main()
