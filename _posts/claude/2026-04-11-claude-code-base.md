---
title: Claude Code 基础知识
date: 2026-04-11 23:03:00 +0800
categories: [Claude Code]
tags: [claude, ai]
---

Claude Code 是一个 AI 辅助编程工具，支持终端、IDE(VSCode, JetBrains)、桌面应用、浏览器等方式运行。

> 文中出现 `claude --resume` 这样的格式表示 Shell 中执行 claude 命令，出现 `/resume` 这样的格式表示启动 claude 后执行的内置命令（Built-in commands）。 
{: .prompt-tip }

## 1 工作流程

Claude Code 工作的基本流程是一个循环（Agentic loop），每一次循环根据任务类型最多包括三个阶段：收集上下文（Gather context）、采取行动（Take action）、验证结果（Verify results）。代码调查任务可能只需要第一个阶段，而 bug 修复可能需要三个阶段。在这过程中用户可以随时打断它并给出新的指示。

![agent_loop](/assets/img/claude/agentic-loop.svg)

参与工作流的主要是两部分：模型（Models）负责推理（Reason），工具（Tools）负责行动（Act）。

### 1.1 模型（Models）

目前根据能力主要分为以下几个模型：

- **Sonnet**: 默认模型，能力适中，响应速度适中，大多数任务都可以使用该模型。
- **Opus**: 有更强的推理能力，但是需要更长的响应时间，如果有较复杂的任务可以选择该模型。
- **Hiku**: 能力一般，但响应速度很快，简单任务可以选择该模型。

可使用 `/model` 切换模型，或者启动时 `claude --model <name>` 指定模型。

### 1.2 工具（Tools）

工具为 Claude 提供感知环境的能力，主要分为以下几类：

- **文件操作（File Operations）**: 文件读写。
- **搜索（Search）**: 搜索文件及文件内容。
- **执行（Execution）**: 执行 Shell 命令。
- **网络（Web）**: 网上搜索和拉取资源。
- **代码智能（Code Intelligence）**: 静态检查、定义跳转、引用查找等（需要[代码智能插件](https://code.claude.com/docs/en/discover-plugins#code-intelligence)）。

完整的工具列表请查看[官方文档](https://code.claude.com/docs/en/tools-reference)。

## 2 执行环境与访问接口

Claude Code 可以在以下 2 种环境中执行：

- **本地（Local）**: 即你自己的电脑本机上运行。
- **云上（Cloud）**: 在 Anthropic 提供的云虚拟机中运行。

然后可以通过以下几种接口来进行访问：

- 终端（Terminal）
- 桌面 APP
- IDE 扩展（VSCode/JetBrains）
- Web（https://claude.ai/code）
- 移动端（iOS/Android）
- Slack
- CICD (Github Actions/GitLab CICD)

## 3 会话（Session）

终端中每一次启动 claude 都会开启一个新的会话（Session），每次会话都是与当前目录绑定的，即把当前目录当作一个 `项目（Project）`，每次会话的消息记录都会以 `JSONL` 格式保存到 `~/.claude/projects/<projectname>` 目录下，文件名为 `<sessionid>.jsonl`，每次会话都会开始一个新的上下文窗口（Context window）。

### 3.1 会话恢复（Resume）

可以用以下几种方式恢复会话：

- `claude --continue`: 恢复当前工作目录的最近一次会话。
- `claude --resume [sessionid]`: 恢复指定会话或者交互式选择要恢复的会话（不指定 sessionid 时）。
- `/resume`: 交互式的方式选择要恢复的会话。

恢复后的会话可以看到之前的对话历史（Conversion history），但是之前批准的权限（Session-scoped permissions）不会恢复。

### 3.2 会话分叉（Fork）

可以用以下几种方式分叉会话：

- `claude --continue --fork-session`: 从当前工作目录的最近一次会话分叉出一个新会话。
- `/branch` 或 `/fork`: 从当前会话分叉处一个新会话。

分叉出的会话会保留原会话的对话历史（Conversion history），原会话不受影响，但是分叉出的会话不会保留原会话批准的权限（Session-scoped permissions）。

## 4 上下文（Context）

上下文窗口（Context window）是 Claude 用来在当前会话保存关于当前项目的记忆的，保存着对话历史（Conversion history）、已读取文件内容、命令输出、`CLAUDE.md`、`Auto memory`、系统指令（System instructions）等内容。

当上下文窗口满了之后，Claude Code 会进行压缩（Compact）：首先会清理早期的命令输出，然后把对话（Conversion）进行总结（Summarize）。如果某些已读取文件内容过大导致压缩后仍然占满了上下文窗口，Claude Code 会报错。压缩后可能会丢失早期的指令（Instructions），所以如果是固定指令的话建议写入到 `CLAUDE.md` 文件中进行保存。

可以通过 `/compact focus ...` 命令来指示 Claude Code 需要优先保存的内容，比如：`/compact focus on the API changes`。

可以通过 `/context` 命令查看当前上下文窗口里有哪些内容。

## 5 检查点（Checkpoint）

Claude Code 在每次编辑文件之前会对文件创建一个快照（即检查点），如果编辑后想要回退，可以连按两次 `Esc` 进行回退，也可以让 Claude Code 自己回退。

## 6 权限模式（Permission modes）

Claude Code 有以下几种权限模式：

- **Default**: 每次文件编辑和命令执行前都会请求用户的批准。
- **Auto-accept edits**: 文件编辑和 `mkdir`, `mv` 这样的命令不请求用户的批准，其他命令仍然会请求用户的批准。
- **Plan mode**: 使用只读（read-only）工具创建一个计划给用户，用户批准后才会执行。
- **Auto mode**: Claude Code 自己评估哪些动作需要请求批准。

## 7 参考资料

- [How Claude Code works] : https://code.claude.com/docs/en/how-claude-code-works
