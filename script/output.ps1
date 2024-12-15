
# 定义一个函数来处理文件
function Update-BranchInFile {
    param (
        [string]$fileName
    )

    # 使用 UTF-8 编码读取输入文件内容
    $content = [System.IO.File]::ReadAllText($fileName, [System.Text.Encoding]::UTF8)

    # 使用正则表达式匹配并替换 "TARGET_BRANCH: main" 为 "TARGET_BRANCH: master"
    $updatedContent = $content -replace 'TARGET_BRANCH:\s*main', 'TARGET_BRANCH: master'

    # 将更新后的内容写回原文件，使用 UTF-8 编码
    [System.IO.File]::WriteAllText($fileName, $updatedContent, [System.Text.Encoding]::UTF8)

    # 输出完成信息
    Write-Host "File updated: $fileName"
}
function Remove-UnittestInFile {
    param (
        [string]$fileName
    )

    # 使用 UTF-8 编码读取输入文件内容
    $content = [System.IO.File]::ReadAllText($fileName, [System.Text.Encoding]::UTF8)
    # 删除 "unittest" 阶段
    $fileContent = $content -replace "(?m)^\s*- unittest\s*$", ""

    # 删除 "- local: \"/.gitlab/workflows/Unittest.yml\"" 行
    $fileContent = $fileContent -replace "(?m)^\s*- local: `"/.gitlab/workflows/Unittest.yml`"\s*$", ""

    # 将更新后的内容写回原文件，使用 UTF-8 编码
    [System.IO.File]::WriteAllText($fileName, $fileContent, [System.Text.Encoding]::UTF8)

    # 输出完成信息
    Write-Host "File updated: $fileName"
}

function Add-IncludeInGitlabCi {
    param (
        [string]$fileName
    )

    # 使用 UTF-8 编码读取输入文件内容
    $content = [System.IO.File]::ReadAllText($fileName, [System.Text.Encoding]::UTF8)

    # 使用正则表达式匹配并替换 "TARGET_BRANCH: main" 为 "TARGET_BRANCH: master"
    $updatedContent = $content -replace "(include:)", "`$1`n  - local: `"/.gitlab/workflows/DeployAutoArchiving.yml`""

    # 将更新后的内容写回原文件，使用 UTF-8 编码
    [System.IO.File]::WriteAllText($fileName, $updatedContent, [System.Text.Encoding]::UTF8)

    # 输出完成信息
    Write-Host "File updated: $fileName"
}

# 定义一个函数来检查并返回指定参数的值
function Get-CommandLineParameter {
    param (
        [array]$cmdArgs,
        [string]$parameterName
    )

    # 初始化参数值
    $parameterValue = $null

    # 遍历命令行参数
    for ($i = 0; $i -lt $cmdArgs.Length; $i++) {
        if ($cmdArgs[$i] -eq $parameterName) {
            if ($i + 1 -lt $cmdArgs.Length) {
                $parameterValue = $cmdArgs[$i + 1]
                break
            }
            else {
                Write-Host "Error: Missing value for $parameterName"
                exit 1
            }
        }
    }

    # 检查参数值是否为空
    if (-not $parameterValue) {
        Write-Host "Error: Parameter $parameterName not found or invalid."
        exit 1
    }
    else {
        Write-Host "Get Parameter '$parameterName' , value : $parameterValue"
    }    
    # 返回参数值
    return $parameterValue
}

# 创建输出目录，如果已经存在则不报错
Write-Host "clear output dir"
Remove-Item -Recurse -Force -Path "./output/*"
New-Item -ItemType Directory -Force -Path "./output"

# 复制文件和目录
Write-Host "copy file to output dir"
Copy-Item -Recurse -Force "./config" -Destination "./output/config"
Copy-Item -Recurse -Force "./.github" -Destination "./output/.github"
Copy-Item -Recurse -Force "./.gitlab" -Destination "./output/.gitlab"
Copy-Item -Force "./.gitlab-ci.yml" -Destination "./output/.gitlab-ci.yml"
Copy-Item -Recurse -Force "./rn_issues_auto_archiving" -Destination "./output/rn_issues_auto_archiving"

Write-Host "copy markdown and images to output dir"
Copy-Item -Force "./手动运行归档流水线指南.md" -Destination "./output/"
Copy-Item -Force "./自动归档流水线使用指南.md" -Destination "./output/"
Copy-Item -Recurse -Force "./image" -Destination "./output/"
Remove-Item -Recurse -Force -Path "./output/image/README"


