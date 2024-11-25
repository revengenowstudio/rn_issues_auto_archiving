
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
            } else {
                Write-Host "Error: Missing value for $parameterName"
                exit 1
            }
        }
    }

    # 检查参数值是否为空
    if (-not $parameterValue) {
        Write-Host "Error: Parameter $parameterName not found or invalid."
        exit 1
    }else {
        Write-Host "Get Parameter '$parameterName' , value : $parameterValue"
    }    
    # 返回参数值
    return $parameterValue
}

# 创建输出目录，如果已经存在则不报错
Remove-Item -Recurse -Force -Path "./output/*"
New-Item -ItemType Directory -Force -Path "./output"

# 复制文件和目录
Copy-Item -Recurse -Force -Verbose "./config" -Destination "./output/config"
Copy-Item -Recurse -Force -Verbose "./.github" -Destination "./output/.github"
Copy-Item -Recurse -Force -Verbose "./.gitlab" -Destination "./output/.gitlab"
Copy-Item -Force -Verbose "./.gitlab-ci.yml" -Destination "./output/.gitlab-ci.yml"
Copy-Item -Recurse -Force -Verbose "./rn_issues_auto_archiving" -Destination "./output/rn_issues_auto_archiving"

Remove-Item -Recurse -Force -Path "./output/rn_issues_auto_archiving/__pycache__"
Remove-Item -Recurse -Force -Path "./output/rn_issues_auto_archiving/auto_archiving/__pycache__"
Remove-Item -Recurse -Force -Path "./output/rn_issues_auto_archiving/issue_processor/__pycache__"
Remove-Item -Recurse -Force -Path "./output/rn_issues_auto_archiving/shared/__pycache__"
Remove-Item -Recurse -Force -Path "./output/rn_issues_auto_archiving/utils/__pycache__"
Remove-Item -Recurse -Force -Path "./output/.gitlab/workflows/DeployAutoArchiving.yml"
Remove-Item -Recurse -Force -Path "./output/.github/workflows/DeployAutoArchiving.yml"

# 调用函数处理第一个文件
Update-BranchInFile -fileName "./output/.github/workflows/AutoArchiving.yml"

# 调用函数处理第二个文件
Update-BranchInFile -fileName "./output/.gitlab/workflows/AutoArchiving.yml"

Add-IncludeInGitlabCi -fileName "./output/.gitlab-ci.yml"

# 主程序入口
$RN_ALL_ISSUES_REPO_PATH = Get-CommandLineParameter -parameterName "--RN_ALL_ISSUES_REPO_PATH" -cmdArgs $args
Write-Host "$RN_ALL_ISSUES_REPO_PATH"

$RN_INTERNAL_ISSUES_REPO_PATH = Get-CommandLineParameter -parameterName "--RN_INTERNAL_ISSUES_REPO_PATH" -cmdArgs $args
Write-Host "$RN_INTERNAL_ISSUES_REPO_PATH"

Copy-Item -Recurse -Force -Verbose "./output/config" -Destination "$RN_ALL_ISSUES_REPO_PATH"
Copy-Item -Recurse -Force -Verbose "./output/.github" -Destination "$RN_ALL_ISSUES_REPO_PATH/"
Copy-Item -Recurse -Force -Verbose "./output/rn_issues_auto_archiving" -Destination "$RN_ALL_ISSUES_REPO_PATH/"

Copy-Item -Recurse -Force -Verbose "./output/config" -Destination "$RN_INTERNAL_ISSUES_REPO_PATH"
Copy-Item -Recurse -Force -Verbose "./output/.gitlab" -Destination "$RN_INTERNAL_ISSUES_REPO_PATH/"
Copy-Item -Force -Verbose "./output/.gitlab-ci.yml" -Destination "$RN_INTERNAL_ISSUES_REPO_PATH/.gitlab-ci.yml"
Copy-Item -Recurse -Force -Verbose "./output/rn_issues_auto_archiving" -Destination "$RN_INTERNAL_ISSUES_REPO_PATH/"

# 输出完成信息
Write-Host "output done"