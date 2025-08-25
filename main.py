import os

from dotenv import load_dotenv
from openai import OpenAI, APIError

C = "deepseek-chat" # DeepSeek V3.1 非思考模式
R = "deepseek-reasoner" # DeepSeek V3.1 思考模式

PROMPT = "你是一个友好的人工智能助手"

def get_user_config():

    print("\n---配置开始---\n")

    model_choice = input("请选择你要使用的模型(C/R, 默认使用C): ")

    if model_choice == "R":
        model = R
    else:
        model = C

    stream_choice = input("是否启用流式输出(y/n, 默认为流式输出): ")

    stream = False if stream_choice == "n" else True

    system_choice = input("请定义模型的系统角色(按 Enter 使用默认值): ")

    if not system_choice:
        system_content = PROMPT
        print(f"\n使用默认系统角色: {system_content}")
    else:
        system_content = system_choice
        print(f"\n系统角色配置为: {system_content}")

    print("\n---配置结束---\n")

    return model, stream, system_content

def chat_loop(client, model, stream, system_content):
    messages = [{
        "role": "system",
        "content": system_content,
        }]

    print("对话即将开始，输入 .q 或按 Ctrl-C 退出")

    while True:
        try:
            user_content = input("\nuser: ")

            if user_content == ".q":
                print("\nassistant: Goodbye!")
                break

            messages.append({
                "role": "user",
                "content": user_content,
                })

            try:
                response = client.chat.completions.create(
                    model = model,
                    stream = stream,
                    messages = messages,
                )

                assistant_content = ""

                print("\nassistant: ", end="", flush=True)

                if stream:
                    for chunk in response:
                        if content := chunk.choices[0].delta.content:
                            print(content, end="", flush=True)
                            assistant_content += content
                else:
                    assistant_content =(
                        response.choices[0].message.content
                    )
                    print(assistant_content)

                print()

                if assistant_content:
                    messages.append({
                        "role": "assistant",
                        "content": assistant_content,
                        })

            except APIError as e:
                print(f"\nAPI 请求失败: {e}\n请重试")
                messages.pop()

            except Exception as e:
                print(f"\n发生未知错误: {e}")
                break

        except (KeyboardInterrupt, EOFError):
            print("\n\nassistant: Bye!")
            break

def main():
    load_dotenv()
    
    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key:
        print("错误: DEEPSEEK_API_KEY 环境变量未设置")
        print("请在项目中创建 .env 文件并设置环境变量")
        return

    try:
        client = OpenAI(
            api_key = api_key,
            base_url = "https://api.deepseek.com/v1",
        )

        model, stream, system_content =(
            get_user_config()
        )

        chat_loop(
            client,
            model,
            stream,
            system_content,
        )

    except Exception as e:
        print(f"初始化客户端或配置时出错: {e}")

if __name__ == "__main__":
    main()
