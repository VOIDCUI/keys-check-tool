# API Key 批量检测工具

批量检测 OpenAI 兼容 API 的 Key 是否可用，支持多线程并发检测。

## 功能特性

- ✅ 批量检测 API Keys 有效性
- ✅ 多线程并发检测，速度快
- ✅ 支持 .env 配置文件和命令行参数
- ✅ 支持自定义 Base URL 和模型
- ✅ 默认读取 `keys.txt`，无需每次指定文件
- ✅ 找到有效 Key 后可选择是否继续检测
- ✅ Key 脱敏显示，保护隐私
- ✅ 自动保存有效的 Keys 到文件
- ✅ 实时进度条显示检测进度

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API 信息

复制示例配置文件并编辑:

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 API 配置:

```env
BASE_URL=https://api.openai.com/v1
MODEL=gpt-3.5-turbo
```

### 3. 准备 Keys 文件

创建 `keys.txt` 文件，每行一个 API Key:

```
sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
sk-yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
```

### 4. 运行检测

最简单的方式（使用默认的 `keys.txt` 文件）:

```bash
python key_checker.py
```

或指定其他文件:

```bash
python key_checker.py -f my_keys.txt
```

## 使用方法

### 配置优先级

程序按以下优先级读取配置:

1. `.env` 文件中的配置（优先级最高）
2. 命令行参数
3. 默认值

### 基本用法

使用 `.env` 配置 + 默认 `keys.txt` 文件（推荐）:

```bash
python key_checker.py
```

指定其他 Keys 文件:

```bash
python key_checker.py -f my_keys.txt
```

使用命令行参数覆盖配置:

```bash
python key_checker.py -u https://api.openai.com/v1 -m gpt-3.5-turbo
```

### 完整参数说明

```bash
python key_checker.py \
  -f keys.txt \                          # Keys 文件路径（可选，默认 keys.txt）
  -u https://api.openai.com/v1 \         # API Base URL（可选，优先使用 .env）
  -m gpt-3.5-turbo \                     # 模型名称（可选，优先使用 .env）
  -w 10 \                                # 并发线程数（可选，默认 10）
  -o valid_keys/my_keys.txt \            # 输出文件（可选，默认 valid_keys/valid_keys_YYYYMMDD_HHMMSS.txt）
  -t 10                                  # 超时时间/秒（可选，默认 10）
```

### 使用示例

检测 OpenAI Keys:
```bash
# 在 .env 中配置
BASE_URL=https://api.openai.com/v1
MODEL=gpt-4

# 运行（自动读取 keys.txt）
python key_checker.py
```

检测 Claude Keys:
```bash
# 在 .env 中配置
BASE_URL=https://api.anthropic.com/v1
MODEL=claude-opus-4-6

# 运行
python key_checker.py
```

检测自定义 API:
```bash
# 使用命令行参数覆盖 .env 配置
python key_checker.py -u https://custom-api.com/v1 -m custom-model
```

指定其他 Keys 文件:
```bash
python key_checker.py -f other_keys.txt
```

## Keys 文件格式

创建一个文本文件（如 `keys.txt`），每行一个 API Key:

```
sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
sk-yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
sk-zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
```

注意:
- 每行一个 Key
- 空行会被自动忽略
- 不要在 Key 前后添加引号或空格

## 输出示例

```
[*] 共 512 个 API Key
[*] 目标验证节点: https://api.openai.com/v1
[*] 检测模型: gpt-3.5-turbo
[*] 开始多线程并发检测...

[+] 成功! 找到有效的 API Key: sk-2L...xzE2g

是否继续检测剩余的 Keys? (y/n): n
[*] 停止检测...

============================================================
检测完成!
有效 Key 数量: 1
无效 Key 数量: 511
============================================================

[*] 有效的 Keys 已保存到: valid_keys/valid_keys_20260416_143052.txt
```

所有有效的 Keys 会自动保存到 `valid_keys/` 文件夹中，文件名包含时间戳，不会相互覆盖。

## 安全提示

⚠️ **重要**: 请勿将包含真实 API Keys 的文件提交到 Git 仓库

本项目已配置 `.gitignore` 来防止敏感文件被提交:
- `.env` - 你的 API 配置
- `keys.txt` - 待检测的 Keys
- `valid_keys/` - 所有检测结果文件夹
- `*_keys.txt` - 所有包含 keys 的文件

## 注意事项

- 请确保有足够的 API 配额，避免触发速率限制
- 建议根据 API 提供商的限制调整并发线程数（`-w` 参数）
- 检测过程会发送真实的 API 请求，可能产生少量费用
- 请妥善保管 Keys 文件和输出文件，避免泄露
- 不要将 `.env` 文件和 Keys 文件提交到版本控制系统

## License

MIT
