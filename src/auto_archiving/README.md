# ci-test2
- 这是 github action 测试仓库

## 权限
- Github Fine-grained Tokens
    - Github Token 可以设置永不过期
    - 触发目标仓库的workflow_dispatch需要对应仓库的“Contents”写权限，
    - 操作目标仓库issue内容及其评论需要对应仓库的“Issues”的读写权限
- Gitlab Tokens
    - Gitlab Token 不可以设置永不过期，需要定期轮换token
    - 定期轮换token需要“xxx”权限
    - 操作目标仓库issue内容及其评论需要对应仓库的“xxx”的读写权限