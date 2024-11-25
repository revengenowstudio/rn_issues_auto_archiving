#!/usr/bin/env nu

# 此脚本用来快速将本仓库的流水线yml文件和流水线所需脚本输出成部署到issue仓库的目录结构
# 如果填写RN_ALL_ISSUES_REPO_PATH和RN_INTERNAL_ISSUES_REPO_PATH，则会直接将输出的内容复制到对应的路径中
# 不填 RN_ALL_ISSUES_REPO_PATH和RN_INTERNAL_ISSUES_REPO_PATH 参数只会将部署所需文件提取到到输出目录 ./output/ 中

def update_branch_in_file [file_name:string] {
    open -r $file_name | str replace 'TARGET_BRANCH: main' 'TARGET_BRANCH: master' | save -f $file_name
    print $"File updated : ($file_name) , change 'TARGET_BRANCH' value 'main' to 'master'"
}

def main [
    --RN_ALL_ISSUES_REPO_PATH : string  # 选填，外部issue仓库的绝对或者相对路径
    --RN_INTERNAL_ISSUES_REPO_PATH : string  # 选填，内部issue仓库的绝对或者相对路径
] {
    # 创建输出目录，如果已经存在则不报错
    print "clear output dir"
    rm -r ./output/*
    print "create output dir"
    mkdir ./output

    # 复制文件和目录
    print "pick files from the repository for output"
    cp -r ./config ./output/
    cp -r ./.github ./output/
    cp -r ./.gitlab ./output/
    cp ./.gitlab-ci.yml ./output/
    cp -r ./rn_issues_auto_archiving ./output/

    # 删除特定目录
    print "delete unnessesary output files"
    rm -rfv ./output/rn_issues_auto_archiving/__pycache__
    rm -rfv ./output/rn_issues_auto_archiving/auto_archiving/__pycache__
    rm -rfv ./output/rn_issues_auto_archiving/issue_processor/__pycache__
    rm -rfv ./output/rn_issues_auto_archiving/shared/__pycache__
    rm -rfv ./output/rn_issues_auto_archiving/utils/__pycache__
    rm -rfv ./output/.gitlab/workflows/DeployAutoArchiving.yml
    rm -rfv ./output/.github/workflows/DeployAutoArchiving.yml
    # 调用函数处理第一个文件
    update_branch_in_file "./output/.github/workflows/AutoArchiving.yml"

    # 调用函数处理第二个文件
    update_branch_in_file "./output/.gitlab/workflows/AutoArchiving.yml"

    if ($RN_ALL_ISSUES_REPO_PATH | is-empty) {
        print "RN_ALL_ISSUES_REPO_PATH is empty , exit"
        exit 1
    }
    print $"get RN_ALL_ISSUES_REPO_PATH: ($RN_ALL_ISSUES_REPO_PATH)"
    print $"copy output files to ($RN_ALL_ISSUES_REPO_PATH)"
    cp -r ./output/config $"($RN_ALL_ISSUES_REPO_PATH)"
    cp -r ./output/.github $"($RN_ALL_ISSUES_REPO_PATH)/"
    cp -r ./output/rn_issues_auto_archiving $"($RN_ALL_ISSUES_REPO_PATH)/"
    
    if ($RN_INTERNAL_ISSUES_REPO_PATH | is-empty) {
        print "RN_INTERNAL_ISSUES_REPO_PATH is empty , exit"
        exit 1
    }
    print $"get RN_INTERNAL_ISSUES_REPO_PATH: ($RN_INTERNAL_ISSUES_REPO_PATH)"
    print $"copy output files to ($RN_INTERNAL_ISSUES_REPO_PATH)"
    cp -r ./output/config $"($RN_INTERNAL_ISSUES_REPO_PATH)"
    cp -r ./output/.gitlab $"($RN_INTERNAL_ISSUES_REPO_PATH)/"
    cp ./output/.gitlab-ci.yml $"($RN_INTERNAL_ISSUES_REPO_PATH)/.gitlab-ci.yml"
    cp -r ./output/rn_issues_auto_archiving $"($RN_INTERNAL_ISSUES_REPO_PATH)/"

    # 输出完成信息
    print "job done"
}