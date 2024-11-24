#!/bin/bash

# 创建输出目录，如果已经存在则不报错
rm -rf ./output/*
mkdir -p ./output

# 复制文件和目录
cp -r ./config ./output/
cp -r ./.github ./output/
cp -r ./.gitlab ./output/
cp ./.gitlab-ci.yml ./output/
cp -r ./rn_issue_auto_archiving ./output/

# 删除特定目录
rm -rf ./output/rn_issue_auto_archiving/__pycache__
rm -rf ./output/rn_issue_auto_archiving/auto_archiving/__pycache__
rm -rf ./output/rn_issue_auto_archiving/issue_processor/__pycache__
rm -rf ./output/rn_issue_auto_archiving/shared/__pycache__
rm -rf ./output/rn_issue_auto_archiving/utils/__pycache__
rm -rf ./output/.gitlab/workflows/DeployAutoArchiving.yml
rm -rf ./output/.github/workflows/DeployAutoArchiving.yml

# 定义一个函数来处理文件
update_branch_in_file() {
    local file_name="$1"
    local content=$(<"$file_name")
    local updated_content=$(echo "$content" | sed 's/TARGET_BRANCH:[[:space:]]*main/TARGET_BRANCH: master/g')
    echo "$updated_content" > "$file_name"
    echo "File updated: $file_name"
}

# 定义一个函数来检查并返回指定参数的值
get_command_line_parameter() {
    local args=("$@")
    local parameter_name="$2"
    local parameter_value=""

    for (( i=0; i<${#args[@]}; i++ )); do
        if [[ "${args[i]}" == "$parameter_name" ]]; then
            if (( i+1 < ${#args[@]} )); then
                parameter_value="${args[i+1]}"
                break
            else
                echo "Error: Missing value for $parameter_name"
                exit 1
            fi
        fi
    done

    if [[ -z "$parameter_value" ]]; then
        echo "Error: Parameter $parameter_name not found or invalid."
        exit 1
    fi

    echo $parameter_value
}

# 调用函数处理第一个文件
update_branch_in_file "./output/.github/workflows/AutoArchiving.yml"

# 调用函数处理第二个文件
update_branch_in_file "./output/.gitlab/workflows/AutoArchiving.yml"

RN_ALL_ISSUES_REPO_PATH=$(get_command_line_parameter "$@" "--RN_ALL_ISSUES_REPO_PATH")
echo "$RN_ALL_ISSUES_REPO_PATH"

RN_INTERNAL_ISSUES_REPO_PATH=$(get_command_line_parameter "$@" "--RN_INTERNAL_ISSUES_REPO_PATH")
echo "$RN_INTERNAL_ISSUES_REPO_PATH"

# 复制文件和目录到目标路径
cp -r ./output/config "$RN_ALL_ISSUES_REPO_PATH"
cp -r ./output/.github "$RN_ALL_ISSUES_REPO_PATH/"
cp -r ./output/rn_issue_auto_archiving "$RN_ALL_ISSUES_REPO_PATH/"

cp -r ./output/config "$RN_INTERNAL_ISSUES_REPO_PATH"
cp -r ./output/.gitlab "$RN_INTERNAL_ISSUES_REPO_PATH/"
cp ./output/.gitlab-ci.yml "$RN_INTERNAL_ISSUES_REPO_PATH/.gitlab-ci.yml"
cp -r ./output/rn_issue_auto_archiving "$RN_INTERNAL_ISSUES_REPO_PATH/"

# 输出完成信息
echo "output done"