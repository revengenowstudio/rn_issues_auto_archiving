# #!/bin/bash

# set -e
# function msg { out "$*" >&2; }
# function err {
#     local x=$?
#     msg "$*"
#     return $(($x == 0 ? 1 : $x))
# }
# function out { printf '%s\n' "$*"; }

# function globals {
#     this="./output"
#     RN_ALL_ISSUES_REPO_PATH=""
#     RN_INTERNAL_ISSUES_REPO_PATH=""
#     outputPath=""
# }
# globals

# function parseCmds {
#     while [[ $# -gt 0 ]]; do
#         case "$1" in # Munging globals, beware
#         --RN_ALL_ISSUES_REPO_PATH)
#             RN_ALL_ISSUES_REPO_PATH="$2"
#             shift 2
#             ;;
#         --RN_INTERNAL_ISSUES_REPO_PATH)
#             RN_INTERNAL_ISSUES_REPO_PATH="$2"
#             shift 2
#             ;;
#         -o)
#             outputPath="$2"
#             shift 2
#             ;;
#         *) err 'Argument error. Please see help.' ;;
#         esac
#     done
#     : "${outputPath:=$this}"
# }

# function pickFiles {
#     # 创建输出目录，如果已经存在则不报错
#     echo "pick files from repository to '$outputPath'"
#     rm -rf "$outputPath/*"
#     mkdir -p "$outputPath"

#     # 复制文件和目录
#     cp -rf "./config" "$outputPath/"
#     cp -rf "./.github" "$outputPath/"
#     cp -rf "./.gitlab" "$outputPath/"
#     cp "./.gitlab-ci.yml" "$outputPath/"
#     cp -rf "./rn_issues_auto_archiving" "$outputPath/"

#     # 删除特定目录
#     rm -rf "$outputPath/rn_issues_auto_archiving/__pycache__"
#     rm -rf "$outputPath/rn_issues_auto_archiving/auto_archiving/__pycache__"
#     rm -rf "$outputPath/rn_issues_auto_archiving/issue_processor/__pycache__"
#     rm -rf "$outputPath/rn_issues_auto_archiving/shared/__pycache__"
#     rm -rf "$outputPath/rn_issues_auto_archiving/utils/__pycache__"
#     rm -rf "$outputPath/.gitlab/workflows/DeployAutoArchiving.yml"
#     rm -rf "$outputPath/.github/workflows/DeployAutoArchiving.yml"
# }

# # 定义一个函数来处理文件
# function updateBranchInFile {
#     local file_name="$1"
#     sed -i 's/TARGET_BRANCH:[[:space:]]*main/TARGET_BRANCH: master/g' "$file_name"
#     echo "File updated : '$file_name' , TARGET_BRANCH value update to 'master'"
# }

# function updateBranchInGitlabCiFile {
#     local file_name="$1"
#     sed -i '/^include:/a \  - local: "/.gitlab/workflows/DeployAutoArchiving.yml"' "$file_name"
#     echo "Added include: local: \"./.gitlab/workflows/DeployAutoArchiving.yml\" to \"$file_name\""
# }

# function copyOutputFilesToAllIssueRepo {
#     # 复制文件和目录到目标路径
#     cp -rf "$outputPath/config" "$RN_ALL_ISSUES_REPO_PATH"
#     cp -rf "$outputPath/.github" "$RN_ALL_ISSUES_REPO_PATH/"
#     cp -rf "$outputPath/rn_issues_auto_archiving" "$RN_ALL_ISSUES_REPO_PATH/"
# }

# function copyOutputFilesToInternalIssueRepo {
#     cp -rf "$outputPath/config" "$RN_INTERNAL_ISSUES_REPO_PATH"
#     cp -rf "$outputPath/.gitlab" "$RN_INTERNAL_ISSUES_REPO_PATH/"
#     cp -rf "$outputPath/.gitlab-ci.yml" "$RN_INTERNAL_ISSUES_REPO_PATH/.gitlab-ci.yml"
#     cp -rf "$outputPath/rn_issues_auto_archiving" "$RN_INTERNAL_ISSUES_REPO_PATH/"
# }

# parseCmds "$@"
# pickFiles
# updateBranchInFile "$outputPath/.github/workflows/AutoArchiving.yml"
# updateBranchInFile "$outputPath/.gitlab/workflows/AutoArchiving.yml"
# updateBranchInGitlabCiFile "$outputPath/.gitlab-ci.yml"

# if [[ -n "$RN_ALL_ISSUES_REPO_PATH" ]]; then
#     echo "get RN_ALL_ISSUES_REPO_PATH '$RN_ALL_ISSUES_REPO_PATH' , copy output files to '$RN_ALL_ISSUES_REPO_PATH'"
#     copyOutputFilesToAllIssueRepo
# else
#     echo "--RN_ALL_ISSUES_REPO_PATH is empty"
# fi

# if [[ -n "$RN_INTERNAL_ISSUES_REPO_PATH" ]]; then
# echo "get RN_INTERNAL_ISSUES_REPO_PATH '$RN_INTERNAL_ISSUES_REPO_PATH' , copy output files to '$RN_INTERNAL_ISSUES_REPO_PATH'"
#     copyOutputFilesToInternalIssueRepo
# else
#     echo "--RN_INTERNAL_ISSUES_REPO_PATH is empty"
# fi

# # 输出完成信息
# echo "output done"
