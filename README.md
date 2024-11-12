# ci_test

- 本仓库是复仇时刻issue仓库自动归档项目的一部分
- 本仓库的脚本负责处理Issue关闭事件，并将格式化且处理好的Issue内容以json格式发送指另一个归档仓库并触发对应的归档流水线

- 系统架构图：

![1731168073296](image/README/RN-issue自动归档流程.jpg)

# 部署/维护指南

> [!IMPORTANT]
> 本项目由python编写且使用python工具，请确保你的电脑中安装了python解释器

> [!IMPORTANT]
> 拉取仓库后，请在仓库目录打开终端并执行`pip install -r requirements.txt`，接着执行`pre-commit install`，以完成仓库的初始化

> [!IMPORTANT]
> 如果`pre-commit install`执行失败，请手动执行`pip install pre-commit` ，如果拉取速度太慢，可以使用国内镜像源，例如`pip install -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple pre-commit`


- python脚本全部位于`./issue_processor/`目录下
- Github流水线脚本全部位于`./.github/workflows/`目录下，配置文件则在`./.github/configs/`
- Gitlab流水线脚本全部位于`./gitlab-ci.yml`，配置文件则在`./.gitlab/configs/`
- 脚本配置文件`issue_processor.json`负责存储脚本处理Issue的行为，例如匹配所需的关键字，匹配Issue标签的类型等等。部分配置支持正则表达式

## github侧

### 脚本所需环境

- 需要部署/管理的仓库变量：

    |变量名|变量类型|描述|
    |---|---|---|
    |TOKEN|secret|此token用于获取Issue信息，最少需要对应仓库Permissions的`Issues`的**Read and write**权限|
    |DISPATCH_URL|Variable|触发归档仓库的归档流水线的url，详见  [Github文档：Create a workflow dispatch event](https://docs.github.com/zh/rest/actions/workflows?apiVersion=2022-11-28#create-a-workflow-dispatch-event)|
    |DISPATCH_TOKEN|secret|触发归档仓库的归档流水线所需的token，最少需要归档仓库Permissions的`Contents`的**Read and write**权限|
    |DISPATCH_NAME|Variable|触发归档仓库的归档流水线的流水线触发名称，值需要填写位于归档仓库中的流水线yml文件中["repository_dispatch"]["types"]的定义的字符串|

## gitlab侧

- 需要部署/管理的仓库变量：

    |变量名|变量类型|描述|
    |---|---|---|
    |TOKEN|secret|此token用于获取Issue信息，最少需要对应仓库Access Tokens的**read_api**权限|
    |DISPATCH_URL|Variable|触发归档仓库的归档流水线的url，详见 [Github文档：Create a workflow dispatch event](https://docs.github.com/zh/rest/actions/workflows?apiVersion=2022-11-28#create-a-workflow-dispatch-event)|
    |DISPATCH_TOKEN|secret|触发归档仓库的归档流水线所需的token，最少需要归档仓库Permissions的`Contents`的**Read and write**权限|
    |DISPATCH_NAME|Variable|触发归档仓库的归档流水线的流水线触发名称，值需要填写位于归档仓库中的流水线yml文件中["repository_dispatch"]["types"]的定义的字符串|

- webhook配置
    - 由于gitlab ci 无法直接由Issue事件激活，所以需要配置webhook来激活gitlab ci归档流水线
    - 具体完整配置流程可参考 [Gitlab文档：Trigger pipelines by using the API](https://docs.gitlab.com/ee/ci/triggers/)
    - 简要说明：
        - 在Gitlab仓库的`Settings（设置）`里的`CI/CD`选项里找到`Pipeline trigger tokens（流水线触发令牌）`页面，创建一个“流水线触发器token”，这个token是不会过期的
        - 然后再`Webhooks`中点击`Add new webhook （添加新的webhook）`按钮，创建新的webhook
        - webhook的url请按照如下格式填写：
        `https://{GITLAB_HOST}/api/v4/projects/{PROJECT_ID}/trigger/pipeline?token={TOKEN}&ref={BRANCH_NAME}`
        - `{GITLAB_HOST}` ：替换为gitlab实际域名
        - `{PROJECT_ID}` ： 替换为仓库的ID，可通过gitlab仓库首页复制
        - `{TOKEN}` ： 替换为刚刚获取的`Pipeline trigger tokens（流水线触发令牌）`）
        - `{BRANCH_NAME}` ： 替换为 `main` 即可，如果流水线文件放在其他分支了或者有其他需求，可以替换为仓库的其他分支名称或者仓库git标签名称

### 开发测试环境

- 为了方便本地测试，项目引入了`python-dotenv`模块，它提供了读取本地`.env`文件内容作为环境变量的能力

- 环境需求：
    - Python : 3.10 或以上
    - IDE : visual studio code
    - `pip install ./develop-requirements.txt`
    - 一个符合脚本运行所需的`.env`文件内容，请参考`example.env`编写`.env`，并将`.env`文件放入`./issue_processor/`目录下

- 项目包含了`launch.json`文件，用于本地调试，VSCode调试页面可以选择调试的项目，选择对应平台的流程后按下`F5`即可启动调试


# 相关文档：

- 流水线dispatch（Restful API触发流水线）
    - Github ： https://docs.github.com/zh/rest/using-the-rest-api/getting-started-with-the-rest-api?apiVersion=2022-11-28#example-request-using-query-parameters
    - Gitlab ： https://docs.gitlab.com/ee/ci/triggers/#use-a-webhook