Write-Host "remove unnecessary files"
Remove-Item -Recurse -Force -Path "./output/rn_issues_auto_archiving/__pycache__"
Remove-Item -Recurse -Force -Path "./output/rn_issues_auto_archiving/auto_archiving/__pycache__"
Remove-Item -Recurse -Force -Path "./output/rn_issues_auto_archiving/issue_processor/__pycache__"
Remove-Item -Recurse -Force -Path "./output/rn_issues_auto_archiving/shared/__pycache__"
Remove-Item -Recurse -Force -Path "./output/rn_issues_auto_archiving/utils/__pycache__"
Remove-Item -Recurse -Force -Path "./output/.gitlab/workflows/DeployAutoArchiving.yml"
Remove-Item -Recurse -Force -Path "./output/.github/workflows/DeployAutoArchiving.yml"
Remove-Item -Recurse -Force -Path "./output/.github/workflows/Unittest.yml"
Remove-Item -Recurse -Force -Path "./output/.gitlab/workflows/Unittest.yml"
Remove-Item -Recurse -Force -Path "./output/rn_issues_auto_archiving/tests"
Remove-Item -Recurse -Force -Path "./output/rn_issues_auto_archiving/test.py"

# 调用函数处理第一个文件
Update-BranchInFile -fileName "./output/.github/workflows/AutoArchiving.yml"

# 调用函数处理第二个文件
Update-BranchInFile -fileName "./output/.gitlab/workflows/AutoArchiving.yml"

Remove-UnittestInFile -fileName "./output/.gitlab-ci.yml"

# Add-IncludeInGitlabCi -fileName "./output/.gitlab-ci.yml"

# 主程序入口
$RN_ALL_ISSUES_REPO_PATH = Get-CommandLineParameter -parameterName "--RN_ALL_ISSUES_REPO_PATH" -cmdArgs $args

$RN_INTERNAL_ISSUES_REPO_PATH = Get-CommandLineParameter -parameterName "--RN_INTERNAL_ISSUES_REPO_PATH" -cmdArgs $args

Write-Host "copy output file to `"$RN_ALL_ISSUES_REPO_PATH`""
Remove-Item -Recurse -Force "$RN_ALL_ISSUES_REPO_PATH/config"
Remove-Item -Recurse -Force "$RN_ALL_ISSUES_REPO_PATH/rn_issues_auto_archiving"
Remove-Item -Recurse -Force "$RN_ALL_ISSUES_REPO_PATH/image"

Copy-Item -Recurse -Force "./output/config" -Destination "$RN_ALL_ISSUES_REPO_PATH"
Copy-Item -Recurse -Force "./output/.github" -Destination "$RN_ALL_ISSUES_REPO_PATH/"
Copy-Item -Recurse -Force "./output/rn_issues_auto_archiving" -Destination "$RN_ALL_ISSUES_REPO_PATH/"
Copy-Item -Force "./output/手动运行归档流水线指南.md" -Destination "$RN_ALL_ISSUES_REPO_PATH/手动运行归档流水线指南.md"
Copy-Item -Force "./output/自动归档流水线使用指南.md" -Destination "$RN_ALL_ISSUES_REPO_PATH/自动归档流水线使用指南.md"
Copy-Item -Recurse -Force "./output/image" -Destination "$RN_ALL_ISSUES_REPO_PATH/"

Write-Host "copy output file to `"$RN_INTERNAL_ISSUES_REPO_PATH`""
Remove-Item -Recurse -Force "$RN_INTERNAL_ISSUES_REPO_PATH/config"
Remove-Item -Force "$RN_INTERNAL_ISSUES_REPO_PATH/.gitlab-ci.yml"
Remove-Item -Recurse -Force "$RN_INTERNAL_ISSUES_REPO_PATH/rn_issues_auto_archiving"
Remove-Item -Recurse -Force "$RN_INTERNAL_ISSUES_REPO_PATH/image"

Copy-Item -Recurse -Force "./output/config" -Destination "$RN_INTERNAL_ISSUES_REPO_PATH"
Copy-Item -Recurse -Force "./output/.gitlab" -Destination "$RN_INTERNAL_ISSUES_REPO_PATH/"
Copy-Item -Force "./output/.gitlab-ci.yml" -Destination "$RN_INTERNAL_ISSUES_REPO_PATH/.gitlab-ci.yml"
Copy-Item -Recurse -Force "./output/rn_issues_auto_archiving" -Destination "$RN_INTERNAL_ISSUES_REPO_PATH/"
Copy-Item -Force "./output/手动运行归档流水线指南.md" -Destination "$RN_INTERNAL_ISSUES_REPO_PATH/手动运行归档流水线指南.md"
Copy-Item -Force "./output/自动归档流水线使用指南.md" -Destination "$RN_INTERNAL_ISSUES_REPO_PATH/自动归档流水线使用指南.md"
Copy-Item -Recurse -Force "./output/image" -Destination "$RN_INTERNAL_ISSUES_REPO_PATH/"

# 输出完成信息
Write-Host "output done"