git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git add ./修改归档.md
diff=$(git diff --cached)
if [[ -z $diff ]]; then
    echo "归档文档没有发生变化，跳过提交流程"
else
    echo "归档文档没有发生变化，提交新内容"
    git commit -m "$COMMIT_TITLE$ISSUE_NUMBER"
    git push origin main
fi