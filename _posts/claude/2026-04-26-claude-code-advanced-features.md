---
title: Claude Code 高级特性
date: 2026-04-26 23:38:00 +0800
categories: [Claude Code]
tags: [claude, ai, unfinished]
---

本文介绍 Claude Code 的 Claude.md、Skills、MCP、Subagents、Agent teams、Hooks、Plugins 等高级特性。

## 特性简介

- [CLAUDE.md](https://code.claude.com/docs/en/memory): 用来向 Claude Code `介绍项目`（如项目背景、架构、技术栈等）和`指定规范`（如构建测试命令、注意事项、禁止事项等）的文件。

- [Skills](https://code.claude.com/docs/en/skills): 可复用的`参考资料`（如 API 文档、代码规范等）和`工作流程`（如代码评审、bug 修复等）。

- [Subagents](https://code.claude.com/docs/en/sub-agents): 运行于当前会话中的具有独立上下文窗口的子代理，子代理运行结束后仅返回结果给主代理，使用子代理的目的是为了`避免主代理的上下文窗口被污染`或`在后台并行运行一个不影响主代理的任务`，如果只关心结果不关心过程信息的任务，比如运行一个需要大量网上搜索的调查任务、需要读取大量文件内容来进行查找信息的任务、有大量日志输出的测试任务等，就适合使用子代理。

- [Agent teams](https://code.claude.com/docs/en/agent-teams): 多个相互独立的代理所组成的团队，每个代理运行在各自的会话中，但是相互之间可以通信，它们共享一个任务列表，通常用于把一项复杂的任务拆分为多个任务后由 Agent teams 中的所有 agent 共同完成。

- [Hooks](https://code.claude.com/docs/en/hooks-guide): 在特定时机触发的动作，动作可以是`执行命令`、`发送 HTTP 请求`、`发送一个提示词`、`运行一个 Subagent`。

- [MCP](https://code.claude.com/docs/en/mcp): Claude Code 用来连接其他服务的配置信息，服务可以是`数据库`、`浏览器`、`即时通讯软件`等，只要实现了 MCP 协议的都可以。

- [Plugins](https://code.claude.com/docs/en/plugins): 打包好的 Skills、Subagents、Hooks、MCP 等，可以分发给其他人使用。

- [Marketplace](https://code.claude.com/docs/en/plugin-marketplaces): 用来分发 Plugins 的平台。


## 作用范围

- **CLAUDE.md**: 
    - **系统级**: 作用于整个系统，根据系统类型划分，存放位置如下：
        - macOS: /Library/Application Support/ClaudeCode/CLAUDE.md
        - Linux: /etc/claude-code/CLAUDE.md
        - Windows: C:\Program Files\ClaudeCode\CLAUDE.md
    - **用户级**: 作用于用户的所有项目，可存放位置如下：
        - ~/.claude/CLAUDE.md
        - ~/.claude/rules/: 细分的用户 CLAUDE.md，作用于用户可访问的所有或指定文件（通配符匹配）。
    - **项目级**: 作用于当前项目，可存放位置如下：
        - ./CLAUDE.md 或 ./.claude/CLAUDE.md: 两者效果相同，任选其一，通常前者用的多一些。
        - ./CLAUDE.local.md: 用来写个人对于当前项目的偏好的，应该加入到 .gitignore 文件中，不与项目其他成员共享。
        - ./.claude/rules: 细分的项目 CLAUDE.md，作用于当前项目下的所有或指定文件（通配符匹配）。
    - **目录级**: 作用于其所在目录，CLAUDE.md 和 CLAUDE.local.md 均可以。

- **Skills**:

- **Subagents**: 

- **Agent teams**:

- **Hooks**: 

- **MCP**:

- **Plugins**: 


## 加载时机

- **CLAUDE.md**: 
    - **系统级**: 在当前系统启动会话时即加载。
    - **用户级**: 由当前用户启动会话时即加载。
        - ~/.claude/CLAUDE.md: 由当前用户启动会话时即加载。
        - ~/.claude/rules/: 有当前用户启动的会话读取匹配的文件时才加载。
    - **项目级**: 
        - ./CLAUDE.md 或 ./.claude/CLAUDE.md: 在当前项目启动会话时即加载。
        - ./CLAUDE.local.md: 在当前项目启动会话时即加载。
        - ./.claude/rules: 当前项目的会话读取匹配的文件时才加载。
    - **目录级**:
        - 当该目录是当前项目的子目录时，则在读取该目录下的文件时才加载。
        - 当该目录是当前项目的父目录时，则在启动该项目的会话时即加载。

- **Skills**:

- **Subagents**: 

- **Agent teams**:

- **Hooks**: 

- **MCP**:

- **Plugins**: 

## 优先级

- **CLAUDE.md**: 不管在什么位置，只有符合加载时机，即会加载近上下文窗口，不存在优先级关系，当不同文件中的指令存在冲突时，Claude Code 会自行判断并选择，具体选择哪个是不确定的，所以用户应该这些不同位置的文件中尽量不要有冲突的指令，但是有一个稍有不同的是同一目录下的 CLAUDE.md 和 CLAUDE.local.md 文件，由于它们时同一时机加载，但是 CLAUDE.local.md 在后，所以它的指令相比前者有一定的优势，但也不是完全确保的规则，详情可以参考官方文档：[
How CLAUDE.md files load](https://code.claude.com/docs/en/memory#how-claude-md-files-load), [Claude isn’t following my CLAUDE.md](https://code.claude.com/docs/en/memory#claude-isn%E2%80%99t-following-my-claude-md)。

- **Skills**:

- **Subagents**: 

- **Agent teams**:

- **Hooks**: 

- **MCP**:

- **Plugins**: 

## 参考资料

- [Claude Code Docs]: https://code.claude.com/docs/en
