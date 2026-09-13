# Config配置项

- 配置定义在 `rn_issues_auto_archiving/app_config/config.py`，文件底部的单例 `config` 由各脚本直接引用（`from app_config import config`）。
- 旧的 `config/auto_archiving.json` 已移除，改配置直接改 `config.py`。
- 下表变量名即 `config.py` 中 `Config` dataclass 的字段路径。
- 原先以 `{version_regex}` 占位符引用的项，现在由 f-string 在定义时展开，修改 `version_regex` 后引用它的正则会自动同步。
- `archive_version_reges_for_comments` 与 `skip_archived_reges_for_comments` 的元素是 `MatchRules`：`rules` 是参与匹配的正则/关键字，`hint` 是展示给人看的提示（报错评论里多个 `hint` 逐行显示），`hint` 为空字符串时不显示。
- 脚本发送的所有评论都会带上 `post_comment_prefix` 前缀；同时脚本会跳过以此前缀开头的评论，避免自己发出的提示被当成归档依据。

    | 变量名 | 变量类型 | 正则表达式支持 | 描述 |
    | --- | --- | --- | --- |
    | config.version_regex | str | 是 | 匹配版本号的正则表达式，最外层必须有一对小括号`()`，因为这个值会被其他值引用 |
    | config.introduced_version_reges | list[str] | 是 | 匹配Issue描述中引入版本号的正则表达式，填写多个正则表达式流水线会用每个正则都匹配一次，直到匹配成功 |
    | config.issue_type.type_keyword | dict[str,str] | 否 | 匹配Issue标题中Issue类型关键字的字典，用来转换成归档内容中的Issue类型文本，由于不再通过Issue标题判断Issue类型，此项可以无视 |
    | config.issue_type.need_introduced_version_issue_type | list[str] | 否 | 归档时需要`引入版本号`的Issue类型，填写的内容为归档文档中定义的Issue类型，可填多个，匹配到任意一个即要求Issue描述中带有`引入版本号`，若Issue属于列表中的Issue类型但Issue描述中没有找到`引入版本号`，则归档流水线会报错并reopen此Issue |
    | config.issue_type.label_map | dict[str,str] | 否 | Issue标签（labels）映射为归档文档中定义的Issue类型，流水线通过这个字典来判断Issue是什么类型的，key为Issue标签名称，value为归档文档中定义的Issue类型名称 |
    | config.archive_necessary_labels | list[str] | 否 | 归档所必须的Issue标签，流水线会检查issue是否包含这些标签，若不包含则报错并reopen此Issue。若填写多个Issue标签，则Issue必须同时具有这些标签才可以被流水线归档 |
    | config.archive_version_reges_for_comments[].rules | str | 是 | 从Issue评论中匹配`归档版本号`的正则表达式，可组合引用`{version_regex}`。若流水线用任意一条规则均无法在Issue评论中匹配成功，则报错并reopen此Issue |
    | config.archive_version_reges_for_comments[].hint | str | 否 | 归档失败时展示给Issue作者的帮助提示，例如`0.99.918 测试通过`。多个`hint`会逐行显示在报错评论里，建议写成可以直接照抄的格式 |
    | config.archive_version_ignore_line_reges_for_comments | list[str] | 是 | 在评论中匹配`归档版本号`之前，先忽略掉匹配这些正则的行（例如引用块`^> `），避免被引用的内容被误判为归档版本号 |
    | config.skip_archived_reges_for_comments[].rules | str | 是 | Issue评论中匹配到这些规则时，流水线跳过归档流程，用于人工标记不需要归档的Issue |
    | config.skip_archived_reges_for_comments[].hint | str | 否 | 归档失败的报错评论末尾会拼上“如果需要跳过归档流程, 请发送带有如下关键字的评论并再次关闭issue即可”，这里列出的就是这些关键字 |
    | config.post_comment_prefix | str | 否 | 本脚本发送评论时统一加的前缀（前缀与内容之间有一个空格）。脚本会跳过以此前缀开头的评论，避免自己发出的提示被当成归档依据；留空则不加前缀、也不会跳过任何评论 |
    | config.archived_document.rjust_space_width | int | 否 | 归档内容中的描述部分的目标字符的长度，若归档内容描述的字符长度不够会用空格填充，具体位置请见`archive_template`的定义 |
    | config.archived_document.rjust_character | str | 否 | `rjust_space_width`填充的字符，空格即可 |
    | config.archived_document.table_separator | str | 否 | 用来区分归档列表每一项的分隔符，由于归档文档是markdown列表格式，所以`\|`即可 |
    | config.archived_document.archive_template | str | 否 | 归档内容的标准模版，定义了流水线归档内容的格式，可用的预定义变量有`{table_id}` `{issue_type}` `{issue_title}` `{rjust_space}` `{issue_repository}` `{issue_id}` `{introduced_version}` `{archive_version}` `{issue_url}` `{issue_url_parents}` |
    | config.archived_document.fill_issue_url_by_repository_type | list[str] | 否 | 根据Issue所属的`repository_type`内容（例如“外部Issue”等），判断`archive_template`中的`{issue_url}` `{issue_url_parents}`值是否需要被填充。如果Issue的`repository_type`的值不在此列表，则不填充url相关占位符 |
    | config.archived_document.issue_title_processing_rules | dict[str,dict[str,str\|list]] | 否 | Issue标题预处理规则，用来对特定类型的Issue标题进行文本的添加或者修改，第一层key为Issue类型，第二层key是固定的，必须要填写`add_prefix` `add_suffix` `remove_keyword`，`add_prefix`是在Issue标题前添加的字符串，`add_suffix`是在Issue标题后添加的字符串，`remove_keyword`是Issue标题中若存在匹配的关键字则删除这些关键字 |
