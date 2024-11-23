# 创建输出目录，如果已经存在则不报错
New-Item -ItemType Directory -Force -Path "./output"

# 复制文件和目录
Copy-Item -Recurse -Force -Verbose "./config" -Destination "./output/config"
Copy-Item -Recurse -Force -Verbose "./.github" -Destination "./output/.github"
Copy-Item -Recurse -Force -Verbose "./.gitlab" -Destination "./output/.gitlab"
Copy-Item -Force -Verbose "./.gitlab-ci.yml" -Destination "./output/.gitlab-ci.yml"
Copy-Item -Recurse -Force -Verbose "./rn_issue_auto_archiving" -Destination "./output/rn_issue_auto_archiving"

# 输出完成信息
Write-Output "output done"